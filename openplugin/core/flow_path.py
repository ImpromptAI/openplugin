import json
import time
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, root_validator

from openplugin.processors import (
    Processor,
    ProcessorImplementationType,
    ProcessorType,
    get_processor_from_str,
)

from .config import Config
from .helper import time_taken
from .port import PORT_TYPE_MAPPING, Port, PortMetadata, PortType


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
        values["log_title"] = (
            f"[PROCESSING-FINISHED] name={values['processor_type']}"
        )
        return values

    @time_taken
    async def run_processor(self, input: Port, config: Config) -> Port:
        return await self.processor.process(input, config)


class FlowPath(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    name: str
    description: Optional[str] = None
    initial_input_port: Port
    finish_output_port: Port
    processors: List[ProcessorNode]
    log_title: str
    default_module: bool = False

    @root_validator(pre=True)
    def setup(cls, values):
        assert "initial_input_port" in values
        values["initial_input_port"] = convert_str_to_port(
            values["initial_input_port"]
        )
        assert "finish_output_port" in values
        values["finish_output_port"] = convert_str_to_port(
            values["finish_output_port"]
        )
        values["log_title"] = f"[MODULE-PROCESSING-FINISHED] name={values['name']}"
        return values

    def get_processor_metadata(self):
        metadata = {}
        for processor in self.processors:
            if processor.metadata:
                metadata.update(processor.metadata)
        return metadata

    async def run(self, input: Port, config: Config) -> Port:
        port = input
        start_time = time.time()
        processor_run_log = []
        for processor in self.processors:
            input_text = port.value
            if isinstance(input_text, dict):
                input_text = json.dumps(input_text)
            else:
                input_text = str(input_text)
            port = await processor.run_processor(port, config)

            output_text = port.value
            if isinstance(output_text, dict):
                output_text = json.dumps(output_text)
            else:
                output_text = str(output_text)
            label = f"{self.name} [{processor.processor.name}]"
            processor_run_log.append(
                {
                    "label": label,
                    "input_text": input_text,
                    "output_text": output_text,
                }
            )
        end_time = time.time()
        port.metadata = {
            PortMetadata.PROCESSING_TIME_SECONDS: round((end_time - start_time), 4),
            PortMetadata.STATUS_CODE: 200,
            PortMetadata.LOG_PROCESSOR_RUN: processor_run_log,
        }
        return port

    def get_output_port_type(self) -> PortType:
        return self.finish_output_port.data_type

    def __str__(self):
        return f"id= {self.id}, name= {self.name}"
