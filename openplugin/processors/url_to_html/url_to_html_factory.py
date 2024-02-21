from openplugin.processors import ProcessorImplementationType

from .url_to_html import UrlToHtml


def get_url_to_html(
    implementation_type: ProcessorImplementationType, metadata: dict
) -> UrlToHtml:
    if implementation_type == ProcessorImplementationType.URL_TO_HTML_WITH_REQUEST:
        from .url_to_html_with_request import UrlToHtmlWithRequest

        return UrlToHtmlWithRequest(**metadata)
    else:
        raise ValueError("Invalid implementation type: {}".format(implementation_type))
