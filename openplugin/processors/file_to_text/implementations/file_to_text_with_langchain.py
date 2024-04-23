import os, requests, uuid
from typing import Optional

from langchain_community.document_loaders import TextLoader

from openplugin.core import Config, Port, PortType, PortValueError

from ..file_to_text import FileToText
from openplugin.utils.helpers import is_url

class FileToTextWithLangchain(FileToText):
    async def process_input(self, input: Port, config: Optional[Config] = None) -> Port:
        if input.value is None:
            raise PortValueError("Input value cannot be None")
        if input.data_type == PortType.FILEPATH:
            if not os.path.isfile(input.value):
                raise ValueError(f"File not found: {input.value}")
            loader = TextLoader(input.value)
            docs = loader.load()
            return Port(data_type=PortType.TEXT, value=docs[0].page_content)
        elif input.data_type == PortType.FILE and input.mime_types:
            if type(input.value) is str and is_url(input.value):
                mime_type_str=input.mime_types[0].value.split("/")[1]
                if mime_type_str=="plain":
                    mime_type_str="txt"
                filename=f'assets/{str(uuid.uuid4())}.{mime_type_str}'
                response = requests.get(input.value, stream=True)
                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024): 
                        if chunk: # filter out keep-alive new chunks
                            f.write(chunk)
                loader = TextLoader(filename)
                docs = loader.load()
                os.remove(filename)
                return Port(data_type=PortType.TEXT, value=docs[0].page_content)
            else:
                decoded_value = input.value.decode("utf-8")
                return Port(data_type=PortType.TEXT, value=decoded_value)
        elif input.data_type == PortType.REMOTE_FILE_URL:
            response = requests.get(input.value)
            return Port(data_type=PortType.TEXT, value=response.content)
        else:
            raise ValueError(f"Invalid input data type: {input.data_type}")
   
