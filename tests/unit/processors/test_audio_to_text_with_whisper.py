import os

import pytest
from dotenv import load_dotenv

from openplugin.core import Port, PortType
from openplugin.processors.processor_factory import get_processor_from_str

load_dotenv()


@pytest.fixture
def audio_to_text_obj():
    api_key = os.environ["OPENAI_API_KEY"]
    return get_processor_from_str(
        processor_type="audio_to_text",
        implementation_type="audio_to_text_with_whisper",
        metadata={"openai_api_key": api_key},
    )


def test_audio_to_text_with_default1(audio_to_text_obj):
    input_port = Port(data_type=PortType.FILEPATH, value="output.mp3")
    output_port = audio_to_text_obj.process(input_port)
    print("+++++")
    print(output_port)
    assert False
    assert output_port.data_type == PortType.TEXT


@pytest.fixture(autouse=True)
def cleanup():
    yield
    try:
        pass
        # os.remove("output.mp3")
    except OSError:
        pass
