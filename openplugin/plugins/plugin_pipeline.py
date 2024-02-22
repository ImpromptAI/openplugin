import asyncio
from typing import List

from loguru import logger
from pydantic import BaseModel

from . import time_taken
from .execution.operation_execution_impl import (
    OperationExecutionImpl,
)
from .models import (
    Config,
    Message,
    MessageType,
    OperationExecutionParams,
    PreferredApproach,
)
from .operations.operation_signature_builder_with_imprompt import (
    ImpromptOperationSignatureBuilder,
)
from .operations.operation_signature_builder_with_openai import (
    OpenAIOperationSignatureBuilder,
)
from .plugin import Plugin
from .port import Port, PortType, PortValueError


async def run_module(output_module, flow_port):
    logger.info(f"\n[RUNNING_OUTPUT_MODULE] {output_module}")
    output_port = await output_module.run(flow_port)
    logger.info(f"\n[FINAL_RESPONSE] {output_port.value}")
    return output_port


class PluginPipeline(BaseModel):
    plugin: Plugin

    async def start(
        self,
        input: Port,
        outputs: List[PortType],
        config: Config,
        preferred_approach: PreferredApproach,
    ) -> List[Port]:
        flow_port = input
        for input_module in self.plugin.input_modules:
            if input_module.initial_input_port.data_type == flow_port.data_type:
                logger.info(f"\n[RUNNING_INPUT_MODULE] {input_module}")
                flow_port = await input_module.run(flow_port)
                break

        flow_port = self._run_plugin(
            input=flow_port,
            config=config,
            preferred_approach=preferred_approach,
        )

        output_ports: List[Port] = []

        expected_output_types = [output for output in outputs]
        selected_output_modules = [
            output_module
            for output_module in self.plugin.output_modules
            if output_module.finish_output_port.data_type in expected_output_types
        ]
        output_ports = await asyncio.gather(
            *(
                run_module(output_module, flow_port)
                for output_module in selected_output_modules
            )
        )

        return output_ports

    def _run_plugin(
        self,
        input: Port,
        config: Config,
        preferred_approach: PreferredApproach,
    ) -> Port:
        api_signature_port = self._run_plugin_signature_selector(
            input, config, preferred_approach
        )
        logger.info(f"\n[PLUGIN_SIGNATURE_RESPONSE] {api_signature_port.value}")
        return self._run_plugin_execution(
            input=api_signature_port,
            config=config,
            preferred_approach=preferred_approach,
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
            val = {
                "api_called": ops[0].api_called,
                "method": ops[0].method,
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
    ) -> Port:
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
            post_processing_cleanup_prompt="",
            llm=preferred_approach.llm,
            plugin_response_template_engine="",
            plugin_response_template="",
            post_call_evaluator_prompt="",
        )
        ex = OperationExecutionImpl(params)
        response = ex.run()
        port = Port(data_type=PortType.JSON, value=response.original_response)
        logger.info(f"\n[PLUGIN_EXECUTION_RESPONSE] {port.value}")
        return port
