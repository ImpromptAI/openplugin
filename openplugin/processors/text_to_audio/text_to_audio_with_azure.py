import base64
import os
from typing import Optional
from xml.sax.saxutils import escape

import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv
from pydantic import Field, validator

from openplugin.plugins.models import Config
from openplugin.plugins.port import Port, PortType, PortValueError
from openplugin.processors.text_to_audio.text_to_audio import TextToAudio

load_dotenv()


class TextToAudioWithAzure(TextToAudio):
    voice_name: str = Field("en-US-AriaNeural")
    azure_region: str = Field("eastus")
    azure_api_key: Optional[str] = Field(None)
    output_filename: str = Field("output.mp3")
    output_folder: str = Field("assets")

    @validator("azure_api_key")
    def check_azure_api_key(cls, v):
        if not v:
            v = os.environ.get("AZURE_API_KEY")
        if v and v.startswith("env."):
            v = os.environ.get(v.split("env.")[1])
        return v

    async def process_input(self, input: Port, config: Optional[Config] = None) -> Port:
        if config and config.azure_api_key:
            self.azure_api_key = config.azure_api_key
        if input.value is None:
            raise PortValueError("Input value cannot be None")
        text = input.value
        if self.voice_name == "en-US-JasonCustomNeural":
            speech_config = speechsdk.SpeechConfig(
                subscription=self.azure_api_key, region=self.azure_region
            )
            speech_synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=speech_config, audio_config=None
            )
            text = escape(text)
            ssml = f'<speak xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" xmlns:emo="http://www.w3.org/2009/10/emotionml" version="1.0" xml:lang="en-US"><voice name="en-US-JasonNeural"><prosody rate="18%" pitch="-4%">{text}</prosody></voice></speak>'  # noqa: E501
            result = speech_synthesizer.speak_ssml_async(ssml).get()
        else:
            speech_config = speechsdk.SpeechConfig(
                subscription=self.azure_api_key, region=self.azure_region
            )
            speech_config.speech_synthesis_voice_name = self.voice_name
            speech_synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=speech_config, audio_config=None
            )
            result = speech_synthesizer.speak_text(text)
        if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
            raise Exception(f"{result.reason}")
        audio = base64.b64encode(result.audio_data)
        audio_data = f'data:audio/mpeg;base64, {audio.decode("utf-8")}'
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
        output_file_loc = f"{self.output_folder}/{self.output_filename}"
        with open(output_file_loc, "wb") as file:
            file.write(base64.b64decode(audio_data.split(",")[1]))
        return Port(data_type=PortType.FILEPATH, value=output_file_loc)
