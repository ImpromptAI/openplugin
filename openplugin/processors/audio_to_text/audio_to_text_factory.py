from openplugin.processors import ProcessorImplementationType

from .audio_to_text import AudioToText


def get_audio_to_text(
    implementation_type: ProcessorImplementationType, metadata: dict
) -> AudioToText:
    if implementation_type == ProcessorImplementationType.AUDIO_TO_TEXT_WITH_WHISPER:
        from .audio_to_text_with_whisper import AudioToTextWithWhisper

        return AudioToTextWithWhisper(**metadata)
    else:
        raise ValueError("Invalid implementation type: {}".format(implementation_type))
