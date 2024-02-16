from abc import ABC, abstractmethod
from enum import Enum

from loguru import logger
from pydantic import BaseModel, Field

from openplugin.plugins.port import Port


class ProcessorType(Enum):
    TEXT_TO_AUDIO = "text_to_audio"
    AUDIO_TO_TEXT = "audio_to_text"
    TEMPLATE_ENGINE = "template_engine"
    TEXT_TO_FILE = "text_to_file"
    FILE_TO_TEXT = "file_to_text"


class ProcessorImplementationType(Enum):
    TEXT_TO_AUDIO_WITH_AZURE = "text_to_audio_with_azure"
    AUDIO_TO_TEXT_WITH_WHISPER = "audio_to_text_with_whisper"
    TEMPLATE_ENGINE_WITH_JINJA = "template_engine_with_jinja"
    TEXT_TO_FILE_WITH_DEFAULT = "text_to_file_with_default"
    FILE_TO_TEXT_WITH_LANGCHAIN = "file_to_text_with_langchain"


PROCESSOR_IMPLEMENTATION_MAP = {
    ProcessorImplementationType.TEXT_TO_AUDIO_WITH_AZURE: ProcessorType.TEXT_TO_AUDIO,
    ProcessorImplementationType.AUDIO_TO_TEXT_WITH_WHISPER: ProcessorType.AUDIO_TO_TEXT,
    ProcessorImplementationType.TEMPLATE_ENGINE_WITH_JINJA: ProcessorType.TEMPLATE_ENGINE,  # noqa: E501
    ProcessorImplementationType.TEXT_TO_FILE_WITH_DEFAULT: ProcessorType.TEXT_TO_FILE,  # noqa: E501
    ProcessorImplementationType.FILE_TO_TEXT_WITH_LANGCHAIN: ProcessorType.FILE_TO_TEXT,  # noqa: E501
}


class Processor(ABC, BaseModel):
    name: str = Field(...)
    description: str = Field(...)

    def process(self, input: Port) -> Port:
        self.validate_input_port(input)
        output = self.process_input(input)
        self.validate_output_port(output)
        logger.info(
            f"\n[PROCESSOR_TRANSFORMATION] name={self.name}, {input.data_type} >> {output.data_type}"  # noqa: E501
        )
        return output

    @abstractmethod
    def validate_input_port(self, input: Port) -> bool:
        raise NotImplementedError("Subclasses must implement the process method")

    @abstractmethod
    def validate_output_port(self, input: Port) -> bool:
        raise NotImplementedError("Subclasses must implement the process method")

    @abstractmethod
    def process_input(self, input: Port) -> Port:
        raise NotImplementedError("Subclasses must implement the process method")
