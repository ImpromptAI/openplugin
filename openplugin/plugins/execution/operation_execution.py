from abc import ABC, abstractmethod
from typing import Any, Optional

from pydantic import BaseModel

from openplugin.plugins.llms import LLM, Config


class OperationExecutionResponse(BaseModel):
    original_response: Optional[Any]
    clarifying_response: Optional[str]
    is_a_clarifying_question: Optional[bool] = False
    api_call_status_code: Optional[int]
    api_call_response_seconds: Optional[float]
    clarifying_question_status_code: Optional[str]
    clarifying_question_response_seconds: Optional[float]
    llm_calls: Optional[Any]


class OperationExecutionParams(BaseModel):
    config: Config
    api: str
    method: str
    query_params: Optional[dict]
    body: Optional[dict]
    header: Optional[dict]
    llm: Optional[LLM]

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


class OperationExecution(ABC):
    """Abstract base class for operation execution."""

    def __init__(self, params: OperationExecutionParams):
        self.params = params

    @abstractmethod
    def run(self) -> OperationExecutionResponse:
        pass
