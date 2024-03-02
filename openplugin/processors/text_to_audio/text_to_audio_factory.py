from openplugin.processors import ProcessorImplementationType

from .text_to_audio import TextToAudio


def get_text_to_audio(
    implementation_type: ProcessorImplementationType, metadata: dict
) -> TextToAudio:
    if implementation_type == ProcessorImplementationType.TEXT_TO_AUDIO_WITH_AZURE:
        from .text_to_audio_with_azure import TextToAudioWithAzure

        return TextToAudioWithAzure(**metadata)
    else:
        raise ValueError("Invalid implementation type: {}".format(implementation_type))
