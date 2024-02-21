from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional

from loguru import logger
from pydantic import BaseModel, Field

from openplugin.plugins.models import Config
from openplugin.plugins.port import Port


class ProcessorType(Enum):
    TEXT_TO_AUDIO = "text_to_audio"
    AUDIO_TO_TEXT = "audio_to_text"
    TEMPLATE_ENGINE = "template_engine"
    TEXT_TO_FILE = "text_to_file"
    FILE_TO_TEXT = "file_to_text"
    FILE_TO_CLOUD = "file_to_cloud"
    URL_TO_HTML = "url_to_html"
    HTML_TO_TEXT = "html_to_text"


class ProcessorImplementationType(Enum):
    TEXT_TO_AUDIO_WITH_AZURE = "text_to_audio_with_azure"
    AUDIO_TO_TEXT_WITH_WHISPER = "audio_to_text_with_whisper"
    TEMPLATE_ENGINE_WITH_JINJA = "template_engine_with_jinja"
    TEXT_TO_FILE_WITH_DEFAULT = "text_to_file_with_default"
    FILE_TO_TEXT_WITH_LANGCHAIN = "file_to_text_with_langchain"
    FILE_TO_CLOUD_WITH_S3 = "file_to_cloud_with_s3"
    URL_TO_HTML_WITH_REQUEST = "url_to_html_with_request"
    HTML_TO_TEXT_WITH_BS = "html_to_text_with_bs"


PROCESSOR_IMPLEMENTATION_MAP = {
    ProcessorImplementationType.TEXT_TO_AUDIO_WITH_AZURE: ProcessorType.TEXT_TO_AUDIO,
    ProcessorImplementationType.AUDIO_TO_TEXT_WITH_WHISPER: ProcessorType.AUDIO_TO_TEXT,
    ProcessorImplementationType.TEMPLATE_ENGINE_WITH_JINJA: ProcessorType.TEMPLATE_ENGINE,  # noqa: E501
    ProcessorImplementationType.TEXT_TO_FILE_WITH_DEFAULT: ProcessorType.TEXT_TO_FILE,  # noqa: E501
    ProcessorImplementationType.FILE_TO_TEXT_WITH_LANGCHAIN: ProcessorType.FILE_TO_TEXT,  # noqa: E501
    ProcessorImplementationType.FILE_TO_CLOUD_WITH_S3: ProcessorType.FILE_TO_CLOUD,
    ProcessorImplementationType.URL_TO_HTML_WITH_REQUEST: ProcessorType.URL_TO_HTML,
    ProcessorImplementationType.HTML_TO_TEXT_WITH_BS: ProcessorType.HTML_TO_TEXT,
}


class InvalidInputPortError(Exception):
    """Raised when the input port is invalid"""

    def __init__(self, message="Invalid input port"):
        self.message = message
        super().__init__(self.message)


class InvalidOutputPortError(Exception):
    """Raised when the output port is invalid"""

    def __init__(self, message="Invalid output port"):
        self.message = message
        super().__init__(self.message)


class ProcessingError(Exception):
    """Raised when there is an error during processing"""

    def __init__(self, message="Error during processing"):
        self.message = message
        super().__init__(self.message)


class Processor(ABC, BaseModel):
    name: str = Field(...)
    description: str = Field(...)

    async def process(self, input: Port, config: Optional[Config] = None) -> Port:
        await self.validate_input_port(input)
        output = await self.process_input(input=input, config=config)
        await self.validate_output_port(output)
        logger.info(
            f"\n[PROCESSOR_TRANSFORMATION] name={self.name}, {input.data_type} >> {output.data_type}"  # noqa: E501
        )
        return output

    @abstractmethod
    async def validate_input_port(self, input: Port) -> bool:
        raise InvalidInputPortError()

    @abstractmethod
    async def validate_output_port(self, input: Port) -> bool:
        raise InvalidOutputPortError()

    @abstractmethod
    async def process_input(self, input: Port, config: Optional[Config] = None) -> Port:
        raise NotImplementedError("Subclasses must implement the process method")
