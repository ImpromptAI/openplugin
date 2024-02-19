import os

import pytest

from openplugin.plugins.port import Port, PortType
from openplugin.processors.processor_factory import get_processor_from_str


@pytest.fixture
def text_to_file_obj():
    return get_processor_from_str(
        processor_type="text_to_file",
        implementation_type="text_to_file_with_default",
        metadata={"file_type": "txt", "file_name": "test_file"},
    )


def test_text_to_file_with_default1(text_to_file_obj):
    input_port = Port(data_type=PortType.TEXT, value="Test data")
    output_port = text_to_file_obj.process(input_port)
    assert output_port.data_type == PortType.FILEPATH
    assert output_port.value == "test_file.txt"
    with open("test_file.txt", "r") as file:
        assert file.read() == "Test data"


def test_text_to_file_with_default2(text_to_file_obj):
    input_port = Port(data_type=PortType.TEXT, value="abcd")
    output_port = text_to_file_obj.process(input_port)
    assert output_port.data_type == PortType.FILEPATH
    assert output_port.value == "test_file.txt"
    with open("test_file.txt", "r") as file:
        assert file.read() == "abcd"


@pytest.fixture(autouse=True)
def cleanup():
    yield
    try:
        os.remove("test_file.txt")
    except OSError:
        pass
