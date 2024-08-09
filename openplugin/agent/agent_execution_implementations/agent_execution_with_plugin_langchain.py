import json
from typing import Dict, List, Optional, Tuple, Type

import requests
from fastapi import WebSocket
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain.tools import BaseTool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from ..agent_actions import InpResponse
from ..agent_execution import (
    AgentExecution,
    AgentExecutionResponse,
    AgentInteractiveExecutionResponse,
)
from ..agent_input import AgentManifest, AgentPrompt, AgentRuntime


def run_plugin(
    prompt,
    openapi_doc_url,
    header,
    config,
    enable_ui_form_controls=True,
    auth_query_param={},
    conversation=[],
    function_provider_name="OpenAI [gpt-4o]",
    output_module_names=None,
    selected_operations=None,
    session_variables=None,
):
    from ...core.config import Config
    from ...utils.run_plugin_pipeline import run_pipeline

    if header is None:
        header = {}
    config = Config(**config)
    selected_operations = None
    response = run_pipeline(
        openapi_doc_obj=None,
        openapi_doc_url=openapi_doc_url,
        prompt=prompt,
        header=header,
        function_provider_name=function_provider_name,
        conversation=conversation,
        auth_query_param=auth_query_param,
        config=config,
        run_all_output_modules=False,
        enable_ui_form_controls=enable_ui_form_controls,
        session_variables=session_variables,
        output_module_names=output_module_names,
        selected_operations=selected_operations,
    )
    return response


def run_plugin_api(
    openplugin_server_url,
    openplugin_api_key,
    prompt,
    openapi_doc_url,
    header,
    config,
    enable_ui_form_controls=True,
    auth_query_param={},
    conversation=[],
    function_provider_name="OpenAI [gpt-4o]",
    output_module_names=None,
    selected_operations=None,
    session_variables=None,
):
    if header is None:
        header = {}
    payload_obj = {
        "prompt": prompt,
        "openapi_doc_url": openapi_doc_url,
        "conversation": conversation,
        "output_module_names": output_module_names,
        "function_provider": {"name": function_provider_name},
        "header": {"Authorization": "Bearer abcd123"},
        "auth_query_param": auth_query_param,
        "run_all_output_modules": False,
        "config": config,
        "enable_ui_form_controls": enable_ui_form_controls,
        "selected_operations": selected_operations,
    }
    payload = json.dumps(payload_obj)
    headers = {"Content-Type": "application/json", "x-api-key": openplugin_api_key}
    OPENPLUGIN_PLUGIN_EXECUTION_URL = (
        f"{openplugin_server_url}/api/plugin-execution-pipeline"
    )
    response = requests.post(
        OPENPLUGIN_PLUGIN_EXECUTION_URL,
        headers=headers,
        data=payload,
    )
    if response.status_code != 200:
        raise ValueError("Error in running plugin")
    return response.json()


def build_llm_model(provider: str, model: str, temperature: float = 1):
    if provider.lower() == "openai":
        llm = ChatOpenAI(temperature=temperature, model=model)
        return llm
    raise ValueError("Invalid LLM Provider")


def build_plugin_auth_header(
    x_plugin_auth: Dict, openapi_doc_url: str, tool_key_map: Optional[Dict]
):
    if x_plugin_auth.get("type") == "user_http":
        if x_plugin_auth.get("authorizationType") == "bearer":
            if not tool_key_map:
                raise ValueError(
                    "Provide key for plugin: {}".format(openapi_doc_url)
                )
            key = tool_key_map.get(openapi_doc_url, {}).get("key")
            if key is None:
                raise ValueError(
                    "Provide key for plugin: {}".format(openapi_doc_url)
                )
            return {"Authorization": f"Bearer {key}"}
    elif x_plugin_auth.get("type") == "none":
        return {}
    raise ValueError("Invalid x-plugin-auth header")


def build_agent_executor(
    openai_api_key: str,
    instruction: Optional[str],
    tool_key_map: Optional[Dict],
    tools_input: List[Dict],
    provider: str,
    model: str,
    temperature: float = 1,
    openplugin_server_url: Optional[str] = None,
    openplugin_api_key: Optional[str] = None,
):
    llm = build_llm_model(provider, model, temperature)
    tools = []
    for tool_input in tools_input:
        openplugin_json = requests.get(tool_input["openapi_doc_url"]).json()
        name = openplugin_json.get("x-openplugin", {}).get("name")
        key_name = name.upper().replace("-", "_").replace(" ", "_").replace(",", "")
        header = build_plugin_auth_header(
            openplugin_json.get("x-plugin-auth", {}),
            tool_input["openapi_doc_url"],
            tool_key_map,
        )
        config = {"openai_api_key": openai_api_key}
        selected_operation_values = None
        selected_operations = tool_input.get("operations")
        if selected_operations and len(selected_operations) > 0:
            selected_operation_values = []
            for ops in selected_operations:
                if ops.get("method") is not None and ops.get("path") is not None:
                    selected_operation_values.append(
                        ops.get("method", "") + "<PATH>" + ops.get("path")
                    )
        tool = OpenpluginTool(
            name=key_name,
            description=openplugin_json.get("x-openplugin", {}).get("description"),
            openplugin_server_url=openplugin_server_url,
            openplugin_api_key=openplugin_api_key,
            selected_operations=tool_input.get("operations"),
            openapi_doc_url=tool_input["openapi_doc_url"],
            header=header,
            config=config,
            selected_operation_values=selected_operation_values,
        )
        tools.append(tool)
    if instruction is None:
        instruction = ""
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", instruction),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    agent = create_openai_tools_agent(llm, tools, prompt)

    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)  # type: ignore
    return agent_executor


