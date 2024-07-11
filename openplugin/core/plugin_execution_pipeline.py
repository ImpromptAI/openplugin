import asyncio
import json
import re
from typing import Any, Dict, List, Optional

from loguru import logger
from pydantic import BaseModel

from .config import Config
from .execution.implementations.operation_execution_with_imprompt import (
    OperationExecutionParams,
    OperationExecutionWithImprompt,
)
from .function_providers import FunctionProvider
from .helper import time_taken
from .messages import Message, MessageType
from .operations.implementations.operation_signature_builder_custom import (
    CustomOperationSignatureBuilder,
)
from .plugin import Plugin
from .port import Port, PortMetadata, PortType, PortValueError


async def run_module(output_module, flow_port, config: Config):
    try:
        logger.info(f"\n[RUNNING_OUTPUT_MODULE] {output_module}")
        output_port = await output_module.run(flow_port, config)
        output_port.name = output_module.name
        if output_module.default_module:
            output_port.add_metadata(PortMetadata.DEFAULT_OUTPUT_MODULE, True)
        logger.info(f"\n[FINAL_RESPONSE] {output_port.value}")
        return output_port
    except Exception as e:
        raise PluginExecutionPipelineError(
            message=f"Output Module Error for {output_module.name}: {e}"
        )


class APIExecutionStepResponse(BaseModel):
    original_response: Port
    clarifying_response: Optional[Port]


