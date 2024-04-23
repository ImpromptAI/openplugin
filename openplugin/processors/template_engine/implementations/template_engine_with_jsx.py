from typing import Optional

from pydantic import Field

from openplugin.core import Config, Port, PortType, PortValueError, MimeType

from ..template_engine import TemplateEngine


class TemplateEngineWithJSX(TemplateEngine):
    template: str = Field()
    output_port_type: PortType = Field(PortType.TEXT)
    mime_type: Optional[MimeType] = MimeType.TEXT_PLAIN

    async def process_input(
        self, input: Port, config: Optional[Config] = None
    ) -> Port:
        if input.value is None:
            raise PortValueError("Input value cannot be None")
        mime_types=[]
        if input.mime_types:
            for mime_type in input.mime_types:
                mime_types.append(mime_type)
        return Port(
            data_type=self.output_port_type,
            value=self.template,
            mime_types=mime_types
        )
