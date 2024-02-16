from abc import abstractmethod

from openplugin.plugins.port import Port, PortType
from openplugin.processors.processor import Processor


class AudioToText(Processor):
    name: str = "Audio to Text"
    description: str = "Converts audio to text"

    def validate_input_port(self, input: Port) -> bool:
        if input.data_type != PortType.TEXT:
            raise ValueError("Input data type must be String")
        return True

    def validate_output_port(self, output: Port) -> bool:
        if output.data_type != PortType.TEXT:
            raise ValueError("Output data type must be String")
        return True

    @abstractmethod
    def process_input(self, input: Port) -> Port:
        pass
