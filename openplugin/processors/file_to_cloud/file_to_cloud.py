from abc import abstractmethod

from openplugin.plugins.port import Port, PortType
from openplugin.processors.processor import Processor


class FileToCloud(Processor):
    name: str = "File to Cloud Storage"
    description: str = "Uploads file to cloud storage"

    def validate_input_port(self, input: Port) -> bool:
        if input.data_type not in [PortType.FILEPATH, PortType.TEXT]:
            raise ValueError("Input data type must be String")
        return True

    def validate_output_port(self, output: Port) -> bool:
        if output.data_type != PortType.FILEPATH:
            raise ValueError("Output data type must be String")
        return True

    @abstractmethod
    def process_input(self, input: Port) -> Port:
        pass
