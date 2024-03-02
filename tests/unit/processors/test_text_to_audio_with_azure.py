import os

import pytest
from dotenv import load_dotenv

from openplugin.core import Port, PortType
from openplugin.processors.processor_factory import get_processor_from_str

load_dotenv()


@pytest.fixture
def text_to_audio_obj():
    api_key = os.environ["AZURE_API_KEY"]
    return get_processor_from_str(
        processor_type="text_to_audio",
        implementation_type="text_to_audio_with_azure",
        metadata={"azure_endpoint_api_key": api_key},
    )


def test_text_to_audio_with_default1(text_to_audio_obj):
    input_port = Port(data_type=PortType.TEXT, value="How are you?")
    output_port = text_to_audio_obj.process(input_port)
    assert output_port.data_type == PortType.FILEPATH
    print(os.path.getsize(output_port.value))
    assert os.path.getsize(output_port.value) > 100


@pytest.fixture(autouse=True)
def cleanup():
    yield
    try:
        os.remove("output.mp3")
    except OSError:
        pass
