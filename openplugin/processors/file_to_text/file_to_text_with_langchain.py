import os

from langchain_community.document_loaders import TextLoader

from openplugin.plugins.port import Port, PortType
from openplugin.processors.file_to_text.file_to_text import FileToText


class FileToTextWithLangchain(FileToText):
    def process_input(self, input: Port) -> Port:
        if not os.path.isfile(input.value):
            raise ValueError(f"File not found: {input.value}")
        loader = TextLoader(input.value)
        docs = loader.load()
        return Port(data_type=PortType.TEXT, value=docs[0].page_content)
