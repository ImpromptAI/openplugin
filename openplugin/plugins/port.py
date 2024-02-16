# inspired by this: https://github.com/gangtao/pyflow/blob/master/src/fbp/port.py

import json
import uuid
from enum import Enum
from typing import Any

from pydantic import BaseModel, DirectoryPath, FilePath, HttpUrl


# All Supported Types
class PortType(Enum):
    BOOLEAN = bool
    INT = int
    LONG = int
    FLOAT = float
    TEXT = str
    LIST = list
    JSON = dict
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


class Port(BaseModel):
    name: str = str(uuid.uuid4())
    data_type: PortType = PortType.TEXT
    type_object: Any = data_type.value
    value: Any

    @classmethod
    def supported_types(cls):
        return list(PortType)

    def get_value(self):
        return {"name": self.name, "value": self.value, "type": self.data_type}

    def __str__(self):
        return f"name= {self.name}, value= {self.value}, type= {self.data_type}"
