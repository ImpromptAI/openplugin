import os
import time
from typing import List, Optional
from langchain.llms import OpenAI
from langchain.agents import AgentType
from langchain.tools import AIPluginTool
from urllib.parse import urlparse, parse_qs
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import get_openai_callback
from langchain.agents import load_tools, initialize_agent
from openplugin import Config, ToolSelectorConfig, PluginOperation, Plugin, PluginSelector, LLMProvider, \
    Message, Response, LLM


def _get_agent_type(pipeline_name: str) -> AgentType:
    if pipeline_name == "zero-shot-react-description":
        return AgentType.ZERO_SHOT_REACT_DESCRIPTION
    elif pipeline_name == "react-docstore":
        return AgentType.REACT_DOCSTORE
    elif pipeline_name == "self-ask-with-search":
        return AgentType.SELF_ASK_WITH_SEARCH
    elif pipeline_name == "conversational-react-description":
        return AgentType.CONVERSATIONAL_REACT_DESCRIPTION
    elif pipeline_name == "chat-zero-shot-react-description":
        return AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION
    elif pipeline_name == "chat-conversational-react-description":
        return AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION
    elif pipeline_name == "structured-chat-zero-shot-react-description":
        return AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION
    raise ValueError(f"Pipeline name {pipeline_name} not supported")


def _get_llm(llm: LLM, api_key: str):
    if llm.provider == LLMProvider.OpenAI:
        if api_key is None:
            api_key = os.environ["OPENAI_API_KEY"]
        os.environ["OPENAI_API_KEY"] = api_key
        llm = OpenAI(
            model_name=llm.model_name,
            temperature=llm.temperature,
            max_tokens=llm.max_tokens,
            top_p=llm.top_p,
            frequency_penalty=llm.frequency_penalty,
            presence_penalty=llm.presence_penalty,
            n=llm.n,
            best_of=llm.best_of
        )
        return llm
    elif llm.provider == LLMProvider.OpenAIChat:
        if api_key is None:
            api_key = os.environ["OPENAI_API_KEY"]
        os.environ["OPENAI_API_KEY"] = api_key
        llm = ChatOpenAI(
            model_name=llm.model_name,
            temperature=llm.temperature,
            max_retries=llm.max_retries,
            n=llm.n,
            max_tokens=llm.max_tokens
        )
        return llm
    raise ValueError(f"LLM provider {llm.provider} not supported")


class LangchainPluginSelector(PluginSelector):
    def __init__(
            self,
            tool_selector_config: ToolSelectorConfig,
            plugins: List[Plugin],
            config: Optional[Config],
            llm: Optional[LLM]):
        super().__init__(tool_selector_config, plugins, config, llm)

    def initialize_tool_selector(
            self,
            tool_selector_config: ToolSelectorConfig,
            plugins: List[Plugin],
            config: Config,
            llm: LLM
    ):
        agent_type = _get_agent_type(tool_selector_config.pipeline_name)
        tools = load_tools(["requests_all"])
        for plugin in plugins:
            if plugin.manifest_url:
                tools.append(AIPluginTool.from_plugin_url(plugin.manifest_url.strip()))
        llm = _get_llm(llm, config.openai_api_key)
        self.agent = initialize_agent(
            tools=tools,
            llm=llm,
            agent=agent_type,
            verbose=False,
            return_intermediate_steps=True
        )

    def run(self, messages: List[Message]) -> Response:
        with get_openai_callback() as cb:
            start_test_case_time = time.time()
            message = messages[-1]
            response = self.agent(message.content)
            response_prompt = response['output']

            detected_plugin_operations = []
            for step in response["intermediate_steps"]:
                detected_plugin = self.get_plugin_by_name(step[0].tool)
                if detected_plugin:
                    plugin_operation = PluginOperation(plugin=detected_plugin)
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
                        extracted_params = {k: v[0] if type(v) == list and len(v) == 1 else v for k, v in
                                            query_dict.items()}
                        for detected_plugin_operation in detected_plugin_operations:
                            if detected_plugin_operation.plugin.has_api_endpoint(api):
                                detected_plugin_operation.api_called = api
                                detected_plugin_operation.mapped_operation_parameters = extracted_params

            response_obj = Response(
                run_completed=True,
                final_text_response=response_prompt,
                detected_plugin_operations=detected_plugin_operations,
                response_time=round(time.time() - start_test_case_time, 2),
                tokens_used=cb.total_tokens,
                llm_api_cost=round(cb.total_cost, 4)
            )
            return response_obj
