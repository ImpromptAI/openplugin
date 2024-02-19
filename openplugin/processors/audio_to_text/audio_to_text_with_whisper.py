from openai import OpenAI

from openplugin.plugins.port import Port, PortType
from openplugin.processors.audio_to_text.audio_to_text import AudioToText


class AudioToTextWithWhisper(AudioToText):
    openai_api_key: str
    model_name: str = "whisper-1"

    def process_input(self, input: Port) -> Port:
        client = OpenAI()
        audio_file = open(input.value, "rb")
        transcript = client.audio.translations.create(
            model=self.model_name, file=audio_file
        )
        return Port(
            data_type=PortType.TEXT,
            value=transcript,
        )
