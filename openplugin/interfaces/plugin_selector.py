import requests
from enum import Enum
from abc import ABC, abstractmethod
from typing import List, Optional, Set, Dict
from pydantic import BaseModel, validator, root_validator
import json, yaml
from pydantic.json import pydantic_encoder


class PluginAuth(BaseModel):
    type: Optional[str]
    authorization_type: Optional[str]
    verification_tokens: Optional[Dict]
    scope: Optional[str]
    client_url: Optional[str]
    authorization_url: Optional[str]
    authorization_content_type: Optional[str]
    token_validation_url: Optional[str]


class PluginOperation(BaseModel):
    """
    Represents the result of a plugin operation.
    """
    human_usage_examples: Optional[List[str]] = []
    prompt_helpers: Optional[List[str]] = []


class Plugin(BaseModel):
    """
    Represents a plugin configuration.
    """
    manifest_url: str
    schema_version: Optional[str]
    name: Optional[str]
    description: Optional[str]
    openapi_doc_url: Optional[str]
    auth: Optional[PluginAuth]
    logo_url: Optional[str]
    contact_email: Optional[str]
    legal_info_url: Optional[str]
    api_endpoints: Optional[Set[str]] = None
    # first str is the path, second str is the method
    plugin_operations: Optional[Dict[str, Dict[str, PluginOperation]]] = None

    @staticmethod
    def build_from_manifest_url(manifest_url: str):
        manifest_obj = requests.get(manifest_url).json()
        values = {}
        for key in manifest_obj.keys():
            if key not in values.keys():
                values[key] = manifest_obj[key]
            if values.get("openapi_doc_url") is None:
                raise ValueError("Incompatible manifest.")
            openapi_doc_json = requests.get(values.get("openapi_doc_url")).json()
            if openapi_doc_json:
                server_url = openapi_doc_json.get("servers")[0].get("url")
                api_endpoints = []
                paths = openapi_doc_json.get("paths")
                for key in paths:
                    api_endpoints.append(f"{server_url}{key}")
                values["api_endpoints"] = api_endpoints
            else:
                raise ValueError("Incompatible manifest.")
        return Plugin(**values)

    def get_openapi_doc_json(self):
        return requests.get(self.openapi_doc_url).json()

    @root_validator(pre=True)
    def _set_fields(cls, values: dict) -> dict:
        """This is a validator that sets the field values based on the manifest_url"""
        if values.get("manifest_url"):
            manifest_obj = requests.get(values.get("manifest_url")).json()
            for key in manifest_obj.keys():
                if key not in values.keys():
                    values[key] = manifest_obj[key]
            if values.get("openapi_doc_url") is None:
                raise ValueError("Incompatible manifest.")
            openapi_doc_json = requests.get(values.get("openapi_doc_url")).json()
            if openapi_doc_json:
                server_url = openapi_doc_json.get("servers")[0].get("url")
                api_endpoints = []
                paths = openapi_doc_json.get("paths")
                for key in paths:
                    api_endpoints.append(f"{server_url}{key}")
                values["api_endpoints"] = api_endpoints
            else:
                raise ValueError("Incompatible manifest.")
        return values

    def has_api_endpoint(self, endpoint) -> bool:
        if endpoint in self.api_endpoints:
            return True
        return False

    def get_manifest_dict(self):
        j = self.dict(exclude={"api_endpoints", "manifest_url", "auth"})
        j["auth"] = self.auth.dict(exclude_none=True)
        return j

    def get_manifest_json(self):
        return json.dumps(self.get_manifest_dict())

    def get_manifest_yaml(self):
        return yaml.dump(self.get_manifest_dict())

    def get_plugin_pre_prompts(self):
        pre_prompt = ""
        index = 1
        if self.plugin_operations:
            for value in self.plugin_operations.values():
                for val in value.values():
                    for helper in val.prompt_helpers:
                        pre_prompt += f"{index}: {helper}\n"
                        index = index + 1
                    for example in val.human_usage_examples:
                        pre_prompt += f"{index}: {example}\n"
                        index = index + 1
        if index > 1:
            pre_prompt = f"For plugin: {self.name}:\n" + pre_prompt
        return pre_prompt.strip()


class PluginDetected(BaseModel):
    """
    Represents the result of a plugin operation.
    """
    plugin: Plugin
    api_called: Optional[str]
    method: Optional[str]
    mapped_operation_parameters: Optional[Dict[str, str]] = None


class Config(BaseModel):
    """
    Represents the API configuration for a plugin.
    """
    openai_api_key: Optional[str]
    cohere_api_key: Optional[str]


class FunctionProperty(BaseModel):
    name: str
    type: str
    description: Optional[str]
    enum: Optional[List[str]]
    is_required: bool = False


class API(BaseModel):
    url: str
    method: str

    def call(self, params):
        if self.method.lower() == "get":
            response = requests.request(self.method.upper(), self.url, params=params,
                                        headers={})
        else:
            response = requests.request(self.method.upper(), self.url, data=params,
                                        headers={})
        return response.json()


