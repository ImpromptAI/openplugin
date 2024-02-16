from openplugin.processors import ProcessorImplementationType

from .file_to_text import FileToText


def get_file_to_text(
    implementation_type: ProcessorImplementationType, metadata: dict
) -> FileToText:
    if implementation_type == ProcessorImplementationType.FILE_TO_TEXT_WITH_LANGCHAIN:
        from .file_to_text_with_langchain import FileToTextWithLangchain

        return FileToTextWithLangchain(**metadata)
    else:
        raise ValueError("Invalid implementation type: {}".format(implementation_type))
