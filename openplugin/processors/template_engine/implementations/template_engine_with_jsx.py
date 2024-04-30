from typing import Optional

from pydantic import Field

from openplugin.core import Config, Port, PortType, PortValueError

from ..template_engine import TemplateEngine


class TemplateEngineWithJSX(TemplateEngine):
    template: str = Field()
    output_port_type: PortType = Field(PortType.TEXT)
    mime_type: Optional[str] = "text"

    async def process_input(self, input: Port, config: Optional[Config] = None) -> Port:
        if input.value is None:
            raise PortValueError("Input value cannot be None")
        return Port(
            data_type=self.output_port_type,
            value=self.template,
            mime_type=self.mime_type,
        )
