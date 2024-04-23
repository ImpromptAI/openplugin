from abc import abstractmethod
from typing import Optional

from openplugin.core import Config, Port, PortType, PortValueError

from ..processor import (
    InvalidInputPortError,
    InvalidOutputPortError,
    Processor,
)


class AudioToText(Processor):
    name: str = "Audio to Text"
    description: str = "Converts audio to text"

    async def validate_input_port(self, input: Port) -> bool:
        if input.data_type not in [PortType.FILEPATH, PortType.FILE]:
            raise InvalidInputPortError("Input data type must be Filepath")
        if input.value is None:
            raise PortValueError("Input value cannot be None")
        return True

    async def validate_output_port(self, output: Port) -> bool:
        if output.data_type != PortType.TEXT:
            raise InvalidOutputPortError("Output data type must be Text")
        if output.value is None:
            raise PortValueError("Output value cannot be None")
        return True

    @abstractmethod
    async def process_input(self, input: Port, config: Optional[Config] = None) -> Port:
        pass