class Function(BaseModel):
    name: Optional[str]
    api: Optional[API]
    description: Optional[str]
    param_type: Optional[str]
    param_properties: Optional[List[FunctionProperty]]
    human_usage_examples: Optional[List[str]] = []
    prompt_helpers: Optional[List[str]] = []

    def get_api_url(self):
        return self.api.url

    def get_api_method(self):
        return self.api.method

    def call_api(self, params):
        return self.api.call(params)

    def get_required_properties(self):
        return [param_property.name for param_property in self.param_properties if
                param_property.is_required]

    def get_property_map(self):
        map = {}
        for param_property in self.param_properties:
            obj = {
                "type": param_property.type,
                "description": param_property.description,
            }
            if param_property.enum:
                obj["enum"] = param_property.enum
            map[param_property.name] = obj
        return map

    def get_openai_function_json(self):
        json = {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": self.param_type,
                "properties": self.get_property_map(),
                "required": self.get_required_properties()
            }

        }
        return json


class Functions(BaseModel):
    functions: List[Function] = []
    plugin_map: dict = {}
    function_map: dict = {}

    def get_json(self):
        json = []
        for function in self.functions:
            json.append(function.get_openai_function_json())
        return json

    def get_plugin_from_func_name(self, function_name):
        return self.plugin_map.get(function_name)

    def get_function_from_func_name(self, function_name):
        return self.function_map.get(function_name)

    def add_from_plugin(self, plugin: Plugin):
        self.add_from_manifest(plugin.manifest_url, plugin)

    def add_from_manifest(self, manifest_url: str, plugin: Plugin = None):
        manifest_obj = requests.get(manifest_url).json()
        open_api_spec_url = manifest_obj.get("openapi_doc_url")
        self.add_from_openapi_spec(open_api_spec_url, plugin=plugin,
                                   plugin_operations_map=manifest_obj.get(
                                       "plugin_operations"))

    def get_helper_pre_prompt(self):
        prompt = ""
        index=1
        for function in self.functions:
            for helper in function.prompt_helpers:
                prompt += f"prompt helper= {helper} \n"
                index = index + 1
            for example in function.human_usage_examples:
                prompt += f"example= {example} \n"
                index = index + 1
        return prompt.strip()

    def add_from_openapi_spec(self, open_api_spec_url: str, plugin: Plugin = None,
                              header: dict = None, plugin_operations_map: dict = None):
        openapi_doc_json = requests.get(open_api_spec_url).json()
        if openapi_doc_json is None:
            return ValueError("Could not get OpenAPI spec from URL")
        server_url = openapi_doc_json.get("servers")[0].get("url")
        api_endpoints = []
        paths = openapi_doc_json.get("paths")
        functions = []
        for path in paths:
            api_endpoints.append(f"{server_url}{path}")
            for method in paths[path]:
                details = paths[path][method]
                function_values = {}
                function_values["api"] = API(url=f"{server_url}{path}", method=method,
                                             header=header)
                function_values["name"] = f"{method}{path.replace('/', '_')}"
                function_values["description"] = details.get("summary")
                function_values["param_type"] = "object"
                properties = []
                if method.lower() == "get":
                    for param in details.get("parameters"):
                        properties_values = {}
                        properties_values["name"] = param.get("name")
                        properties_values["type"] = param.get("schema").get("type")
                        properties_values["description"] = param.get("description")
                        properties_values["is_required"] = param.get("required")
                        properties.append(FunctionProperty(**properties_values))
                elif method.lower() == "post" or method.lower() == "put":
                    application_json_schema = details.get("requestBody").get(
                        "content").get("application/json").get("schema")
                    params = []
                    required_params = {}
                    if "properties" in application_json_schema:
                        params = application_json_schema.get("properties")
                        required_params = application_json_schema.get("required", {})
                    elif "$ref" in application_json_schema:
                        ref = application_json_schema.get("$ref")
                        ref = ref.replace("#/components/schemas/", "")
                        params = openapi_doc_json.get("components").get("schemas").get(
                            ref).get("properties")
                        required_params = openapi_doc_json.get("components").get(
                            "schemas").get(
                            ref).get("required", {})
                    for param in params:
                        properties_values = {}
                        properties_values["name"] = param
                        properties_values["type"] = params.get(param).get("type")
                        properties_values["description"] = params.get(param).get(
                            "description")
                        if param in required_params:
                            properties_values["is_required"] = True
                        else:
                            properties_values["is_required"] = False
                        properties.append(properties_values)
                function_values["param_properties"] = properties
                human_usage_examples = plugin_operations_map.get(path, {}).get(method,
                                                                               {}).get(
                    "human_usage_examples", [])
                function_values["human_usage_examples"] = human_usage_examples
                prompt_helpers = plugin_operations_map.get(path, {}).get(method,
                                                                         {}).get(
                    "prompt_helpers", [])
                function_values["prompt_helpers"] = prompt_helpers
                func = Function(**function_values)
                if plugin:
                    self.plugin_map[func.name] = plugin
                self.function_map[func.name] = func
                functions.append(func)
        self.functions.extend(functions)