class SearchInput(BaseModel):
    query: str = Field(description="should be a search query")


class OpenpluginTool(BaseTool):
    name: str
    description: str
    openplugin_server_url: Optional[str] = None
    openplugin_api_key: Optional[str] = None
    selected_operations: Optional[List[Dict]] = Field(
        description="Selected operations"
    )
    selected_operation_values: Optional[List[str]] = None
    openapi_doc_url: str = Field(description="URL of the OpenAPI doc")
    header: Optional[Dict] = Field(description="Header for the tool")
    config: Dict = {}
    args_schema: Type[BaseModel] = SearchInput  # type: ignore
    response_format: str = "content_and_artifact"

    def _run(
        self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> Tuple[str, Dict]:
        """Use the tool."""
        if self.openplugin_server_url is not None:
            response_json = run_plugin_api(
                openplugin_server_url=self.openplugin_server_url,
                openplugin_api_key=self.openplugin_api_key,
                prompt=query,
                openapi_doc_url=self.openapi_doc_url,
                header=self.header,
                config=self.config,
                selected_operations=self.selected_operation_values,
            )
        else:
            response_json = run_plugin(
                prompt=query,
                openapi_doc_url=self.openapi_doc_url,
                header=self.header,
                config=self.config,
                selected_operations=self.selected_operation_values,
            )
        original_response = (
            response_json.get("response", {})
            .get("output_module_map", {})
            .get("original_response", {})
            .get("value", {})
        )
        return json.dumps(original_response), response_json

    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("Calculator does not support async")


def get_langchain_agent(agent_manifest: AgentManifest, agent_runtime: AgentRuntime):
    # required environment variables
    openplugin_api_key = agent_runtime.secrets.openplugin_api_key
    openplugin_server_url = agent_runtime.secrets.openplugin_server_url
    openai_api_key = agent_runtime.secrets.openai_api_key

    instruction = agent_manifest.instruction

    tools_input = agent_manifest.get_tools_json()

    tool_key_map = agent_runtime.secrets.plugin_keys

    provider = agent_runtime.model.provider
    model = agent_runtime.model.model
    temperature = agent_runtime.model.get_temperature()

    agent_executor = build_agent_executor(
        openai_api_key=openai_api_key,
        instruction=instruction,
        tool_key_map=tool_key_map,
        tools_input=tools_input,
        provider=provider,
        model=model,
        temperature=temperature,
        openplugin_server_url=openplugin_server_url,
        openplugin_api_key=openplugin_api_key,
    )
    return agent_executor


class AgentExecutionWithPluginLangchain(AgentExecution):

    def __init__(
        self,
        agent_manifest: AgentManifest,
        agent_runtime: AgentRuntime,
        websocket: Optional[WebSocket] = None,
    ):
        tool_map: Dict = {}
        super().__init__(agent_manifest, agent_runtime, tool_map)
        self.agent = get_langchain_agent(self.agent_manifest, self.agent_runtime)
        self.websocket = websocket

    async def run_agent_batch(
        self, agent_prompts: List[AgentPrompt]
    ) -> AgentExecutionResponse:
        input_prompt = agent_prompts[0].prompt
        print("----------------------------------------------------------------")
        print("INPUT: {}".format(input_prompt))
        print("----------------------------------------------------------------")
        tools_called = []
        final_response = ""
        for step in self.agent.iter({"input": input_prompt}):
            print("-------")
            print("STEP: ", step)
            print(type(step))
            print("-------")
            if output := step.get("intermediate_step"):
                action, value = output[0]
                print("\n======================STEP======================")
                print(type(action))
                print("\naction: ", action)
                print(type(value))
                print("\nvalue: ", value)
                print(output)
                tool_action_obj = {
                    "tool": action.tool,
                    "query": action.tool_input.get("query"),
                    "agent_log": action.log,
                    "plugin_response": value[1],
                }
                await self.send_json_message(
                    InpResponse.AGENT_JOB_STEP,
                    self.websocket,
                    tool_action_obj,
                    "ran_plugin",
                )
                tools_called.append(tool_action_obj)
            else:
                final_response = step.get("output")
        return AgentExecutionResponse(
            final_response=final_response, tools_called=tools_called
        )

    def interactive_run(
        self, agent_prompt: AgentPrompt
    ) -> AgentInteractiveExecutionResponse:
        raise NotImplementedError("Interactive run not supported")

    def stop(self):
        # Not able to find a way to stop the agent in langchain yet. There is a way to force stop base on time limit.
        pass
