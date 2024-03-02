from openplugin.processors import ProcessorImplementationType

from .text_to_file import TextToFile


def get_text_to_file(
    implementation_type: ProcessorImplementationType, metadata: dict
) -> TextToFile:
    if implementation_type == ProcessorImplementationType.TEXT_TO_FILE_WITH_DEFAULT:
        from .text_to_file_with_default import TextToFileWithDefault

        return TextToFileWithDefault(**metadata)
    else:
        raise ValueError("Invalid implementation type: {}".format(implementation_type))