class LLMProvider(str, Enum):
    """
    Enumeration for different LLM providers.
    """
    OpenAI = "OpenAI"
    OpenAIChat = "OpenAIChat"
    GooglePalm = "GooglePalm"
    Cohere = "Cohere"


class LLM(BaseModel):
    """
    Represents the configuration for an LLM (Language Model) provider.
    """
    provider: LLMProvider
    model_name: str
    temperature: float = 0.7
    max_tokens: int = 1024
    top_p: float = 1
    frequency_penalty: float = 0
    presence_penalty: float = 0
    n: float = 1
    best_of: float = 1
    max_retries: int = 6

    @validator("model_name")
    def _chk_model_name(cls, model_name: str, values, **kwargs) -> str:
        is_correct_model_name = False
        if values['provider'] == LLMProvider.OpenAI and model_name in [
            "text-davinci-003"]:
            is_correct_model_name = True
        if values['provider'] == LLMProvider.OpenAIChat and model_name in [
            "gpt-3.5-turbo", "gpt-3.5-turbo-0613", "gpt-4-0613" "gpt-4"]:
            is_correct_model_name = True
        if values['provider'] == LLMProvider.GooglePalm and model_name in [
            "text-bison-001", "chat-bison@001"]:
            is_correct_model_name = True
        if values['provider'] == LLMProvider.Cohere and model_name in [
            "command", "command-light", "command-xlarge-nightly"]:
            is_correct_model_name = True
        if not is_correct_model_name:
            raise ValueError(
                f"model_name {model_name} not supported for provider {values['provider']}")
        return model_name


class ToolSelectorProvider(str, Enum):
    """
    Enumeration for different Tool Selector providers.
    """

    Langchain = "Langchain"
    Imprompt = "Imprompt"
    OpenAI = "OpenAI"


class ToolSelectorConfig(BaseModel):
    """
    Represents the configuration for a Tool Selector.
    """
    provider: ToolSelectorProvider
    pipeline_name: str


class Response(BaseModel):
    """
    Represents the response from executing prompts.
    """
    run_completed: bool
    final_text_response: Optional[str]
    detected_plugin_operations: Optional[List[PluginDetected]]
    response_time: Optional[float]
    tokens_used: Optional[int]
    llm_api_cost: Optional[float]


class MessageType(str, Enum):
    HumanMessage = "HumanMessage"
    AIMessage = "AIMessage"
    SystemMessage = "SystemMessage"
    FunctionMessage = "FunctionMessage"


class Message(BaseModel):
    """
    Represents a prompt to be executed.
    """
    content: str
    message_type: MessageType

    def get_openai_message(self):
        if self.message_type == MessageType.HumanMessage:
            return {"role": "user", "content": self.content}
        elif self.message_type == MessageType.AIMessage:
            return {"role": "assistant", "content": self.content}
        elif self.message_type == MessageType.SystemMessage:
            return {"role": "system", "content": self.content}


class PluginSelector(ABC):
    """Abstract base class for plugin selectors."""

    def __init__(
            self,
            tool_selector_config: ToolSelectorConfig,
            plugins: List[Plugin],
            config: Optional[Config],
            llm: Optional[LLM]
    ):
        """
        Initialize the plugin selector.
        Args:
            tool_selector_config (ToolSelectorConfig): Configuration for the tool selector.
            plugins (List[Plugin]): List of plugins to be used by the plugin selector.
            config (Optional[Config]): Additional configuration for the plugin selector.
            llm (Optional[LLM]): Additional language model for the plugin selector.
        """
        self.plugins = plugins
        self.llm = llm
        self.initialize_tool_selector(tool_selector_config, plugins, config, llm)

    def get_plugin_by_name(self, name: str):
        for plugin in self.plugins:
            if plugin.name == name:
                return plugin
        return None

    @abstractmethod
    def initialize_tool_selector(
            self,
            tool_selector_config: ToolSelectorConfig,
            plugins: Optional[List[Plugin]],
            config: Optional[Config],
            llm: Optional[LLM],
    ):
        """
        Initialize the plugin selector with the provided configuration.
        This method should be implemented by the derived classes.
        Args:
            tool_selector_config (ToolSelectorConfig): Configuration for the plugin selector.
            plugins (Optional[List[Plugin]]): List of plugins to be used by the plugin selector.
            config (Optional[Config]): Additional configuration for the plugin selector.
            llm (Optional[LLM]): Additional language model for the plugin selector.
        """
        pass

    @abstractmethod
    def run(
            self,
            messages: List[Message]
    ) -> Response:
        """
        Run the plugin selector on the given list of messages and return a response.
        This method should be implemented by the derived classes.
        Args:
            messages (List[Message]): List of messages to be processed by the plugin selector.
        Returns:
            Response: The response generated by the plugin selector.
        """
        pass
