import jinja2
from pydantic import Field

from openplugin.plugins.port import Port, PortType
from openplugin.processors.template_engine.template_engine import TemplateEngine


class TemplateEngineWithJinja(TemplateEngine):
    template: str = Field()
    output_port_type: PortType = Field(PortType.TEXT)

    def process_input(self, input: Port) -> Port:
        template = jinja2.Template(self.template)
        template_response = template.render(input.value)
        return Port(data_type=self.output_port_type, value=template_response)
