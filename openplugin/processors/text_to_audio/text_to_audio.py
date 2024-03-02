from abc import abstractmethod
from typing import Optional

from openplugin.core import Config, Port, PortType, PortValueError

from ..processor import (
    InvalidInputPortError,
    InvalidOutputPortError,
    Processor,
)


class TextToAudio(Processor):
    name: str = "Text To Audio"
    description: str = "Converts text to audio"

    async def validate_input_port(self, input: Port) -> bool:
        if input.data_type != PortType.TEXT:
            raise InvalidInputPortError("Input data type must be Text")
        if input.value is None:
            raise PortValueError("Input value cannot be None")
        return True

    async def validate_output_port(self, output: Port) -> bool:
        if output.data_type != PortType.FILEPATH:
            raise InvalidOutputPortError("Output data type must be Filepath")
        if output.value is None:
            raise PortValueError("Output value cannot be None")
        return True

    @abstractmethod
    async def process_input(self, input: Port, config: Optional[Config] = None) -> Port:
        pass

    def __str__(self):
        return f"name= {self.name}"
