from abc import abstractmethod

from openplugin.plugins.port import Port, PortType
from openplugin.processors.processor import Processor


class UrlToHtml(Processor):
    name: str = "Url to html"
    description: str = "Converts a URL to HTML."

    def validate_input_port(self, input: Port) -> bool:
        if input.data_type not in [PortType.HTTPURL]:
            raise ValueError("Input data type must be HTTPURL")
        return True

    def validate_output_port(self, output: Port) -> bool:
        if output.data_type != PortType.HTML:
            raise ValueError("Output data type must be HTML")
        return True

    @abstractmethod
    def process_input(self, input: Port) -> Port:
        pass
