import asyncio
import re
from typing import Dict, List, Optional

from loguru import logger
from pydantic import BaseModel, computed_field

from .config import Config
from .execution.implementations.operation_execution_with_imprompt import (
    OperationExecutionParams,
    OperationExecutionWithImprompt,
)
from .function_providers import FunctionProvider
from .helper import time_taken
from .messages import Message, MessageType
from .operations.implementations.operation_signature_builder_with_langchain import (
    LangchainOperationSignatureBuilder,
)
from .plugin import Plugin
from .port import Port, PortMetadata, PortType, PortValueError


async def run_module(output_module, flow_port):
    logger.info(f"\n[RUNNING_OUTPUT_MODULE] {output_module}")
    output_port = await output_module.run(flow_port)
    output_port.name = output_module.name
    if output_module.default_module:
        output_port.add_metadata(PortMetadata.DEFAULT_OUTPUT_MODULE, True)
    logger.info(f"\n[FINAL_RESPONSE] {output_port.value}")
    return output_port


class APIExecutionStepResponse(BaseModel):
    original_response: Port
    clarifying_response: Optional[Port]


class PluginExecutionResponse(BaseModel):
    input_modules: List[Port]
    api_and_signature_detection_step: dict
    api_execution_step: APIExecutionStepResponse
    output_module_map: Dict[str, Port]
    default_output_module: Optional[str]

    @computed_field  # type: ignore
    @property
    def tracing_steps(self) -> List:
        metrics = [
            {
                "name": "input_module_step",
                "label": "Input Module",
                "processing_time_seconds": self.input_modules[0].get_metadata(
                    PortMetadata.PROCESSING_TIME_SECONDS
                ),
                "processor_logs": self.input_modules[0].get_metadata(
                    PortMetadata.LOG_PROCESSOR_RUN, []
                ),
                "status_code": self.input_modules[0].get_metadata(
                    PortMetadata.STATUS_CODE
                ),
            },
            {
                "name": "api_and_signature_detection_step",
                "label": "Signature Creation (w/ LLM)",
                "processing_time_seconds": self.api_and_signature_detection_step.get(
                    "metadata", {}
                ).get("processing_time_seconds"),
                "status_code": self.api_and_signature_detection_step.get(
                    "metadata", {}
                ).get("status_code"),
                "input_text": self.api_and_signature_detection_step.get(
                    "metadata", {}
                ).get("input_text"),
                "output_text": self.api_and_signature_detection_step.get(
                    "metadata", {}
                ).get("output_text"),
            },
            {
                "name": "api_execution_step",
                "label": "API Execution",
                "processing_time_seconds": self.api_execution_step.original_response.get_metadata(
                    PortMetadata.PROCESSING_TIME_SECONDS
                ),
                "status_code": self.api_execution_step.original_response.get_metadata(
                    PortMetadata.STATUS_CODE
                ),
                "input_text": self.api_execution_step.original_response.get_metadata(
                    PortMetadata.LOG_INPUT_TEXT
                ),
                "output_text": self.api_execution_step.original_response.get_metadata(
                    PortMetadata.LOG_OUTPUT_TEXT
                ),
            },
        ]

        for key, item in self.output_module_map.items():
            metrics.append(
                {
                    "name": item.name,
                    "label": f"Output Module [ {item.name.replace('_',' ')} ]",
                    "parallel": True,
                    "processing_time_seconds": item.get_metadata(
                        PortMetadata.PROCESSING_TIME_SECONDS
                    ),
                    "processor_logs": item.get_metadata(PortMetadata.LOG_PROCESSOR_RUN),
                    "status_code": item.get_metadata(PortMetadata.STATUS_CODE),
                }
            )
        return metrics


