import os

import pytest

from openplugin.plugins.port import Port, PortType
from openplugin.processors.processor_factory import get_processor_from_str


@pytest.fixture
def url_to_html_obj():
    return get_processor_from_str(
        processor_type="url_to_html",
        implementation_type="url_to_html_with_request",
        metadata={},
    )


def test_url_to_html_obj1(url_to_html_obj):
    input_port = Port(
        data_type=PortType.HTTPURL, value="https://www.brandops.io/about-us"
    )
    output_port = url_to_html_obj.process(input_port)
    assert output_port.data_type == PortType.HTML
