import json
from typing import Any, Dict, List, Optional

from httpx import request
from pydantic import BaseModel, Field, model_validator

from .agent_templates import get_langchain_openai_agent_template


class OperationInput(BaseModel):
    path: str = Field(description="Path of the operation")
    method: str = Field(description="HTTP method of the operation")


class ToolInput(BaseModel):
    openapi_doc_url: str = Field(description="URL of the OpenAPI doc")
    operations: List[OperationInput] = Field(
        description="List of operations to be executed"
    )

    def get_tool_operation_json(self):
        operations = []
        for operation in self.operations:
            operation_input = {
                "path": operation.path,
                "method": operation.method,
            }
            operations.append(operation_input)
        return operations


class AgentImplementation(BaseModel):
    provider: str = Field(description="Provider of the agent")
    type: str = Field(description="Type of the agent")


class ModelInput(BaseModel):
    provider: str = Field(description="Provider of the model")
    model: str = Field(description="Model name")
    temperature: Optional[float] = Field(description="Temperature of the model")

    def get_temperature(self):
        if self.temperature:
            return self.temperature
        return 1.0


class Secret(BaseModel):
    openai_api_key: str = Field(description="OpenAI API key")
    openplugin_api_key: Optional[str] = None
    openplugin_server_url: Optional[str] = None
    plugin_keys: Optional[Dict] = {}


class AgentManifest(BaseModel):
    agent_url: Optional[str] = None
    name: str
    instruction: str
    tools: List[ToolInput]

    @model_validator(mode="before")
    @classmethod
    def check_agent_manifest_url(cls, data: Any) -> Any:
        if isinstance(data, dict):
            agent_url = data.get("agent_url")
            if agent_url:
                agent_json = request("GET", agent_url).json()
                data["name"] = agent_json.get("name")
                data["instruction"] = agent_json.get("instruction")
                data["tools"] = agent_json.get("tools")
        return data

    def get_tools_json(self):
        tools = []
        id = 1
        for tool in self.tools:
            tool_input = {
                "tool_id": id,
                "openapi_doc_url": tool.openapi_doc_url,
                "operations": tool.get_tool_operation_json(),
            }
            tools.append(tool_input)
            id = id + 1
        return tools

    def get_langchain_openai_tools_agent(self):
        template = get_langchain_openai_agent_template()
        instruction = self.instruction
        provider = self.model.provider
        model = self.model.model
        temperature = self.model.temperature
        tools = []
        id = 1
        tool_key_map = {}
        plugin_environment_variables = ""
        for tool in self.tools:
            tool_input = {
                "tool_id": id,
                "openapi_doc_url": tool.openapi_doc_url,
            }
            tool_key_map[str(id)] = {"KEY": f"PLUGIN_{id}_KEY"}
            plugin_environment_variables += (
                f'PLUGIN_{id}_KEY = os.environ["PLUGIN_{id}_KEY"]\n'
            )
            id += 1
            tools.append(tool_input)

        required_keys = f"""
    OPENPLUGIN_API_KEY = os.environ["OPENPLUGIN_API_KEY"]
    OPENPLUGIN_SERVER_URL = os.environ["OPENPLUGIN_SERVER_URL"]
    OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
        
    {plugin_environment_variables}
        """
        template = (
            template.replace("$TOOLS_INPUT", json.dumps(tools))
            .replace("$INSTRUCTION", instruction)
            .replace("$PROVIDER", provider)
            .replace("$MODEL", model)
            .replace("$TEMPERATURE", str(temperature))
            .replace("$TOOL_KEY_MAP", json.dumps(tool_key_map))
            .replace("$REQUIRED_KEYS", required_keys)
        )
        return template


class AgentRuntime(BaseModel):
    secrets: Secret = Field(..., alias="secrets")
    model: ModelInput = Field(..., alias="model")
    implementation: AgentImplementation = Field(..., alias="implementation")


class AgentPrompt(BaseModel):
    prompt: str = Field(description="Prompt for the agent")
    associated_job_id: Optional[str] = Field(
        description="Associated job ID", default=None
    )
