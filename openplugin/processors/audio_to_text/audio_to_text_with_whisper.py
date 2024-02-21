from typing import Optional

from openai import OpenAI

from openplugin.plugins.models import Config
from openplugin.plugins.port import Port, PortType, PortValueError
from openplugin.processors.audio_to_text.audio_to_text import AudioToText


class AudioToTextWithWhisper(AudioToText):
    openai_api_key: str
    model_name: str = "whisper-1"

    async def process_input(self, input: Port, config: Optional[Config] = None) -> Port:
        if input.value is None:
            raise PortValueError("Input value cannot be None")
        client = OpenAI()
        audio_file = open(input.value, "rb")
        transcript = client.audio.translations.create(
            model=self.model_name, file=audio_file
        )
        return Port(
            data_type=PortType.TEXT,
            value=transcript,
        )
