from bs4 import BeautifulSoup
from openplugin.plugins.port import Port, PortType

from .html_to_text import HtmlToText


class HtmlToTextWithBS(HtmlToText):

    def process_input(self, input: Port) -> Port:
        # Parse the HTML content
        soup = BeautifulSoup(input.value, "html.parser")
        text = soup.get_text()
        return Port(data_type=PortType.TEXT, value=text)
