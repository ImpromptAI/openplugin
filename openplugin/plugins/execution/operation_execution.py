from abc import ABC, abstractmethod

from openplugin.plugins.models import (
    OperationExecutionParams,
    OperationExecutionResponse,
)


class OperationExecution(ABC):
    """Abstract base class for operation execution."""

    def __init__(self, params: OperationExecutionParams):
        self.params = params

    @abstractmethod
    def run(self) -> OperationExecutionResponse:
        pass
