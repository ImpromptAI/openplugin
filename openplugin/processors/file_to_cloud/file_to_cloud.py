from abc import abstractmethod
from typing import Optional

from openplugin.plugins.models import Config
from openplugin.plugins.port import Port, PortType, PortValueError
from openplugin.processors import (
    InvalidInputPortError,
    InvalidOutputPortError,
    Processor,
)


class FileToCloud(Processor):
    name: str = "File to Cloud Storage"
    description: str = "Uploads file to cloud storage"

    async def validate_input_port(self, input: Port) -> bool:
        if input.data_type not in [PortType.FILEPATH, PortType.TEXT]:
            raise InvalidInputPortError("Input data type must be Filepath or Text")
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
