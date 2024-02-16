from abc import abstractmethod

from openplugin.plugins.port import Port, PortType
from openplugin.processors import Processor


class TextToFile(Processor):
    name: str = "Text To File"
    description: str = "Converts text to file"

    def validate_input_port(self, input: Port) -> bool:
        if input.data_type != PortType.TEXT:
            raise ValueError("Input data type must be text")
        return True

    def validate_output_port(self, output: Port) -> bool:
        if output.data_type != PortType.FILEPATH:
            raise ValueError("Output data type must be text")
        return True

    @abstractmethod
    def process_input(self, input: Port) -> Port:
        pass

    def __str__(self):
        return f"name= {self.name}"
