from .processor import (
    PROCESSOR_IMPLEMENTATION_MAP,
    Processor,
    ProcessorImplementationType,
    ProcessorType,
)


def get_processor_from_str(
    processor_type: str,
    implementation_type: str,
    metadata: dict,
) -> Processor:
    return get_processor_from_enum(
        ProcessorType(processor_type),
        ProcessorImplementationType(implementation_type),
        metadata,
    )


def get_processor_from_enum(
    processor_type: ProcessorType,
    implementation_type: ProcessorImplementationType,
    metadata: dict,
) -> Processor:
    if PROCESSOR_IMPLEMENTATION_MAP[implementation_type] != processor_type:
        raise ValueError(
            "Invalid implementation type: {} for processor type: {}".format(
                implementation_type, processor_type
            )
        )
    if processor_type == ProcessorType.AUDIO_TO_TEXT:
        from .audio_to_text.audio_to_text_factory import get_audio_to_text

        return get_audio_to_text(
            implementation_type=implementation_type, metadata=metadata
        )
    elif processor_type == ProcessorType.TEXT_TO_AUDIO:
        from .text_to_audio.text_to_audio_factory import get_text_to_audio

        return get_text_to_audio(
            implementation_type=implementation_type, metadata=metadata
        )
    elif processor_type == ProcessorType.TEMPLATE_ENGINE:
        from .template_engine.template_engine_factory import get_template_engine

        return get_template_engine(
            implementation_type=implementation_type, metadata=metadata
        )
    elif processor_type == ProcessorType.TEXT_TO_FILE:
        from .text_to_file.text_to_file_factory import get_text_to_file

        return get_text_to_file(
            implementation_type=implementation_type, metadata=metadata
        )
    elif processor_type == ProcessorType.FILE_TO_TEXT:
        from .file_to_text.file_to_text_factory import get_file_to_text

        return get_file_to_text(
            implementation_type=implementation_type, metadata=metadata
        )
    elif processor_type == ProcessorType.FILE_TO_CLOUD:
        from .file_to_cloud.file_to_cloud_factory import get_file_to_cloud

        return get_file_to_cloud(
            implementation_type=implementation_type, metadata=metadata
        )
    elif processor_type == ProcessorType.URL_TO_HTML:
        from .url_to_html.url_to_html_factory import get_url_to_html

        return get_url_to_html(
            implementation_type=implementation_type, metadata=metadata
        )
    elif processor_type == ProcessorType.HTML_TO_TEXT:
        from .html_to_text.html_to_text_factory import get_html_to_text

        return get_html_to_text(
            implementation_type=implementation_type, metadata=metadata
        )

    else:
        raise ValueError("Invalid processor type: {}".format(processor_type))
