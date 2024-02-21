import os
from typing import Optional

from langchain_community.document_loaders import TextLoader

from openplugin.plugins.models import Config
from openplugin.plugins.port import Port, PortType, PortValueError
from openplugin.processors.file_to_text.file_to_text import FileToText


class FileToTextWithLangchain(FileToText):
    async def process_input(self, input: Port, config: Optional[Config] = None) -> Port:
        if input.value is None:
            raise PortValueError("Input value cannot be None")

        if not os.path.isfile(input.value):
            raise ValueError(f"File not found: {input.value}")
        loader = TextLoader(input.value)
        docs = loader.load()
        return Port(data_type=PortType.TEXT, value=docs[0].page_content)
