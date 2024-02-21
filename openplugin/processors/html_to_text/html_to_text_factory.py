from openplugin.processors import ProcessorImplementationType

from .html_to_text import HtmlToText


def get_html_to_text(
    implementation_type: ProcessorImplementationType, metadata: dict
) -> HtmlToText:
    if implementation_type == ProcessorImplementationType.HTML_TO_TEXT_WITH_BS:
        from .html_to_text_with_bs import HtmlToTextWithBS

        return HtmlToTextWithBS(**metadata)
    else:
        raise ValueError("Invalid implementation type: {}".format(implementation_type))
