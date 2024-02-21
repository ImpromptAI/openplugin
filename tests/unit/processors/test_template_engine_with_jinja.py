import pytest

from openplugin.plugins.port import Port, PortType
from openplugin.processors.processor_factory import get_processor_from_str


@pytest.fixture
def template_obj():
    template = """{% for product in products %}
    Name: {{ product['name'] }}
    URL: {{ product['url'] }}
    Price: {{ product['price'] }}
    -----------------------------------
    {% endfor %}"""
    return get_processor_from_str(
        processor_type="template_engine",
        implementation_type="template_engine_with_jinja",
        metadata={"template": template},
    )


def test_template_engine_with_default1(template_obj):
    inp_json = {
        "products": [
            {"name": "a", "url": "http://a.com", "price": "10"},
            {"name": "b", "url": "http://b.com", "price": "20"},
        ]
    }
    input_port = Port(data_type=PortType.JSON, value=inp_json)
    output_port = template_obj.process(input_port)
    assert output_port.data_type == PortType.TEXT
