from typing import Optional

from bs4 import BeautifulSoup

from openplugin.plugins.models import Config
from openplugin.plugins.port import Port, PortType, PortValueError

from .html_to_text import HtmlToText


class HtmlToTextWithBS(HtmlToText):
    async def process_input(self, input: Port, config: Optional[Config] = None) -> Port:
        # Parse the HTML content
        if input.value is None:
            raise PortValueError("Input value cannot be None")
        soup = BeautifulSoup(input.value, "html.parser")
        text = soup.get_text()
        return Port(data_type=PortType.TEXT, value=text)
