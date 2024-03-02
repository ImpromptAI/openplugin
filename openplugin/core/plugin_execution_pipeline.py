import asyncio
from typing import Dict, List, Optional

from loguru import logger
from pydantic import BaseModel

from .execution.implementations.operation_execution_with_imprompt import (
    OperationExecutionParams,
    OperationExecutionWithImprompt,
)
from .helper import time_taken
from .llms import Config
from .messages import Message, MessageType
from .operations.implementations.operation_signature_builder_with_imprompt import (
    ImpromptOperationSignatureBuilder,
)
from .operations.implementations.operation_signature_builder_with_openai import (
    OpenAIOperationSignatureBuilder,
)
from .plugin import Plugin, PreferredApproach
from .port import Port, PortMetadata, PortType, PortValueError


async def run_module(output_module, flow_port):
    logger.info(f"\n[RUNNING_OUTPUT_MODULE] {output_module}")
    output_port = await output_module.run(flow_port)
    output_port.name = output_module.name
    output_port.metadata = {
        PortMetadata.PROCESSING_TIME_SECONDS: 0,
        PortMetadata.STATUS_CODE: 200,
    }
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
    default_output: Port


class PluginExecutionPipeline(BaseModel):
    plugin: Plugin

    async def start(
        self,
        input: Port,
        config: Config,
        preferred_approach: PreferredApproach,
        output_module_ids: Optional[List[str]] = None,
    ) -> PluginExecutionResponse:
        flow_port = input
        flow_port.name = "default_no_change_input"
        flow_port.metadata = {
            PortMetadata.PROCESSING_TIME_SECONDS: 0,
            PortMetadata.STATUS_CODE: 200,
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
            input=flow_port, config=config, preferred_approach=preferred_approach
        )

        logger.info(f"\n[PLUGIN_SIGNATURE_RESPONSE] {api_signature_port.value}")
        api_execution_step = self._run_plugin_execution(
            input=api_signature_port,
            config=config,
            preferred_approach=preferred_approach,
        )
        if api_execution_step.clarifying_response is None:
            flow_port = api_execution_step.original_response
            response_output_ports: List[Port] = []
            if output_module_ids and self.plugin.output_modules:
                selected_output_modules = []
                for output_module in self.plugin.output_modules:
                    if output_module.id in output_module_ids:
                        selected_output_modules.append(output_module)
                o_ports = await asyncio.gather(
                    *(
                        run_module(output_module, flow_port)
                        for output_module in selected_output_modules
                    )
                )
                if o_ports:
                    response_output_ports.extend(o_ports)
        # TODO change this
        default_output = api_execution_step.original_response
        output_module_map = {}
        if response_output_ports:
            for output_port in response_output_ports:
                output_module_map[output_port.name] = output_port
        return PluginExecutionResponse(
            input_modules=input_modules,
            output_module_map=output_module_map,
            api_execution_step=api_execution_step,
            api_and_signature_detection_step=api_signature_port.value,
            default_output=default_output,
        )

    @time_taken
    def _run_plugin_signature_selector(
        self,
        input: Port,
        config: Config,
        preferred_approach: PreferredApproach,
    ) -> Port:
        if input.data_type != PortType.TEXT:
            raise Exception("Input data type to plugin must be text.")
        if input.value is None:
            raise PortValueError("Input value cannot be None")
        messages = [Message(content=input.value, message_type=MessageType.HumanMessage)]
        pipeline_name = preferred_approach.base_strategy
        llm = preferred_approach.llm
        logger.info(f"\n[RUNNING_PLUGIN_SIGNATURE] pipeline={pipeline_name}, {llm}")
        # API signature selector
        if (
            pipeline_name.lower() == "LLM Passthrough (OpenPlugin and Swagger)".lower()
            or pipeline_name.lower() == "LLM Passthrough (OpenPlugin + Swagger)".lower()
        ):
            imprompt_selector = ImpromptOperationSignatureBuilder(
                plugin=self.plugin, config=config, llm=llm, use="openplugin-swagger"
            )
            response = imprompt_selector.run(messages)
        elif pipeline_name.lower() == "LLM Passthrough (Stuffed Swagger)".lower():
            imprompt_selector = ImpromptOperationSignatureBuilder(
                plugin=self.plugin, config=config, llm=llm, use="stuffed-swagger"
            )
            response = imprompt_selector.run(messages)
        elif pipeline_name.lower() == "LLM Passthrough (Bare Swagger)".lower():
            imprompt_selector = ImpromptOperationSignatureBuilder(
                plugin=self.plugin, config=config, llm=llm, use="bare-swagger"
            )
            response = imprompt_selector.run(messages)
        elif (
            pipeline_name.lower()
            == ImpromptOperationSignatureBuilder.get_pipeline_name().lower()
        ):
            selector = ImpromptOperationSignatureBuilder(self.plugin, config, llm)
            response = selector.run(messages)
        elif (
            pipeline_name.lower()
            == OpenAIOperationSignatureBuilder.get_pipeline_name().lower()
        ):
            oai_selector = OpenAIOperationSignatureBuilder(self.plugin, config, llm)
            response = oai_selector.run(messages)
        else:
            raise Exception("Unknown tool selector provider")
        ops = response.detected_plugin_operations
        if ops and len(ops) > 0:
            status_code = 500
            if response.run_completed:
                status_code = 200
            val = {
                "api_called": ops[0].api_called,
                "method": ops[0].method,
                "metadata": {
                    "processing_time_seconds": response.response_time,
                    "tokens_used": response.tokens_used,
                    "llm_api_cost": response.llm_api_cost,
                    "status_code": status_code,
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
        preferred_approach: PreferredApproach,
    ) -> APIExecutionStepResponse:
        if input.data_type != PortType.JSON:
            raise Exception("Input data type to plugin must be JSON.")
        if input.value is None:
            raise PortValueError("Input value cannot be None")

        api_called = input.value.get("api_called")
        method = input.value.get("method")
        query_params = input.value.get("mapped_operation_parameters")
        logger.info(f"\n[RUNNING_PLUGIN_EXECUTION] url={api_called}, method={method}")
        params = OperationExecutionParams(
            config=config,
            api=api_called,
            method=method,
            query_params=query_params,
            body={},
            header={},
            llm=preferred_approach.llm,
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
                },
            )
        logger.info(f"\n[PLUGIN_EXECUTION_RESPONSE] {original_port.value}")
        return APIExecutionStepResponse(
            original_response=original_port,
            clarifying_response=clarifying_port,
        )