class PluginExecutionPipeline(BaseModel):
    plugin: Plugin

    async def start(
        self,
        input: Port,
        config: Config,
        function_provider: FunctionProvider,
        header: Optional[dict],
        auth_query_param: Optional[dict],
        output_module_names: Optional[List[str]] = None,
        run_all_output_modules: bool = False,
    ) -> PluginExecutionResponse:
        if not run_all_output_modules and (
            output_module_names is None or len(output_module_names) == 0
        ):
            output_module_names = ["original_response"]
        config.replace_missing_with_system_keys()
        # setup default keys
        flow_port = input
        flow_port.name = "default_no_change_input"
        flow_port.metadata = {
            PortMetadata.PROCESSING_TIME_SECONDS: 0,
            PortMetadata.STATUS_CODE: 200,
            PortMetadata.LOG_PROCESSOR_RUN: [
                {
                    "label": "Input Module [Standard]",
                    "input_text": input.value,
                    "output_text": input.value
                }
            ],
        }
        input_modules: List[Port] = []
        if self.plugin.input_modules:
            for input_module in self.plugin.input_modules:
                if input_module.initial_input_port.data_type == flow_port.data_type:
                    logger.info(f"\n[RUNNING_INPUT_MODULE] {input_module}")
                    flow_port = await input_module.run(flow_port)
                    break
        input_modules.append(flow_port)

        api_signature_port = self._run_plugin_signature_selector(
            input=flow_port, config=config, function_provider=function_provider
        )

        logger.info(f"\n[PLUGIN_SIGNATURE_RESPONSE] {api_signature_port.value}")
        api_execution_step = self._run_plugin_execution(
            input=api_signature_port,
            config=config,
            header=header,
            auth_query_param=auth_query_param,
            function_provider=function_provider,
        )
        default_output_module = None
        output_module_map = {}
        if api_execution_step.clarifying_response is None:
            flow_port = api_execution_step.original_response
            response_output_ports: List[Port] = []

            api_called = api_signature_port.value.get("api_called")
            method = api_signature_port.value.get("method")

            supported_output_modules = self.plugin.get_supported_output_modules(
                operation=api_called, method=method
            )
            if run_all_output_modules and supported_output_modules:
                for output_module in supported_output_modules:
                    o_ports = await asyncio.gather(
                        *(
                            run_module(output_module, flow_port)
                            for output_module in supported_output_modules
                        )
                    )
                    if o_ports:
                        response_output_ports.extend(o_ports)
            elif output_module_names and supported_output_modules:
                selected_output_modules = []
                for output_module in supported_output_modules:
                    if output_module.name in output_module_names:
                        selected_output_modules.append(output_module)
                o_ports = await asyncio.gather(
                    *(
                        run_module(output_module, flow_port)
                        for output_module in selected_output_modules
                    )
                )
                if o_ports:
                    response_output_ports.extend(o_ports)
        else:
            default_output_module = "clarifying_response"
            output_module_map[
                "clarifying_response"
            ] = api_execution_step.clarifying_response

        if response_output_ports:
            for output_port in response_output_ports:
                output_module_map[output_port.name] = output_port
                if output_port.get_metadata(PortMetadata.DEFAULT_OUTPUT_MODULE):
                    default_output_module = output_port.name
        # set the first one as default if not set in manifest
        if default_output_module is None and response_output_ports:
            default_output_module = response_output_ports[0].name

        if output_module_names and "original_response" in output_module_names:
            output_module_map[
                "original_response"
            ] = api_execution_step.original_response
            default_output_module = "original_response"

        return PluginExecutionResponse(
            input_modules=input_modules,
            output_module_map=output_module_map,
            api_execution_step=api_execution_step,
            api_and_signature_detection_step=api_signature_port.value,
            default_output_module=default_output_module,
        )

    @time_taken
    def _run_plugin_signature_selector(
        self,
        input: Port,
        config: Config,
        function_provider: FunctionProvider,
    ) -> Port:
        if input.data_type != PortType.TEXT:
            raise Exception("Input data type to plugin must be text.")
        if input.value is None:
            raise PortValueError("Input value cannot be None")
        messages = [Message(content=input.value, message_type=MessageType.HumanMessage)]
        logger.info(f"\n[RUNNING_PLUGIN_SIGNATURE] provider]={function_provider}")
        # API signature selector
        oai_selector = LangchainOperationSignatureBuilder(
            plugin=self.plugin, function_provider=function_provider, config=config
        )
        response = oai_selector.run(messages)

        ops = response.detected_plugin_operations
        if ops and len(ops) > 0:
            status_code = 500
            if response.run_completed:
                status_code = 200
            output_port_text = f"api_called={ops[0].api_called}, method={ops[0].method}, mapped_operation_parameters={ops[0].mapped_operation_parameters}"
            val = {
                "api_called": ops[0].api_called,
                "method": ops[0].method,
                "metadata": {
                    "processing_time_seconds": response.response_time,
                    "tokens_used": response.tokens_used,
                    "llm_api_cost": response.llm_api_cost,
                    "status_code": status_code,
                    "input_text": str(input.value),
                    "output_text": str(output_port_text),
                },
                "mapped_operation_parameters": ops[0].mapped_operation_parameters,
            }
            return Port(data_type=PortType.JSON, value=val)
        raise Exception("No operations detected")

    @time_taken
    def _run_plugin_execution(
        self,
        input: Port,
        config: Config,
        header: dict,
        auth_query_param: Optional[dict],
        function_provider: FunctionProvider,
    ) -> APIExecutionStepResponse:
        if input.data_type != PortType.JSON:
            raise Exception("Input data type to plugin must be JSON.")
        if input.value is None:
            raise PortValueError("Input value cannot be None")

        api_called = input.value.get("api_called")
        method = input.value.get("method")
        query_params = input.value.get("mapped_operation_parameters")

        input_port_text = f"api_called={api_called}, method={method}, mapped_operation_parameters={query_params}"

        # identify path parameters
        pattern = re.compile(r"\{([^}]+)\}")
        path_params = pattern.findall(api_called)

        # use path parameter values instead of names in endpoint
        # "example.com/path/{id}" >> "example.com/path/1"
        for param_name in path_params:
            if param_name in query_params:
                parameter_key = f"{{{param_name}}}"
                parameter_value = str(query_params[param_name])
                api_called = api_called.replace(parameter_key, parameter_value)

                # remove matched path parameters from query_params
                del query_params[param_name]
        logger.info(f"\n[RUNNING_PLUGIN_EXECUTION] url={api_called}, method={method}")
        if auth_query_param:
            query_params.update(auth_query_param)
        params = OperationExecutionParams(
            config=config,
            api=api_called,
            method=method,
            query_params=query_params,
            body={},
            header=header,
            function_provider=function_provider,
        )
        ex = OperationExecutionWithImprompt(params)
        response = ex.run()

        # original port
        original_port = Port(
            name="original_response",
            data_type=PortType.JSON,
            value=response.original_response,
            metadata={
                PortMetadata.PROCESSING_TIME_SECONDS: response.api_call_response_seconds,
                PortMetadata.STATUS_CODE: response.api_call_status_code,
                PortMetadata.LOG_INPUT_TEXT: str(input_port_text),
                PortMetadata.LOG_OUTPUT_TEXT: str(response.original_response),
            },
        )

        # clarifying question
        clarifying_port = None
        if response.clarifying_response:
            clarifying_port = Port(
                name="clarifying_response",
                data_type=PortType.TEXT,
                value=response.clarifying_response,
                metadata={
                    PortMetadata.PROCESSING_TIME_SECONDS: response.clarifying_question_response_seconds,
                    PortMetadata.STATUS_CODE: response.clarifying_question_status_code,
                    PortMetadata.LOG_INPUT_TEXT: str(input_port_text),
                    PortMetadata.LOG_OUTPUT_TEXT: str(response.original_response),
                },
            )
        logger.info(f"\n[PLUGIN_EXECUTION_RESPONSE] {original_port.value}")
        return APIExecutionStepResponse(
            original_response=original_port,
            clarifying_response=clarifying_port,
        )
