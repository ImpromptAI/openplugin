from pydantic import Field

from openplugin.plugins.port import Port, PortType
from openplugin.processors.text_to_file.text_to_file import TextToFile


class TextToFileWithDefault(TextToFile):
    file_type: str = Field("txt")
    file_name: str = Field("response")

    def process_input(self, input: Port) -> Port:
        output_file_name = f"{self.file_name}.{self.file_type}"
        with open(output_file_name, "w") as file:
            file.write(input.value)
        return Port(data_type=PortType.FILEPATH, value=output_file_name)
