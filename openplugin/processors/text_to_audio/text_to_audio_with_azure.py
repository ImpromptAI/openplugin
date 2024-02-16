import json, requests
import re
import base64
from pydantic import Field

from openplugin.plugins.port import Port, PortType
from openplugin.processors.text_to_audio.text_to_audio import TextToAudio


class TextToAudioWithAzure(TextToAudio):
    voice: str = Field("en-US-AriaNeural")
    endpoint: str = Field(
        "https://api.brandops.io/content-scraping/api/azure-text-to-speech"
    )
    azure_endpoint_api_key: str = Field(...)

    def process_input(self, input: Port) -> Port:
        print("++++")
        payload = json.dumps({"text": input.value, "voice": self.voice})
        headers = {
            "x-api-key": self.azure_endpoint_api_key,
            "Content-Type": "application/json",
        }
        response = requests.post(self.endpoint, headers=headers, data=payload)

        response_json = response.json()
        # save to file
        with open("audio.wav", "wb") as file:
            file.write(base64.b64decode(response_json["audio_data"]))
        encode_string = base64.b64encode(open("audio.wav", "rb").read())
        wav_file = open("temp.mp3", "wb")
        decode_string = base64.b64decode(encode_string)
        wav_file.write(decode_string)
        print(response.json())
        raise ValueError("Not implemented")
        return Port(data_type=PortType.TEXT, value=f"TEXT_TO_AUDIO {input.value}")
