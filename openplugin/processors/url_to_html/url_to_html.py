from abc import abstractmethod
from typing import Optional

from openplugin.plugins.models import Config
from openplugin.plugins.port import Port, PortType, PortValueError
from openplugin.processors import (
    InvalidInputPortError,
    InvalidOutputPortError,
    Processor,
)


class UrlToHtml(Processor):
    name: str = "Url to html"
    description: str = "Converts a URL to HTML."

    async def validate_input_port(self, input: Port) -> bool:
        if input.data_type not in [PortType.HTTPURL]:
            raise InvalidInputPortError("Input data type must be HTTPURL")
        if input.value is None:
            raise PortValueError("Input value cannot be None")
        return True

    async def validate_output_port(self, output: Port) -> bool:
        if output.data_type != PortType.HTML:
            raise InvalidOutputPortError("Output data type must be HTML")
        if output.value is None:
            raise PortValueError("Output value cannot be None")
        return True

    @abstractmethod
    async def process_input(self, input: Port, config: Optional[Config] = None) -> Port:
        pass
