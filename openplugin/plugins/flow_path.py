from typing import Any, Dict, List
from uuid import uuid4

from pydantic import BaseModel, Field, root_validator

from openplugin.processors import (
    Processor,
    ProcessorImplementationType,
    ProcessorType,
    get_processor_from_str,
)

from . import time_taken
from .port import PORT_TYPE_MAPPING, Port, PortType


def convert_str_to_port(v):
    if isinstance(v, str):
        if v not in PORT_TYPE_MAPPING:
            raise Exception(f"Incorrect Port Type {v}")
        v = Port(data_type=PORT_TYPE_MAPPING[v])
    return v


class ProcessorNode(BaseModel):
    input_port: Port
    output_port: Port
    processor_type: ProcessorType
    processor_implementation_type: ProcessorImplementationType
    processor: Processor
    metadata: Dict[Any, Any]
    log_title: str

    @root_validator(pre=True)
    def setup(cls, values):
        assert "input_port" in values
        values["input_port"] = convert_str_to_port(values["input_port"])

        assert "output_port" in values
        values["output_port"] = convert_str_to_port(values["output_port"])

        values["processor"] = get_processor_from_str(
            processor_type=values["processor_type"],
            implementation_type=values["processor_implementation_type"],
            metadata=values["metadata"],
        )
        values["log_title"] = f"[PROCESSING-FINISHED] name={values['processor_type']}"
        return values

    @time_taken
    async def run_processor(self, input: Port) -> Port:
        return await self.processor.process(input)


class FlowPath(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    name: str
    description: str
    initial_input_port: Port
    finish_output_port: Port
    processors: List[ProcessorNode]
    log_title: str

    @root_validator(pre=True)
    def setup(cls, values):
        assert "initial_input_port" in values
        values["initial_input_port"] = convert_str_to_port(values["initial_input_port"])
        assert "finish_output_port" in values
        values["finish_output_port"] = convert_str_to_port(values["finish_output_port"])
        values["log_title"] = f"[MODULE-PROCESSING-FINISHED] name={values['name']}"
        return values

    async def run(self, input: Port) -> Port:
        port = input
        for processor in self.processors:
            port = await processor.run_processor(port)
        return port

    def get_output_port_type(self) -> PortType:
        return self.finish_output_port.data_type

    def __str__(self):
        return f"id= {self.id}, name= {self.name}"
