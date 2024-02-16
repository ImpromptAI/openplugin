# TODO: OUTDATED, needs to be updated to use the new plugin system
"""
import re
import time
from typing import List, Optional

from langchain.agents import initialize_agent, load_tools
from langchain.callbacks import get_openai_callback
from langchain.tools import AIPluginTool
from langchain.tools.plugin import AIPlugin, ApiConfig

from openplugin.bindings.langchain.langchain_helpers import get_agent_type, get_llm
from openplugin.plugins.models import (
    LLM,
    Config,
    Message,
    PluginDetected,
    SelectedPluginsResponse,
    ToolSelectorConfig,
)
from openplugin.plugins.plugin import Plugin
from openplugin.plugins.plugin_selector import PluginSelector


class LangchainPluginSelector(PluginSelector):
    def __init__(
        self,
        tool_selector_config: ToolSelectorConfig,
        plugins: List[Plugin],
        config: Optional[Config],
        llm: Optional[LLM],
    ):
        super().__init__(tool_selector_config, plugins, config, llm)
        self.initialize()

    def initialize(self):
        agent_type = get_agent_type(self.tool_selector_config.pipeline_name)
        tools = load_tools(["requests_all"])
        for plugin in self.plugins:
            if plugin.manifest_url:
                api_config = ApiConfig(type="openapi", url=plugin.openapi_doc_url)
                ai_plugin = AIPlugin(
                    schema_version=plugin.schema_version,
                    name_for_model=plugin.name,
                    name_for_human=plugin.name,
                    description_for_model=plugin.description,
                    description_for_human=plugin.description,
                    auth={"type": "none"},
                    api=api_config,
                    logo_url=plugin.logo_url,
                    contact_email=plugin.contact_email,
                    legal_info_url=plugin.legal_info_url,
                )
                api_spec = (
                    f"Usage Guide: {plugin.description}\n\n"
                    f"OpenAPI Spec: {plugin.get_openapi_doc_json()}"
                )
                ai_plugin_tool = AIPluginTool(
                    name=plugin.name,
                    description=plugin.description,
                    plugin=ai_plugin,
                    api_spec=api_spec,
                )
                tools.append(ai_plugin_tool)
        llm = get_llm(self.llm, self.config.openai_api_key)
        self.agent = initialize_agent(
            tools=tools,
            llm=llm,
            agent=agent_type,
            verbose=False,
            return_intermediate_steps=True,
        )

    def run(self, messages: List[Message]) -> SelectedPluginsResponse:
        pre_prompts = ""
        for plugin in self.plugins:
            pre_prompts += plugin.get_plugin_pre_prompts()

        with get_openai_callback() as cb:
            start_test_case_time = time.time()
            message = messages[-1]
            detected_plugin_operations = []
            response_prompt = None
            try:
                prompt = f"{pre_prompts}\n{message.content}"
                response = self.agent(prompt)
                response_prompt = response["output"]
                for step in response["intermediate_steps"]:
                    detected_plugin = self.get_plugin_by_name(step[0].tool)
                    if detected_plugin:
                        plugin_operation = PluginDetected(
                            plugin=detected_plugin,
                            api_called=None,
                            method=None,
                        )
                        detected_plugin_operations.append(plugin_operation)

                for step in response["intermediate_steps"]:
                    if step[0].tool_input:
                        url = step[0].tool_input
                        if url.startswith("'"):
                            url = url[1:-1]
                        if url.endswith("'"):
                            url = url[:-1]
                        if url.lower() != "none":
                            api = url.split("?")[0].strip()
                            for detected_plugin_operation in detected_plugin_operations:
                                if detected_plugin_operation.plugin.has_api_endpoint(
                                    api
                                ):
                                    detected_plugin_operation.api_called = api
            except Exception as e:
                # TODO: handle this better, use callback
                response = str(e)
                for line in response.splitlines():
                    if line.strip().startswith(
                        "Action"
                    ) and not line.strip().startswith("Action Input"):
                        plugin = line.split(":")[1].strip()
                        if plugin:
                            detected_plugin = self.get_plugin_by_name(str(plugin))
                            if detected_plugin:
                                plugin_operation = PluginDetected(
                                    plugin=detected_plugin,
                                    api_called=None,
                                    method=None,
                                )
                                detected_plugin_operations.append(plugin_operation)
                matches = re.findall(r'"([^"]*)"', response)
                for url in matches:
                    if url.startswith("http"):
                        for detected_plugin_operation in detected_plugin_operations:
                            if detected_plugin_operation.plugin.has_api_endpoint(api):
                                detected_plugin_operation.api_called = api

            response_obj = SelectedPluginsResponse(
                run_completed=True,
                final_text_response=response_prompt,
                detected_plugin_operations=detected_plugin_operations,
                response_time=round(time.time() - start_test_case_time, 2),
                tokens_used=cb.total_tokens,
                llm_api_cost=round(cb.total_cost, 4),
            )
            return response_obj
"""
