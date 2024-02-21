from enum import Enum
from typing import Any, Optional

from pydantic import BaseConfig, BaseModel


class Config(BaseModel):
    """
    Represents the API configuration for a plugin.
    """

    provider: str = "openai"
    openai_api_key: Optional[str] = None
    cohere_api_key: Optional[str] = None
    google_palm_key: Optional[str] = None
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region_name: Optional[str] = None
    azure_api_key: Optional[str] = None


class LLM(BaseModel):
    """
    Represents the configuration for an LLM (Language Model) provider.
    """

    provider: str
    model_name: str
    temperature: float = 0
    max_tokens: int = 2048
    top_p: float = 1
    frequency_penalty: float = 0
    presence_penalty: float = 0
    n: int = 1
    best_of: int = 1
    max_retries: int = 6

    class Config(BaseConfig):
        # Set protected_namespaces to an empty tuple to resolve the conflict
        protected_namespaces = ()


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


class OperationExecutionParams(BaseModel):
    config: Config
    api: str
    method: str
    query_params: Optional[dict]
    body: Optional[dict]
    header: Optional[dict]
    post_processing_cleanup_prompt: Optional[str]
    llm: Optional[LLM]
    plugin_response_template_engine: Optional[str]
    plugin_response_template: Optional[str]
    post_call_evaluator_prompt: Optional[str]

    def get_temperature(self):
        if self.llm:
            return self.llm.temperature
        return None

    def get_top_p(self):
        if self.llm:
            return self.llm.top_p
        return None

    def get_max_tokens(self):
        if self.llm:
            return self.llm.max_tokens
        return None

    def get_frequency_penalty(self):
        if self.llm:
            return self.llm.frequency_penalty
        return None

    def get_presence_penalty(self):
        if self.llm:
            return self.llm.presence_penalty
        return None


class OperationExecutionResponse(BaseModel):
    original_response: Optional[Any]
    cleanup_response: Optional[str]
    template_response: Optional[str]
    summary_response: Optional[str]
    clarifying_response: Optional[str]
    is_a_clarifying_question: Optional[bool] = False
    api_call_status_code: Optional[int]
    api_call_response_seconds: Optional[float]
    template_execution_status_code: Optional[str]
    template_execution_response_seconds: Optional[float]
    cleanup_helper_status_code: Optional[str]
    cleanup_helper_response_seconds: Optional[float]
    summary_response_status_code: Optional[str]
    summary_response_seconds: Optional[float]
    clarifying_question_status_code: Optional[str]
    clarifying_question_response_seconds: Optional[float]
    llm_calls: Optional[Any]


class PreferredApproach(BaseModel):
    base_strategy: str
    name: str
    pre_prompt: Optional[str]
    llm: Optional[LLM]
