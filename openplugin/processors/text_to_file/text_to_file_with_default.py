import os
from typing import Optional

from pydantic import Field

from openplugin.plugins.models import Config
from openplugin.plugins.port import Port, PortType, PortValueError
from openplugin.processors.text_to_file.text_to_file import TextToFile


class TextToFileWithDefault(TextToFile):
    file_type: str = Field("txt")
    file_name: str = Field("response")
    folder_name: str = Field("assets")

    async def process_input(self, input: Port, config: Optional[Config] = None) -> Port:
        if input.value is None:
            raise PortValueError("Input value cannot be None")
        if not os.path.exists(self.folder_name):
            os.makedirs(self.folder_name)
        output_file_name = f"{self.folder_name}/{self.file_name}.{self.file_type}"
        with open(output_file_name, "w") as file:
            file.write(input.value)
        return Port(data_type=PortType.FILEPATH, value=output_file_name)
