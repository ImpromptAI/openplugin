# inspired by this: https://github.com/gangtao/pyflow/blob/master/src/fbp/port.py
import uuid
import json
from enum import Enum
from typing import Any, Dict, Optional

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
    BINARY = bytes
    HTML = str
    HTTPURL = HttpUrl
    FILEPATH = FilePath
    DIRECTORYPATH = DirectoryPath


# Mapping of string values to PortType enum members
PORT_TYPE_MAPPING = {
    "boolean": PortType.BOOLEAN,
    "int": PortType.INT,
    "long": PortType.LONG,
    "float": PortType.FLOAT,
    "text": PortType.TEXT,
    "list": PortType.LIST,
    "json": PortType.JSON,
    "binary": PortType.BINARY,
    "html": PortType.HTML,
    "httpurl": PortType.HTTPURL,
    "filepath": PortType.FILEPATH,
    "directorypath": PortType.DIRECTORYPATH,
}


def type_conversion(value, data_type: PortType):
    if data_type == PortType.BOOLEAN:
        return bool(value)
    elif data_type == PortType.INT or data_type == PortType.LONG:
        return int(value)
    elif data_type == PortType.FLOAT:
        return float(value)
    elif data_type == PortType.TEXT:
        return str(value)
    elif data_type == PortType.LIST:
        return list(value) if isinstance(value, list) else str(value).split(",")
    elif data_type == PortType.JSON:
        return dict(value) if isinstance(value, dict) else json.loads(str(value))
    else:
        return None


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


class Port(BaseModel):
    name: str = str(uuid.uuid4())
    data_type: PortType = PortType.TEXT
    type_object: Any = Field(default=None, alias="type_object", exclude=True)
    value: Optional[Any] = None
    metadata: Optional[Dict[PortMetadata, Any]] = {}

    class Config:
        json_encoders = {
            PortType: lambda v: str(v.value),
        }

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
        return {"name": self.name, "value": self.value, "type": self.data_type}

    def __str__(self):
        return f"name= {self.name}, value= {self.value}, type= {self.data_type}"

    def to_dict(self):
        return {
            "name": self.name,
            "data_type": str(self.data_type),
            "value": self.value,
        }
