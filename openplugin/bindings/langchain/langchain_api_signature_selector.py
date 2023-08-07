import re
import time
from typing import List, Optional
from langchain.tools import AIPluginTool
from urllib.parse import urlparse, parse_qs
from langchain.callbacks import get_openai_callback
from langchain.tools.plugin import AIPlugin, ApiConfig
from .langchain_helpers import get_agent_type, get_llm
from langchain.agents import load_tools, initialize_agent
from openplugin import Config, ToolSelectorConfig, PluginDetected, Plugin, \
    ApiSignatureSelector, Message, SelectedApiSignatureResponse, LLM


class LangchainApiSignatureSelector(ApiSignatureSelector):
    def __init__(
            self,
            tool_selector_config: ToolSelectorConfig,
            plugin: Plugin,
            config: Optional[Config],
            llm: Optional[LLM]):
        super().__init__(tool_selector_config, plugin, config, llm)
        self.initialize()

    def initialize(self):
        agent_type = get_agent_type(self.tool_selector_config.pipeline_name)
        tools = load_tools(["requests_all"])
        if self.plugin.manifest_url:
            api_config = ApiConfig(
                type="openapi",
                url=self.plugin.openapi_doc_url
            )
            ai_plugin = AIPlugin(
                schema_version=self.plugin.schema_version,
                name_for_model=self.plugin.name,
                name_for_human=self.plugin.name,
                description_for_model=self.plugin.description,
                description_for_human=self.plugin.description,
                auth={
                    "type": "none"
                },
                api=api_config,
                logo_url=self.plugin.logo_url,
                contact_email=self.plugin.contact_email,
                legal_info_url=self.plugin.legal_info_url,
            )
            api_spec = (
                f"Usage Guide: {self.plugin.description}\n\n"
                f"OpenAPI Spec: {self.plugin.get_openapi_doc_json()}"
            )
            ai_plugin_tool = AIPluginTool(
                name=self.plugin.name,
                description=self.plugin.description,
                plugin=ai_plugin,
                api_spec=api_spec
            )
            tools.append(ai_plugin_tool)

        llm = get_llm(self.llm, self.config.openai_api_key)
        self.agent = initialize_agent(
            tools=tools,
            llm=llm,
            agent=agent_type,
            verbose=False,
            return_intermediate_steps=True
        )

    def run(self, messages: List[Message]) -> SelectedApiSignatureResponse:
        pre_prompts = ""
        pre_prompts += self.plugin.get_plugin_pre_prompts()

        with get_openai_callback() as cb:
            start_test_case_time = time.time()
            message = messages[-1]
            detected_plugin_operations = []
            response_prompt = None
            try:
                prompt = f"{pre_prompts}\n{message.content}"
                response = self.agent(prompt)
                response_prompt = response['output']
                for step in response["intermediate_steps"]:
                    detected_plugin = self.plugin.name
                    if detected_plugin:
                        plugin_operation = PluginDetected(plugin=detected_plugin)
                        detected_plugin_operations.append(plugin_operation)

                for step in response["intermediate_steps"]:
                    if step[0].tool_input:
                        url = step[0].tool_input
                        if url.startswith("'"):
                            url = url[1:-1]
                        if url.endswith("'"):
                            url = url[:-1]
                        if url.lower() != "none":
                            api = url.split('?')[0].strip()
                            parsed_url = urlparse(url)
                            query_dict = parse_qs(parsed_url.query)
                            extracted_params = {
                                k: v[0] if type(v) == list and len(v) == 1 else v for
                                k, v in
                                query_dict.items()}
                            for detected_plugin_operation in detected_plugin_operations:
                                if detected_plugin_operation.plugin.has_api_endpoint(
                                        api):
                                    detected_plugin_operation.api_called = api
                                    detected_plugin_operation.mapped_operation_parameters = extracted_params
            except Exception as e:
                # TODO: handle this better, use callback
                response = str(e)
                for line in response.splitlines():
                    if line.strip().startswith(
                            "Action") and not line.strip().startswith("Action Input"):
                        plugin = line.split(":")[1].strip()
                        detected_plugin = self.plugin.name
                        if detected_plugin:
                            plugin_operation = PluginDetected(plugin=detected_plugin)
                            detected_plugin_operations.append(plugin_operation)
                matches = re.findall(r'"([^"]*)"', response)
                for url in matches:
                    if url.startswith("http"):
                        parsed_url = urlparse(url)
                        query_dict = parse_qs(parsed_url.query)
                        extracted_params = {
                            k: v[0] if type(v) == list and len(v) == 1 else v for
                            k, v in
                            query_dict.items()}
                        for detected_plugin_operation in detected_plugin_operations:
                            if detected_plugin_operation.plugin.has_api_endpoint(
                                    api):
                                detected_plugin_operation.api_called = api
                                detected_plugin_operation.mapped_operation_parameters = extracted_params
            response_obj = SelectedApiSignatureResponse(
                run_completed=True,
                final_text_response=response_prompt,
                detected_plugin_operations=detected_plugin_operations,
                response_time=round(time.time() - start_test_case_time, 2),
                tokens_used=cb.total_tokens,
                llm_api_cost=round(cb.total_cost, 4)
            )
            return response_obj
