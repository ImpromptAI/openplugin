import json
from typing import Optional

import jinja2
from pydantic import Field

from openplugin.core import Config, Port, PortType, PortValueError

from ..template_engine import TemplateEngine


class TemplateEngineWithJinja(TemplateEngine):
    template: str = Field()
    mime_type: Optional[str] = None
    output_port: PortType = Field(PortType.TEXT)

    async def process_input(self, input: Port, config: Optional[Config] = None) -> Port:
        if input.value is None:
            raise PortValueError("Input value cannot be None")
        if self.mime_type and "json" in self.mime_type:
            self.output_port = PortType.JSON
        template = jinja2.Template(self.template)
        try:
            template_response = template.render(input.value)
        except Exception:
            template_response = template.render(data=input.value)
        if self.output_port == PortType.JSON:
            template_response = json.loads(template_response)
        return Port(
            data_type=self.output_port,
            mime_type=self.mime_type,
            value=template_response,
        )
