import pytest

from openplugin.plugins.port import Port, PortType
from openplugin.processors.processor_factory import get_processor_from_str


@pytest.fixture
def html_to_text_obj():
    return get_processor_from_str(
        processor_type="html_to_text",
        implementation_type="html_to_text_with_bs",
        metadata={},
    )


def test_html_to_text_obj1(html_to_text_obj):
    input_port = Port(
        data_type=PortType.HTML, value="<html><body><p>Test</p></body></html>"
    )
    output_port = html_to_text_obj.process(input_port)
    assert output_port.data_type == PortType.TEXT
    assert output_port.value == "Test"
