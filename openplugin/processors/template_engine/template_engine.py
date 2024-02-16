from abc import abstractmethod

from openplugin.plugins.port import Port, PortType
from openplugin.processors import Processor


class TemplateEngine(Processor):
    name: str = "Template Engine"
    description: str = "Converts"

    def validate_input_port(self, input: Port) -> bool:
        if input.data_type not in [PortType.TEXT, PortType.JSON]:
            raise ValueError("Invalid input data type")
        return True

    def validate_output_port(self, output: Port) -> bool:
        if output.data_type not in [PortType.TEXT, PortType.JSON]:
            raise ValueError("Invalid output data type")
        return True

    @abstractmethod
    def process_input(self, input: Port) -> Port:
        pass

    def __str__(self):
        return f"name= {self.name}"
