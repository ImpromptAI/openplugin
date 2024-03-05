from typing import Optional

import jinja2
from pydantic import Field

from openplugin.core import Config, Port, PortType, PortValueError

from ..template_engine import TemplateEngine


class TemplateEngineWithJinja(TemplateEngine):
    template: str = Field()
    output_port_type: PortType = Field(PortType.TEXT)

    async def process_input(
        self, input: Port, config: Optional[Config] = None
    ) -> Port:
        if input.value is None:
            raise PortValueError("Input value cannot be None")
        template = jinja2.Template(self.template)
        # TODO improve this
        try:
            template_response = template.render(input.value)
        except Exception as e:
            template_response = template.render(data=input.value)
        return Port(data_type=self.output_port_type, value=template_response)
