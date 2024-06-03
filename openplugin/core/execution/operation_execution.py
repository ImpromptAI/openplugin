from abc import ABC, abstractmethod
from typing import Any, Optional

from pydantic import BaseModel

from ..config import Config
from ..function_providers import FunctionProvider


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
    function_provider: FunctionProvider

    def get_temperature(self):
        return 0.2

    def get_top_p(self):
        return None

    def get_max_tokens(self):
        return None

    def get_frequency_penalty(self):
        return None

    def get_presence_penalty(self):
        return None


class OperationExecution(ABC):
    """Abstract base class for operation execution."""

    def __init__(self, params: OperationExecutionParams):
        self.params = params

    @abstractmethod
    def run(self) -> OperationExecutionResponse:
        pass
