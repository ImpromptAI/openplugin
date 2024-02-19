import base64
from xml.sax.saxutils import escape

import azure.cognitiveservices.speech as speechsdk
from pydantic import Field

from openplugin.plugins.port import Port, PortType
from openplugin.processors.text_to_audio.text_to_audio import TextToAudio


class TextToAudioWithAzure(TextToAudio):
    voice_name: str = Field("en-US-AriaNeural")
    azure_region: str = Field("eastus")
    azure_endpoint_api_key: str = Field(...)
    output_filename: str = Field("output.mp3")

    def process_input(self, input: Port) -> Port:
        text = input.value
        if self.voice_name == "en-US-JasonCustomNeural":
            speech_config = speechsdk.SpeechConfig(
                subscription=self.azure_endpoint_api_key, region=self.azure_region
            )
            speech_synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=speech_config, audio_config=None
            )
            text = escape(text)
            ssml = f'<speak xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" xmlns:emo="http://www.w3.org/2009/10/emotionml" version="1.0" xml:lang="en-US"><voice name="en-US-JasonNeural"><prosody rate="18%" pitch="-4%">{text}</prosody></voice></speak>'  # noqa: E501
            result = speech_synthesizer.speak_ssml_async(ssml).get()
            audio = base64.b64encode(result.audio_data)
            audio_data = f'data:audio/mpeg;base64, {audio.decode("utf-8")}'
        else:
            speech_config = speechsdk.SpeechConfig(
                subscription=self.azure_endpoint_api_key, region=self.azure_region
            )
            speech_config.speech_synthesis_voice_name = self.voice_name

            speech_synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=speech_config, audio_config=None
            )
            result = speech_synthesizer.speak_text(text)
            audio = base64.b64encode(result.audio_data)
            audio_data = f'data:audio/mpeg;base64, {audio.decode("utf-8")}'
        with open(self.output_filename, "wb") as file:
            file.write(base64.b64decode(audio_data.split(",")[1]))
        return Port(data_type=PortType.FILEPATH, value=self.output_filename)