class PluginExecutionPipelineError(Exception):
    """Exception raised when a plugin execution operation is not found.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="Plugin execution pipeline failed."):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class PluginExecutionResponse(BaseModel):
    input_modules: List[Port]
    api_and_signature_detection_step: dict
    api_execution_step: APIExecutionStepResponse
    output_module_map: Dict[str, Port]
    default_output_module: Optional[str]


class PluginExecutionPipeline(BaseModel):
    plugin: Plugin
    tracing_steps: List[Dict[Any, Any]] = []
    total_tokens_used: int = 0
    total_cost: float = 0

    async def start(
        self,
        input: Port,
        config: Config,
        function_provider: FunctionProvider,
        header: Optional[dict],
        auth_query_param: Optional[dict],
        output_module_names: Optional[List[str]] = None,
        run_all_output_modules: bool = False,
        conversation: Optional[List] = [],
        selected_operation: Optional[str] = None,
        enable_ui_form_controls: bool = True,
    ) -> PluginExecutionResponse:
        if not run_all_output_modules and (
            output_module_names is None or len(output_module_names) == 0
        ):
            output_module_names = ["original_response"]
        config.replace_missing_with_system_keys()

        # INPUT MODULE PROCESSING
        input_modules: List[Port] = []
        flow_port = await self._input_module_processing(input, config)
        input_modules.append(flow_port)
        # API SIGNATURE DETECTION
        api_signature_port = self._run_plugin_signature_selector(
            input=flow_port,
            config=config,
            function_provider=function_provider,
            conversation=conversation,
            selected_operation=selected_operation,
            header=header,
        )
        self.add_tokens(api_signature_port)
        # API EXECUTION
        api_execution_step = self._run_plugin_execution(
            input=api_signature_port,
            config=config,
            header=header,
            auth_query_param=auth_query_param,
            function_provider=function_provider,
            enable_ui_form_controls=enable_ui_form_controls,
        )

        if not api_execution_step.clarifying_response:
            # filter response
            api_execution_step.original_response = await self._run_filter_module(
                api_execution_step.original_response,
                api_signature_port,
                config=config,
            )

        # OUTPUT MODULE PROCESSING
        output_module_map, default_output_module = (
            await self._output_module_processing(
                api_execution_step,
                api_signature_port,
                config,
                run_all_output_modules,
                output_module_names,
            )
        )
        return PluginExecutionResponse(
            input_modules=input_modules,
            output_module_map=output_module_map,
            api_execution_step=api_execution_step,
            api_and_signature_detection_step=api_signature_port.value,
            default_output_module=default_output_module,
        )

    async def _run_filter_module(
        self,
        port: Port,
        api_signature_port: Port,
        config: Config,
    ):
        try:
            input_text = None
            if api_signature_port.value is None:
                raise PluginExecutionPipelineError(
                    message="API Signature Detection Error: No operations found."
                )
            api_called = api_signature_port.value.get("api_called")
            method = api_signature_port.value.get("method")
            filter_module = self.plugin.get_filter_module(api_called, method)
            if filter_module:
                input_text = json.dumps(port.value)
                port = await filter_module.run(port, config)
                output_text = json.dumps(port.value)
                self.tracing_steps.append(
                    {
                        "name": "filter_step",
                        "label": "API Response Filter Step",
                        "processing_time_seconds": port.get_metadata(
                            PortMetadata.PROCESSING_TIME_SECONDS
                        ),
                        "status_code": port.get_metadata(PortMetadata.STATUS_CODE),
                        "input_text": input_text,
                        "output_text": output_text,
                    }
                )
            return port
        except Exception as e:
            if port:
                self.tracing_steps.append(
                    {
                        "name": "filter_step",
                        "label": "API Response Filter Step",
                        "processing_time_seconds": port.get_metadata(
                            PortMetadata.PROCESSING_TIME_SECONDS
                        ),
                        "status_code": port.get_metadata(PortMetadata.STATUS_CODE),
                        "input_text": input_text,
                        "output_text": f"Error: {str(e)}",
                    }
                )
            raise PluginExecutionPipelineError(
                message="Filter Module Error: Not able to run the jinja template on the api response"
            )

    async def _output_module_processing(
        self,
        api_execution_step: APIExecutionStepResponse,
        api_signature_port: Port,
        config: Config,
        run_all_output_modules: bool = False,
        output_module_names: Optional[List[str]] = None,
    ):
        try:
            output_module_map = {}
            default_output_module = None
            processor_metadata = {}
            is_clarifying_response = False
            response_output_ports: List[Port] = []
            if api_execution_step.clarifying_response is None:
                flow_port = api_execution_step.original_response

                if api_signature_port.value is None:
                    raise PluginExecutionPipelineError(
                        message="API Signature Detection Error: No operations found."
                    )
                api_called = api_signature_port.value.get("api_called")
                method = api_signature_port.value.get("method")

                supported_output_modules = self.plugin.get_supported_output_modules(
                    operation=api_called, method=method
                )
                if run_all_output_modules and supported_output_modules:
                    for output_module in supported_output_modules:
                        processor_metadata[output_module.name] = (
                            output_module.get_processor_metadata()
                        )
                        o_ports = await asyncio.gather(
                            *(
                                run_module(output_module, flow_port, config)
                                for output_module in supported_output_modules
                            )
                        )
                        if o_ports:
                            response_output_ports.extend(o_ports)
                elif output_module_names and supported_output_modules:
                    selected_output_modules = []
                    for output_module in supported_output_modules:
                        if output_module.name in output_module_names:
                            processor_metadata[output_module.name] = (
                                output_module.get_processor_metadata()
                            )
                            selected_output_modules.append(output_module)
                    o_ports = await asyncio.gather(
                        *(
                            run_module(output_module, flow_port, config)
                            for output_module in selected_output_modules
                        )
                    )
                    if o_ports:
                        response_output_ports.extend(o_ports)
            else:
                is_clarifying_response = True
                default_output_module = "clarifying_response"
                output_module_map["clarifying_response"] = (
                    api_execution_step.clarifying_response
                )

            if not is_clarifying_response:
                if response_output_ports:
                    for output_port in response_output_ports:
                        self.add_output_module_trace(output_port, processor_metadata)
                        output_module_map[output_port.name] = output_port
                        if output_port.get_metadata(
                            PortMetadata.DEFAULT_OUTPUT_MODULE
                        ):
                            default_output_module = output_port.name

                # set the first one as default if not set in manifest
                if default_output_module is None and response_output_ports:
                    default_output_module = response_output_ports[0].name

                if (
                    output_module_names
                    and "original_response" in output_module_names
                ):
                    output_module_map["original_response"] = (
                        api_execution_step.original_response
                    )
                    default_output_module = "original_response"

            return output_module_map, default_output_module
        except Exception as e:
            raise PluginExecutionPipelineError(message=f"Output Module Error: {e}")

    async def _input_module_processing(
        self,
        input: Port,
        config: Config,
    ):
        try:
            flow_port = input
            flow_port.name = "default_no_change_input"
            flow_port.metadata = {
                PortMetadata.PROCESSING_TIME_SECONDS: 0,
                PortMetadata.STATUS_CODE: 200,
                PortMetadata.LOG_PROCESSOR_RUN: [
                    {
                        "label": "Input Module [Standard]",
                        "input_text": input.value,
                        "output_text": input.value,
                    }
                ],
            }
            if self.plugin.input_modules:
                for input_module in self.plugin.input_modules:
                    if (
                        input_module.initial_input_port.data_type
                        == flow_port.data_type
                    ):
                        logger.info(f"\n[RUNNING_INPUT_MODULE] {input_module}")
                        flow_port = await input_module.run(flow_port, config)
                        break
            self.add_input_module_trace(flow_port)
            return flow_port
        except Exception as e:
            raise PluginExecutionPipelineError(message=f"Input Module Error: {e}")

    def add_input_module_trace(self, input_module: Port):
        self.tracing_steps.append(
            {
                "name": "input_module_step",
                "label": "Input Module",
                "processing_time_seconds": input_module.get_metadata(
                    PortMetadata.PROCESSING_TIME_SECONDS
                ),
                "processor_logs": input_module.get_metadata(
                    PortMetadata.LOG_PROCESSOR_RUN, []
                ),
                "status_code": input_module.get_metadata(PortMetadata.STATUS_CODE),
            }
        )

    def add_signature_detection_trace(self, signature_port: Dict[Any, Any]):
        try:
            intermediate_fc_request = None
            if (
                signature_port.get("metadata", {}).get("intermediate_fc_request")
                is not None
            ):
                intermediate_fc_request = json.dumps(
                    signature_port.get("metadata", {}).get(
                        "intermediate_fc_request", {}
                    )
                )

            intermediate_fc_response = None
            if (
                signature_port.get("metadata", {}).get("intermediate_fc_response")
                is not None
            ):
                intermediate_fc_response = json.dumps(
                    signature_port.get("metadata", {}).get(
                        "intermediate_fc_response", {}
                    )
                )

            self.tracing_steps.append(
                {
                    "name": "api_and_signature_detection_step",
                    "label": "Signature Creation (w/ LLM)",
                    "processing_time_seconds": signature_port.get(
                        "metadata", {}
                    ).get("processing_time_seconds"),
                    "status_code": signature_port.get("metadata", {}).get(
                        "status_code"
                    ),
                    "input_text": signature_port.get("metadata", {}).get(
                        "input_text"
                    ),
                    "system_prompt": signature_port.get("metadata", {}).get(
                        "system_prompt"
                    ),
                    "conversations": signature_port.get("metadata", {}).get(
                        "conversations"
                    ),
                    "examples": signature_port.get("metadata", {}).get("examples"),
                    "intermediate_fc_request": intermediate_fc_request,
                    "intermediate_fc_response": intermediate_fc_response,
                    "x_dep_tracing": signature_port.get("metadata", {}).get(
                        "x_dep_tracing"
                    ),
                    "output_text": signature_port.get("metadata", {}).get(
                        "output_text"
                    ),
                }
            )
        except Exception as e:
            print(e)

    def add_api_execution_trace(self, api_execution_step):
        try:
            self.tracing_steps.append(
                {
                    "name": "api_execution_step",
                    "label": "API Execution",
                    "processing_time_seconds": api_execution_step.original_response.get_metadata(
                        PortMetadata.PROCESSING_TIME_SECONDS
                    ),
                    "status_code": api_execution_step.original_response.get_metadata(
                        PortMetadata.STATUS_CODE
                    ),
                    "input_text": api_execution_step.original_response.get_metadata(
                        PortMetadata.LOG_INPUT_TEXT
                    ),
                    "output_text": api_execution_step.original_response.get_metadata(
                        PortMetadata.LOG_OUTPUT_TEXT
                    ),
                    "x_lookup": api_execution_step.original_response.get_metadata(
                        PortMetadata.X_LOOKUP
                    ),
                    "missing_required_params": api_execution_step.original_response.get_metadata(
                        PortMetadata.MISSING_REQUIRED_PARAMS
                    ),
                }
            )
        except Exception as e:
            print(e)

    def add_output_module_trace(self, item: Port, metadata: dict):
        processor_logs = item.get_metadata(PortMetadata.LOG_PROCESSOR_RUN)
        transformed_metadata = {}
        for key, value in metadata.items():
            for key1, value1 in value.items():
                tranformed_key = key + " [" + key1 + "]"
                transformed_metadata[tranformed_key] = value1
        for processor_log in processor_logs:
            processor_log["metadata"] = transformed_metadata.get(
                processor_log.get("label"), {}
            )

        self.tracing_steps.append(
            {
                "name": item.name,
                "is_output_module": True,
                "label": f"Output Module [ {item.name.replace('_',' ')} ]",
                "parallel": True,
                "processing_time_seconds": item.get_metadata(
                    PortMetadata.PROCESSING_TIME_SECONDS
                ),
                "processor_logs": processor_logs,
                "status_code": item.get_metadata(PortMetadata.STATUS_CODE),
            }
        )

    @time_taken
    def _run_plugin_signature_selector(
        self,
        input: Port,
        config: Config,
        function_provider: FunctionProvider,
        conversation: Optional[List] = [],
        selected_operation: Optional[str] = None,
        header: Optional[dict] = None,
    ) -> Port:
        if input.data_type != PortType.TEXT:
            raise Exception("Input data type to plugin must be text.")
        if input.value is None:
            raise PortValueError("Input value cannot be None")
        messages = [
            Message(content=input.value, message_type=MessageType.HumanMessage)
        ]
        logger.info(f"\n[RUNNING_PLUGIN_SIGNATURE] provider]={function_provider}")
        # API signature selector
        oai_selector = CustomOperationSignatureBuilder(
            plugin=self.plugin,
            function_provider=function_provider,
            config=config,
            selected_operation=selected_operation,
            header=header,
        )
        response = oai_selector.run(messages, conversation=conversation)

        ops = response.detected_plugin_operations
        if ops and len(ops) > 0:
            status_code = 500
            if response.run_completed:
                status_code = 200
            output_port_json = {
                "api_called": ops[0].api_called,
                "method": ops[0].method,
                "mapped_operation_parameters": ops[0].mapped_operation_parameters,
            }
            val = {
                "api_called": ops[0].api_called,
                "method": ops[0].method,
                "path": ops[0].path,
                "metadata": {
                    "processing_time_seconds": response.response_time,
                    "tokens_used": response.tokens_used,
                    "llm_api_cost": response.llm_api_cost,
                    "status_code": status_code,
                    "input_text": response.modified_input_prompt,
                    "output_text": output_port_json,
                    "intermediate_fc_request": response.function_request_json,
                    "intermediate_fc_response": response.function_response_json,
                    "x_dep_tracing": response.x_dep_tracing,
                    "system_prompt": response.system_prompt,
                    "conversations": response.conversations,
                    "examples": response.examples,
                },
                "mapped_operation_parameters": ops[0].mapped_operation_parameters,
                "response_obj_200": response.response_obj_200,
            }
            self.add_signature_detection_trace(val)
            return Port(data_type=PortType.JSON, value=val)
        else:
            val = {
                "api_called": None,
                "method": None,
                "mapped_operation_parameters": None,
                "metadata": {
                    "processing_time_seconds": response.response_time,
                    "tokens_used": response.tokens_used,
                    "llm_api_cost": response.llm_api_cost,
                    "status_code": 500,
                    "input_text": str(input.value),
                    "output_text": "No operations found",
                    "intermediate_fc_request": response.function_request_json,
                    "intermediate_fc_response": response.function_response_json,
                    "x_dep_tracing": response.x_dep_tracing,
                    "system_prompt": response.system_prompt,
                    "conversations": response.conversations,
                    "examples": response.examples,
                },
            }
            self.add_signature_detection_trace(val)
            if response.run_completed is False:
                raise PluginExecutionPipelineError(
                    message=f"Failed to run plugin signature selector. {response.final_text_response}"
                )
            else:
                raise PluginExecutionPipelineError(message="No operations found.")

    @time_taken
    def _run_plugin_execution(
        self,
        input: Port,
        config: Config,
        header: dict,
        auth_query_param: Optional[dict],
        function_provider: FunctionProvider,
        enable_ui_form_controls: bool = True,
    ) -> APIExecutionStepResponse:
        if input.data_type != PortType.JSON:
            raise Exception("Input data type to plugin must be JSON.")
        if input.value is None:
            raise PortValueError("Input value cannot be None")
        try:
            api_called = input.value.get("api_called")
            method = input.value.get("method")
            query_params = input.value.get("mapped_operation_parameters")
            response_obj_200 = input.value.get("response_obj_200")
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

            input_port_json = {
                "api_called": api_called,
                "method": method,
                "mapped_operation_parameters": query_params,
            }
            logger.info(
                f"\n[RUNNING_PLUGIN_EXECUTION] url={api_called}, method={method}"
            )
            if auth_query_param:
                query_params.update(auth_query_param)
            params = OperationExecutionParams(
                config=config,
                api=api_called,
                path=input.value.get("path"),
                method=method,
                query_params=query_params,
                body={},
                header=header,
                response_obj_200=response_obj_200,
                function_provider=function_provider,
                plugin_op_property_map=self.plugin.plugin_op_property_map,
                enable_ui_form_controls=enable_ui_form_controls,
            )
            ex = OperationExecutionWithImprompt(params)
            response = ex.run()
            # original port
            if isinstance(response.original_response, dict):
                output_text = json.dumps(response.original_response)
            else:
                output_text = str(response.original_response)
            original_port = Port(
                name="original_response",
                data_type=PortType.JSON,
                value=response.original_response,
                metadata={
                    PortMetadata.PROCESSING_TIME_SECONDS: response.api_call_response_seconds,
                    PortMetadata.STATUS_CODE: response.api_call_status_code,
                    PortMetadata.LOG_INPUT_TEXT: input_port_json,
                    PortMetadata.LOG_OUTPUT_TEXT: output_text,
                    PortMetadata.X_LOOKUP: response.x_lookup_tracing,
                    PortMetadata.MISSING_REQUIRED_PARAMS: response.missing_params,
                },
            )
            # clarifying question
            clarifying_port = None
            if response.clarifying_response is not None:
                clarifying_port = Port(
                    name="clarifying_response",
                    data_type=PortType.TEXT,
                    value=response.clarifying_response,
                    metadata={
                        PortMetadata.PROCESSING_TIME_SECONDS: response.clarifying_question_response_seconds,
                        PortMetadata.STATUS_CODE: response.clarifying_question_status_code,
                        PortMetadata.LOG_INPUT_TEXT: input_port_json,
                        PortMetadata.LOG_OUTPUT_TEXT: str(
                            response.original_response
                        ),
                        PortMetadata.MISSING_REQUIRED_PARAMS: response.missing_params,
                    },
                )
            logger.info(f"\n[PLUGIN_EXECUTION_RESPONSE] {original_port.value}")
            api_execution_step = APIExecutionStepResponse(
                original_response=original_port,
                clarifying_response=clarifying_port,
            )
            self.add_api_execution_trace(api_execution_step)
            return api_execution_step
        except Exception as e:
            api_execution_step = APIExecutionStepResponse(
                original_response=Port(
                    name="original_response",
                    data_type=PortType.JSON,
                    value={},
                    metadata={
                        PortMetadata.PROCESSING_TIME_SECONDS: None,
                        PortMetadata.STATUS_CODE: 500,
                        PortMetadata.LOG_INPUT_TEXT: input_port_json,
                        PortMetadata.LOG_OUTPUT_TEXT: None,
                    },
                ),
                clarifying_response=None,
            )
            self.add_api_execution_trace(api_execution_step)
            raise PluginExecutionPipelineError(message=f"API Execution Error: {e}")

    def add_tokens(self, port: Port):
        if port:
            token = port.get_total_tokens_used()
            if token:
                self.total_tokens_used += token
            cost = port.get_total_cost()
            if cost:
                self.total_cost += port.get_total_cost()
