import ast
import asyncio
import base64
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
from langchain_core.messages.ai import AIMessage
from langchain_core.messages.human import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import ToolException
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from ..agent_actions import InpResponse
from ..agent_execution import (
    AgentExecution,
    AgentExecutionResponse,
    AgentInteractiveExecutionResponse,
)
from ..agent_input import AgentManifest, AgentPrompt, AgentRuntime, MessageType


class ToolAuthMissingException(ToolException):
    """Exception raised when a specific tool is not found."""

    def __init__(self, openapi_doc_url, message="Auth not provided for tool"):
        self.openapi_doc_url = openapi_doc_url
        self.message = f"{message}: {openapi_doc_url}"
        super().__init__(self.message)


def get_basic_token(username, password):
    credentials = username + ":" + password
    moz_auth_cred = base64.b64encode(credentials.encode())
    return moz_auth_cred.decode("UTF-8")


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
    response = asyncio.run(
        run_pipeline(
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
    )
    return response


async def arun_plugin(
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
    response = await run_pipeline(
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
    tool_map: Dict[str, Dict] = {}
    openplugin_tools_by_name = {}
    openplugin_tools_by_url = {}
    for tool_input in tools_input:
        openplugin_json = requests.get(tool_input["openapi_doc_url"]).json()
        name = openplugin_json.get("x-openplugin", {}).get("name")
        plugin_key = None
        if tool_key_map:
            plugin_key = tool_key_map.get(tool_input["openapi_doc_url"])
        config = {"openai_api_key": openai_api_key}
        picked_operations = {}
        for ops in tool_input.get("operations", []):
            if ops.get("method") is not None and ops.get("path") is not None:
                picked_operations[ops.get("method") + "<PATH>" + ops.get("path")] = (
                    ops.get("output_module_name")
                )

        for path, path_obj in openplugin_json.get("paths", {}).items():
            for method, method_obj in path_obj.items():
                sp = method + "<PATH>" + path
                if sp in picked_operations:
                    summary = method_obj.get("summary", "")
                    human_usage_examples = method_obj.get(
                        "x-human-usage-examples", []
                    )
                    helpers = method_obj.get("x-helpers", [])
                    few_shot_examples = method_obj.get("x-few-shot-examples", [])
                    description = f"""Summary: {summary}
                    Human Usage Examples: {human_usage_examples}
                    Helpers: {helpers}
                    Few Shot Examples: {few_shot_examples}  
                    """
                    tool = OpenpluginOperationTool(
                        name=method_obj.get("operationId"),
                        operation_path=path,
                        operation_method=method,
                        output_module_name=picked_operations.get(sp),
                        description=description,
                        summary=summary,
                        human_usage_examples=human_usage_examples,
                        helpers=helpers,
                        few_shot_examples=few_shot_examples,
                        openplugin_server_url=openplugin_server_url,
                        openplugin_api_key=openplugin_api_key,
                        openapi_doc_url=tool_input["openapi_doc_url"],
                        header=None,
                        auth_obj=openplugin_json.get("x-plugin-auth", {}),
                        config=config,
                    )
                    if plugin_key:
                        tool.set_plugin_auth(plugin_key)
                    openplugin_tools_by_name[name] = tool
                    openplugin_tools_by_url[tool_input["openapi_doc_url"]] = tool
                    tool_map[method_obj.get("operationId")] = {
                        "plugin_name": name,
                        "path": path,
                        "method": method,
                        "openapi_doc_url": tool_input["openapi_doc_url"],
                        "openapi_doc_json": openplugin_json,
                    }
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
    return (
        agent_executor,
        tool_map,
        openplugin_tools_by_name,
        openplugin_tools_by_url,
    )


class SearchInput(BaseModel):
    query: str = Field(description="should be a search query")


class OpenpluginOperationTool(BaseTool):
    name: str
    operation_path: str
    operation_method: str
    output_module_name: Optional[str] = None
    description: str = Field(description="Description of the tool")
    summary: Optional[str] = None
    human_usage_examples: Optional[List[str]] = []
    helpers: Optional[List[str]] = []
    few_shot_examples: Optional[List] = []
    openplugin_server_url: Optional[str] = None
    openplugin_api_key: Optional[str] = None
    auth_obj: Dict = Field(description="Auth object")
    openapi_doc_url: str = Field(description="URL of the OpenAPI doc")
    header: Optional[Dict] = Field(description="Header for the tool")
    config: Dict = {}
    args_schema: Type[BaseModel] = SearchInput  # type: ignore
    response_format: str = "content_and_artifact"

    def _run(
        self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> Tuple[str, Dict]:
        """Use the tool."""
        if not self.is_auth_provided():
            raise ToolAuthMissingException(self.openapi_doc_url)
        if self.openplugin_server_url is not None:
            response_json = run_plugin_api(
                openplugin_server_url=self.openplugin_server_url,
                openplugin_api_key=self.openplugin_api_key,
                prompt=query,
                openapi_doc_url=self.openapi_doc_url,
                header=self.header,
                config=self.config,
                selected_operations=self.get_selected_operations(),
                output_module_names=self.get_output_module_names(),
            )
        else:
            response_json = run_plugin(
                prompt=query,
                openapi_doc_url=self.openapi_doc_url,
                header=self.header,
                config=self.config,
                selected_operations=self.get_selected_operations(),
                output_module_names=self.get_output_module_names(),
            )
        original_response = (
            response_json.get("response", {})
            .get("output_module_map", {})
            .get("original_response", {})
            .get("value", {})
        )
        return json.dumps(original_response), response_json

    async def _arun(
        self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> Tuple[str, Dict]:
        """Use the tool."""
        if not self.is_auth_provided():
            raise ToolAuthMissingException(self.openapi_doc_url)
        if self.openplugin_server_url is not None:
            response_json = run_plugin_api(
                openplugin_server_url=self.openplugin_server_url,
                openplugin_api_key=self.openplugin_api_key,
                prompt=query,
                openapi_doc_url=self.openapi_doc_url,
                header=self.header,
                config=self.config,
                selected_operations=self.get_selected_operations(),
                output_module_names=self.get_output_module_names(),
            )
        else:
            response_json = await arun_plugin(
                prompt=query,
                openapi_doc_url=self.openapi_doc_url,
                header=self.header,
                config=self.config,
                selected_operations=self.get_selected_operations(),
                output_module_names=self.get_output_module_names(),
            )
        original_response = (
            response_json.get("response", {})
            .get("output_module_map", {})
            .get("original_response", {})
            .get("value", {})
        )
        return json.dumps(original_response), response_json

    def is_auth_provided(self) -> bool:
        if self.auth_obj.get("type") is None or self.auth_obj.get("type") == "none":
            return True
        if self.header:
            return True
        return False

    def get_output_module_names(self):
        output_module_names = []
        if self.output_module_name:
            output_module_names.append(self.output_module_name)
        output_module_names.append("original_response")
        return output_module_names

    def set_plugin_auth(self, plugin_auth):
        if plugin_auth:
            user_http_token = plugin_auth.get("user_http_token")
            authorization_type = self.auth_obj.get("authorizationType")
            query_param_key = self.auth_obj.get("query_param_key")
            if user_http_token:
                if authorization_type == "bearer":
                    self.header = {"Authorization": f"Bearer {user_http_token}"}
                    return
                if authorization_type == "header_param":
                    self.header = {query_param_key: user_http_token}
                    return

            basic_username = plugin_auth.get("basic_username")
            basic_password = plugin_auth.get("basic_password")
            if basic_username and basic_password:
                basic_token = get_basic_token(basic_username, basic_password)
                self.header = {"Authorization": f"Basic {basic_token}"}
                return

            oauth_access_token = plugin_auth.get("oauth_access_token")
            if oauth_access_token is not None:
                self.header = {"Authorization": f"Bearer {oauth_access_token}"}
                return

    def get_selected_operations(self):
        return [self.operation_method + "<PATH>" + self.operation_path]


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

    agent_executor, tool_map, openplugin_tools_by_name, openplugin_tools_by_url = (
        build_agent_executor(
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
    )
    return (
        agent_executor,
        tool_map,
        openplugin_tools_by_name,
        openplugin_tools_by_url,
    )


class AgentExecutionWithOperationLangchain(AgentExecution):

    def __init__(
        self,
        agent_manifest: AgentManifest,
        agent_runtime: AgentRuntime,
        websocket: Optional[WebSocket] = None,
    ):
        self.agent, tool_map, openplugin_tools_by_name, openplugin_tools_by_url = (
            get_langchain_agent(agent_manifest, agent_runtime)
        )
        super().__init__(
            agent_manifest,
            agent_runtime,
            tool_map,
            openplugin_tools_by_name,
            openplugin_tools_by_url,
        )
        self.websocket = websocket

    async def run_agent_batch(
        self, agent_prompts: List[AgentPrompt], conversations: List[AgentPrompt]
    ) -> AgentExecutionResponse:

        input_prompt = agent_prompts[-1].prompt
        print("----------------------------------------------------------------")
        chat_history = self.build_chat_history(conversations)
        for ch in chat_history:
            print(f"INPUT: {ch}")
            print("-------------------")
        print("----------------------------------------------------------------")
        tools_called = []
        final_response = ""
        async for event in self.agent.astream_events(
            {"input": input_prompt, "chat_history": chat_history},
            version="v1",
        ):
            kind = event["event"]

            # if kind != "on_chat_model_stream":
            # print("=-=-=-=-=-=-=-=-=-=-=-=-=-=")
            # print(kind)
            # print("=-=-=-=-=-=-=-=-=-=-=-=-=-=")
            if kind == "on_chain_start":
                if (
                    event["name"] == "Agent"
                ):  # Was assigned when creating the agent with `.with_config({"run_name": "Agent"})`
                    print("******************* ON_CHAIN_START ******************")
                    print(
                        f"Starting agent: {event['name']} with input: {event['data'].get('input')}"
                    )
            elif kind == "on_chain_end":
                if (
                    event["name"] == "Agent"
                ):  # Was assigned when creating the agent with `.with_config({"run_name": "Agent"})`
                    print("******************* ON_CHAIN_END ******************")
                    print(
                        f"Done agent: {event['name']} with output: {event['data'].get('output')['output']}"
                    )
            if kind == "on_chat_model_stream":
                content = event["data"]["chunk"].content
                if content:
                    final_response = final_response + content
            elif kind == "on_tool_start":
                print("\n\n******************* ON_TOOL_START ******************")
                print(
                    f"Starting tool: {event['name']} with inputs: {event['data'].get('input')}"
                )
                plugin_obj = self.tool_map.get(event["name"], {})
                openplugin_tool = self.openplugin_tools_by_name.get(
                    plugin_obj.get("plugin_name", "")
                )
                # if openplugin_tool and not openplugin_tool.is_auth_provided():
                #    raise Exception("Auth not provided for tool")

                tool_action_obj = {
                    "tool": event["name"],
                    "plugin": plugin_obj,
                    "query": event["data"].get("input").get("query"),
                    "execution_id": event["run_id"],
                }
                await self.send_json_message(
                    InpResponse.AGENT_JOB_STEP,
                    self.websocket,
                    tool_action_obj,
                    "plugin_started",
                )
            elif kind == "on_tool_end":
                print("\n\n******************* ON_TOOL_END ******************")
                print(f"Done tool: {event['name']}")
                plugin_obj = self.tool_map.get(event["name"], {})
                openplugin_tool = self.openplugin_tools_by_name.get(
                    plugin_obj.get("plugin_name", "")
                )

                print(openplugin_tool)
                display_response = False
                if openplugin_tool and openplugin_tool.output_module_name:
                    display_response = True
                if event["data"].get("output"):
                    tuple_val = ast.literal_eval(event["data"].get("output"))
                    tool_action_obj = {
                        "tool": event["name"],
                        "display_response": display_response,
                        "query": event["data"].get("input").get("query"),
                        "plugin": plugin_obj,
                        "plugin_response": tuple_val[1],
                        "execution_id": event["run_id"],
                    }
                    await self.send_json_message(
                        InpResponse.AGENT_JOB_STEP,
                        self.websocket,
                        tool_action_obj,
                        "plugin_ended",
                    )
                    tools_called.append(tool_action_obj)
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

    def build_chat_history(self, conversations: List[AgentPrompt]):
        history = []
        if conversations and len(conversations) > 1:
            for conversation in conversations[:-1]:
                if conversation.message_type == MessageType.USER:
                    history.append(HumanMessage(content=conversation.prompt))
                elif conversation.message_type == MessageType.AGENT:
                    history.append(AIMessage(content=conversation.prompt))  # type: ignore
        return history
