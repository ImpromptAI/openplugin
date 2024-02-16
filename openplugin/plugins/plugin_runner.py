from typing import List

from loguru import logger

from openplugin.plugins.execution.operation_execution_impl import (
    OperationExecutionImpl,
)
from openplugin.plugins.models import (
    Config,
    Message,
    MessageType,
    OperationExecutionParams,
    PreferredApproach,
)
from openplugin.plugins.operations.operation_signature_builder_with_imprompt import (
    ImpromptOperationSignatureBuilder,
)
from openplugin.plugins.operations.operation_signature_builder_with_openai import (
    OpenAIOperationSignatureBuilder,
)
from openplugin.plugins.plugin import Plugin
from openplugin.plugins.port import Port, PortType


def run_plugin_pipeline(
    plugin: Plugin,
    input: Port,
    outputs: List[Port],
    config: Config,
    preferred_approach: PreferredApproach,
) -> List[Port]:
    flow_port = input
    for input_module in plugin.input_modules:
        if input_module.initial_input_port.data_type == flow_port.data_type:
            logger.info(f"\n[RUNNING_INPUT_MODULE] {input_module}")
            flow_port = input_module.run(flow_port)
            break

    flow_port = run_plugin(
        plugin=plugin,
        input=flow_port,
        config=config,
        preferred_approach=preferred_approach,
    )

    output_ports: List[Port] = []
    expected_output_types = [output for output in outputs]
    for output_module in plugin.output_modules:
        if output_module.finish_output_port.data_type in expected_output_types:
            logger.info(f"\n[RUNNING_OUTPUT_MODULE] {output_module}")
            output_port = output_module.run(flow_port)
            output_ports.append(output_port)
            logger.info(f"\n[FINAL_RESPONSE] {output_port.value}")

    return output_ports


def run_plugin(
    plugin: Plugin,
    input: Port,
    config: Config,
    preferred_approach: PreferredApproach,
) -> Port:
    api_signature_port = run_plugin_signature_selector(
        plugin, input, config, preferred_approach
    )
    logger.info(f"\n[PLUGIN_SIGNATURE_RESPONSE] {api_signature_port.value}")
    return run_plugin_execution(
        plugin=plugin,
        input=api_signature_port,
        config=config,
        preferred_approach=preferred_approach,
    )


def run_plugin_execution(
    plugin: Plugin,
    input: Port,
    config: Config,
    preferred_approach: PreferredApproach,
) -> Port:
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


def run_plugin_signature_selector(
    plugin: Plugin,
    input: Port,
    config: Config,
    preferred_approach: PreferredApproach,
) -> Port:
    if input.data_type != PortType.TEXT:
        raise Exception("Input data type to plugin must be text.")
    messages = [Message(content=input.value, message_type=MessageType.HumanMessage)]
    pipeline_name = preferred_approach.base_strategy
    llm = preferred_approach.llm
    logger.info(f"\n[RUNNING_PLUGIN_SIGNATURE] pipeline={pipeline_name}, {llm}")
    # Check the provider specified in tool_selector_config and select the appropriate
    # API signature selector
    if (
        pipeline_name.lower() == "LLM Passthrough (OpenPlugin and Swagger)".lower()
        or pipeline_name.lower() == "LLM Passthrough (OpenPlugin + Swagger)".lower()
    ):
        imprompt_selector = ImpromptOperationSignatureBuilder(
            plugin=plugin, config=config, llm=llm, use="openplugin-swagger"
        )
        response = imprompt_selector.run(messages)
    elif pipeline_name.lower() == "LLM Passthrough (Stuffed Swagger)".lower():
        imprompt_selector = ImpromptOperationSignatureBuilder(
            plugin=plugin, config=config, llm=llm, use="stuffed-swagger"
        )
        response = imprompt_selector.run(messages)
    elif pipeline_name.lower() == "LLM Passthrough (Bare Swagger)".lower():
        imprompt_selector = ImpromptOperationSignatureBuilder(
            plugin=plugin, config=config, llm=llm, use="bare-swagger"
        )
        response = imprompt_selector.run(messages)
    elif (
        pipeline_name.lower()
        == ImpromptOperationSignatureBuilder.get_pipeline_name().lower()
    ):
        selector = ImpromptOperationSignatureBuilder(plugin, config, llm)
        response = selector.run(messages)
    elif (
        pipeline_name.lower()
        == OpenAIOperationSignatureBuilder.get_pipeline_name().lower()
    ):
        oai_selector = OpenAIOperationSignatureBuilder(plugin, config, llm)
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
