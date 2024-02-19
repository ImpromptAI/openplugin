import requests
from openplugin.plugins.port import Port, PortType

from .url_to_html import UrlToHtml


class UrlToHtmlWithRequest(UrlToHtml):

    def process_input(self, input: Port) -> Port:
        response = requests.get(input.value)
        response.raise_for_status()
        return Port(
            data_type=PortType.HTML,
            value=response.text,
        )
