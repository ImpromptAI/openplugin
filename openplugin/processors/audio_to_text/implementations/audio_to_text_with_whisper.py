from typing import Optional

from openai import OpenAI
import os, uuid, requests
from openplugin.core import Config, Port, PortType, PortValueError

from ..audio_to_text import AudioToText
from openplugin.utils.helpers import is_url

class AudioToTextWithWhisper(AudioToText):
    openai_api_key: str
    model_name: str = "whisper-1"

    async def process_input(self, input: Port, config: Optional[Config] = None) -> Port:
        if input.value is None:
            raise PortValueError("Input value cannot be None")
        if input.data_type==PortType.FILEPATH:
            client = OpenAI()
            audio_file = open(input.value, "rb")
            transcript = client.audio.translations.create(
                model=self.model_name, file=audio_file
            )
            return Port(
                data_type=PortType.TEXT,
                value=transcript,
            )
        elif input.data_type==PortType.FILE and input.mime_types:
            if type(input.value) is str and is_url(input.value):
                mime_type_str=input.mime_types[0].value.split("/")[1]
                # mpeg is not supported by openai
                if mime_type_str =="mpeg":
                    mime_type_str="mp3"
                filename=f'assets/{str(uuid.uuid4())}.{mime_type_str}'

                response = requests.get(input.value, stream=True)
                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024): 
                        if chunk: # filter out keep-alive new chunks
                            f.write(chunk)
                client = OpenAI()
                audio_file = open(filename, "rb")
                transcript = client.audio.translations.create(
                    model=self.model_name, file=audio_file
                )
                os.remove(filename)
                return Port(
                    data_type=PortType.TEXT,
                    value=transcript.text,
                )
            else:
                mime_type_str=input.mime_types[0].value.split("/")[1]
                # mpeg is not supported by openai
                if mime_type_str =="mpeg":
                    mime_type_str="mp3"
                filename=f'assets/{str(uuid.uuid4())}.{mime_type_str}'
                with open(filename, 'wb') as file:
                    file.write(input.value)
                client = OpenAI()
                audio_file = open(filename, "rb")
                transcript = client.audio.translations.create(
                    model=self.model_name, file=audio_file
                )
                os.remove(filename)
                return Port(
                    data_type=PortType.TEXT,
                    value=transcript.text,
                )
        else:
            raise ValueError(f"Invalid input data type: {input.data_type}")
