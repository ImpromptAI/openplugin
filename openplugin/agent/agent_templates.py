def get_langchain_openai_agent_template():
    template = """
import json
import os
import sys
from typing import Dict, List, Optional, Type

import requests
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from langchain.tools import BaseTool

def run_plugin(
    openplugin_server_url,
    openplugin_api_key,
    prompt,
    openapi_doc_url,
    header,
    config,
    enable_ui_form_controls=True,
    auth_query_param={},
    conversation=[],
    function_provider_name="OpenAI [gpt-4]",
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
        "header": header,
        "auth_query_param": auth_query_param,
        "run_all_output_modules": False,
        "config": config,
        "enable_ui_form_controls": enable_ui_form_controls,
        "selected_operations":selected_operations
    }
    payload = json.dumps(payload_obj)
    headers = {"Content-Type": "application/json", "x-api-key": openplugin_api_key}
    OPENPLUGIN_PLUGIN_EXECUTION_URL = f"{openplugin_server_url}/api/plugin-execution-pipeline"
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


def build_plugin_auth_header(x_plugin_auth: Dict, key: str):
    if x_plugin_auth.get("type") == "user_http":
        if x_plugin_auth.get("authorizationType") == "bearer":
            return {"Authorization": f"Bearer {key}"}
    elif x_plugin_auth.get("type") == "none":
        return {}
    raise ValueError("Invalid x-plugin-auth header")


def build_agent_executor(
    openplugin_server_url: str,
    openplugin_api_key: str,
    openai_api_key: str,
    instruction: str,
    tool_key_map: Dict,
    tools_input: List[Dict],
    provider: str,
    model: str,
    temperature: float = 1,
):
    llm = build_llm_model(provider, model, temperature)
    tools = []
    for tool_input in tools_input:
        openplugin_json = requests.get(tool_input["openapi_doc_url"]).json()
        name = openplugin_json.get("x-openplugin", {}).get("name")
        key_name = name.upper().replace("-", "_").replace(" ", "_").replace(",", "")
        tool_id = str(tool_input["tool_id"])
        header = build_plugin_auth_header(
            openplugin_json.get("x-plugin-auth", {}),
            tool_key_map.get(tool_id, {}).get("KEY"),
        )
        config = {"openai_api_key": openai_api_key}
        tool = OpenpluginTool(
            name=key_name,
            description=openplugin_json.get("x-openplugin", {}).get("description"),
            openplugin_server_url=openplugin_server_url,
            openplugin_api_key=openplugin_api_key,
            openapi_doc_url=tool_input["openapi_doc_url"],
            header=header,
            config=config,
        )
        tools.append(tool)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", instruction),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    agent = create_openai_tools_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    return agent_executor

class SearchInput(BaseModel):
    query: str = Field(description="should be a search query")

class OpenpluginTool(BaseTool):
    name: str
    description: str
    openplugin_server_url: str
    openplugin_api_key: str
    openapi_doc_url: str = Field(description="URL of the OpenAPI doc")
    header: Optional[Dict] = Field(description="Header for the tool")
    config: Dict = {}
    args_schema: Type[BaseModel] = SearchInput

    def _run(
        self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        response_json = run_plugin(
            openplugin_server_url=self.openplugin_server_url,
            openplugin_api_key=self.openplugin_api_key,
            prompt=query,
            openapi_doc_url=self.openapi_doc_url,
            header=self.header,
            config=self.config,
        )
        original_response = (
            response_json.get("response", {})
            .get("output_module_map", {})
            .get("original_response", {})
            .get("value")
        )
        return {"response": original_response}

    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        raise NotImplementedError("Calculator does not support async")


def run_agent(agent_executor, input_prompt):
    print("----------------------------------------------------------------")
    print("INPUT: {}".format(input_prompt))
    print("----------------------------------------------------------------")
    response = {}
    for step in agent_executor.iter({"input": input_prompt}):
        if output := step.get("intermediate_step"):
            action, value = output[0]
            print("\n======================STEP======================")
            print("\naction: ", action)
            print("\nvalue: ", value)
    return response


def setup_agent():
    # required environment variables
    $REQUIRED_KEYS

    instruction = $INSTRUCTION
    tools_input =  $TOOLS_INPUT
    tool_key_map = $TOOL_KEY_MAP
    provider = $PROVIDER
    model = $MODEL
    temperature = $TEMPERATURE

    agent_executor = build_agent_executor(
        openplugin_server_url=OPENPLUGIN_SERVER_URL,
        openplugin_api_key=OPENPLUGIN_API_KEY,
        openai_api_key=OPENAI_API_KEY,
        instruction=instruction,
        tool_key_map=tool_key_map,
        tools_input=tools_input,
        provider=provider,
        model=model,
        temperature=temperature,
    )
    return agent_executor


def main(args):
    if len(args) < 2:
        print("Usage: python agent_execution.py <input_prompt>")
        return
    input_prompt = args[1]
    response = run_agent(agent_executor=setup_agent(), input_prompt=input_prompt)
    print("=-=-=-=-= FINAL RESPONSE =-=-=-=-=")
    print(response)


if __name__ == "__main__":
    main(sys.argv)

# sample:  OPENPLUGIN_SERVER_URL=<VAL> OPENPLUGIN_API_KEY=<VAL> OPENAI_API_KEY=<VAL> DEMO_PLUGIN_SHRI_KEY=<VAL> python agent_execution.py <INPUT_PROMPT>"""
    return template
