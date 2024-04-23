# inspired by this: https://github.com/gangtao/pyflow/blob/master/src/fbp/port.py
import json
import uuid
from enum import Enum
from typing import Any, Dict, Optional, List

from pydantic import (
    BaseModel,
    DirectoryPath,
    Field,
    FilePath,
    HttpUrl,
    field_serializer,
)


# All Supported Types
class PortType(Enum):
    BOOLEAN = bool
    INT = int
    LONG = int
    FLOAT = float
    TEXT = str
    LIST = list
    JSON = dict
    HTML = str
    HTTPURL = HttpUrl
    REMOTE_FILE_URL = HttpUrl
    FILEPATH = FilePath
    FILE = Any 
    DIRECTORYPATH = DirectoryPath


class MimeType(Enum):
    TEXT_ANY="text/*"
    TEXT_CSV="text/csv"
    TEXT_HTML="text/html"
    TEXT_PLAIN="text/plain"
    TEXT_JAVASCRIPT="text/javascript"
    TEXT_JSX="text/jsx"
    
    IMAGE_ANY="image/*"
    IMAGE_JPEG = "image/jpeg"
    IMAGE_PNG = "image/png"
   
    AUDIO_ANY="audio/*"
    AUDIO_WAV = "audio/wav"
    AUDIO_MP3 = "audio/mp3"
    AUDIO_FLAC = "audio/flac"
    AUDIO_AAC = "audio/aac"
    AUDIO_MPEG = "audio/mpeg"

    JSON="application/json"
    XML="application/xml"
    PDF="application/pdf"
    ZIP="application/zip"
    GZIP="application/gzip"

    VIDEO_ANY="video/*"
    VIDEO_MP4 = "video/mp4"
    VIDEO_WEBM = "video/webm"
    VIDEO_OGG = "video/ogg"
    VIDEO_QUICKTIME="video/quicktime"

# Mapping of string values to PortType enum members
PORT_TYPE_MAPPING = {
    "boolean": PortType.BOOLEAN,
    "int": PortType.INT,
    "long": PortType.LONG,
    "float": PortType.FLOAT,
    "text": PortType.TEXT,
    "list": PortType.LIST,
    "json": PortType.JSON,
    "html": PortType.HTML,
    "httpurl": PortType.HTTPURL,
    "filepath": PortType.FILEPATH,
    "directorypath": PortType.DIRECTORYPATH,
    "remote_file_url": PortType.REMOTE_FILE_URL,
    "file": PortType.FILE,
}


class PortValueError(Exception):
    """Raised when the port value is invalid"""

    def __init__(self, message="Invalid port value"):
        self.message = message
        super().__init__(self.message)


class PortMetadata(Enum):
    PROCESSING_TIME_SECONDS = "processing_time"
    STATUS_CODE = "status_code"
    TEMPLATE_ENGINE = "template_engine"
    TEMPLATE_MIME_TYPE = "template_mime_type"
    DEFAULT_OUTPUT_MODULE = "default_output_module"


class Port(BaseModel):
    name: str = str(uuid.uuid4())
    data_type: PortType
    mime_types: Optional[List[MimeType]] = None # For files
    value: Optional[Any] = None
    metadata: Optional[Dict[PortMetadata, Any]] = {}

    class Config:
        json_encoders = {
            PortType: lambda v: str(v.value),
        }

    def add_metadata(self, key: PortMetadata, value: Any):
        if self.metadata is None:
            self.metadata = {}
        self.metadata[key] = value

    def get_metadata(self, key: PortMetadata):
        if self.metadata is None:
            return None
        return self.metadata.get(key)

    @field_serializer("data_type")
    def serialize_data_type(self, data_type: PortType, _info):
        return data_type.name

    @field_serializer("metadata")
    def serialize_metadata(self, metadata: Dict[PortMetadata, Any], _info):
        values = {}
        for key, value in metadata.items():
            values[key.name.lower()] = value
        return values

    @classmethod
    def supported_types(cls):
        return list(PortType)

    def get_value(self):
        return {"name": self.name, "value": self.value, "type": self.data_type, "mime_types": self.mime_types}

    def __str__(self):
        return f"name= {self.name}, value= {self.value}, type= {self.data_type}, mime_types= {self.mime_types}"

    def to_dict(self):
        return {
            "name": self.name,
            "data_type": str(self.data_type),
            "value": self.value,
            "mime_types": self.mime_types,
        }
