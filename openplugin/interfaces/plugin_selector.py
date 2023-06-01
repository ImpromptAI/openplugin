import requests
from enum import Enum
from abc import ABC, abstractmethod
from typing import List, Optional, Set
from pydantic import BaseModel, validator, root_validator


class Config(BaseModel):
    """
    Represents the API configuration for a plugin.
    """
    openai_api_key: Optional[str]


class PluginAPI(BaseModel):
    """
    Represents the API configuration for a plugin.
    """
    type: str
    url: str
    has_user_authentication: Optional[bool] = False
    # openapi_doc_json: Optional[Dict] = None
    api_endpoints: Optional[Set[str]] = None

    @root_validator(pre=True)
    def _set_fields(cls, values: dict) -> dict:
        """This is a validator that sets the field values based on the manifest_url"""
        if values.get("url"):
            openapi_doc_json = requests.get(values.get("url")).json()
            if openapi_doc_json:
                # values["openapi_doc_json"] = openapi_doc_json
                server_url = openapi_doc_json.get("servers")[0].get("url")
                api_endpoints = []
                paths = openapi_doc_json.get("paths")
                for key in paths:
                    api_endpoints.append(f"{server_url}{key}")
                values["api_endpoints"] = api_endpoints
        return values

    def get_openapi_doc(self):
        return requests.get(self.url).json()


class Plugin(BaseModel):
    """
    Represents a plugin configuration.
    """
    schema_version: Optional[str]
    name_for_model: Optional[str]
    name_for_human: Optional[str]
    description_for_model: Optional[str]
    description_for_human: Optional[str]
    logo_url: Optional[str]
    contact_email: Optional[str]
    legal_info_url: Optional[str]
    manifest_url: str
    api: Optional[PluginAPI]

    @root_validator(pre=True)
    def _set_fields(cls, values: dict) -> dict:
        """This is a validator that sets the field values based on the manifest_url"""
        if values.get("manifest_url"):
            manifest_obj = requests.get(values.get("manifest_url")).json()
            for key in manifest_obj.keys():
                if key not in values.keys():
                    values[key] = manifest_obj[key]
        return values

    def has_api_endpoint(self, endpoint) -> bool:
        if endpoint in self.api.api_endpoints:
            return True
        return False


class PluginOperation(BaseModel):
    """
    Represents the result of a plugin operation.
    """
    plugin: Plugin
    # input_prompt: Optional[str]
    api_called: Optional[str]
    mapped_operation_parameters: Optional[dict]
    # plugin_response: Optional[str]


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
    max_tokens: int = 256
    top_p: float = 1
    frequency_penalty: float = 0
    presence_penalty: float = 0
    n: float = 1
    best_of: float = 1
    max_tokens: int = 1024
    max_retries: int = 6

    @validator("model_name")
    def _chk_model_name(cls, model_name: str, values, **kwargs) -> str:
        is_correct_model_name = False
        if values['provider'] == LLMProvider.OpenAI and model_name in ["text-davinci-003"]:
            is_correct_model_name = True
        if values['provider'] == LLMProvider.OpenAIChat and model_name in ["gpt-3.5-turbo"]:
            is_correct_model_name = True
        if values['provider'] == LLMProvider.GooglePalm and model_name in ["models/text-bison-001"]:
            is_correct_model_name = True
        if values['provider'] == LLMProvider.Cohere and model_name in ["models/text-bison-001"]:
            is_correct_model_name = True
        if not is_correct_model_name:
            raise ValueError(f"model_name {model_name} not supported for provider {values['provider']}")
        return model_name


class ToolSelectorProvider(str, Enum):
    """
    Enumeration for different Tool Selector providers.
    """

    Langchain = "Langchain"
    Imprompt = "Imprompt"


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
    detected_plugin_operations: Optional[List[PluginOperation]]
    response_time: Optional[float]
    tokens_used: Optional[int]
    llm_api_cost: Optional[float]


class MessageType(str, Enum):
    HumanMessage = "HumanMessage"
    AIMessage = "AIMessage"
    SystemMessage = "SystemMessage"


class Message(BaseModel):
    """
    Represents a prompt to be executed.
    """
    content: str
    message_type: MessageType


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
        self.agent = None
        self.plugins = plugins
        self.initialize_tool_selector(tool_selector_config, plugins, config, llm)

    def get_plugin_by_name(self, name: str):
        for plugin in self.plugins:
            if plugin.name_for_human == name or plugin.name_for_model == name:
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
