from abc import abstractmethod
from typing import Optional

from openplugin.plugins.models import Config
from openplugin.plugins.port import Port, PortType, PortValueError
from openplugin.processors import (
    InvalidInputPortError,
    InvalidOutputPortError,
    Processor,
)


class TemplateEngine(Processor):
    name: str = "Template Engine"
    description: str = "Converts"

    async def validate_input_port(self, input: Port) -> bool:
        if input.data_type not in [PortType.TEXT, PortType.JSON]:
            raise InvalidInputPortError("Input data type must be Text or JSON")
        if input.value is None:
            raise PortValueError("Input value cannot be None")
        return True

    async def validate_output_port(self, output: Port) -> bool:
        if output.data_type not in [PortType.TEXT, PortType.JSON]:
            raise InvalidOutputPortError("Output data type must be Text or JSON")
        if output.value is None:
            raise PortValueError("Output value cannot be None")
        return True

    @abstractmethod
    async def process_input(self, input: Port, config: Optional[Config] = None) -> Port:
        pass

    def __str__(self):
        return f"name= {self.name}"
