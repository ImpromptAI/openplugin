from typing import Optional

import requests

from openplugin.plugins.models import Config
from openplugin.plugins.port import Port, PortType, PortValueError

from .url_to_html import UrlToHtml


class UrlToHtmlWithRequest(UrlToHtml):
    async def process_input(
        self,
        input: Port,
        config: Optional[Config] = None,
    ) -> Port:
        if input.value is None:
            raise PortValueError("Input value cannot be None")
        response = requests.get(input.value)
        response.raise_for_status()
        return Port(
            data_type=PortType.HTML,
            value=response.text,
        )
