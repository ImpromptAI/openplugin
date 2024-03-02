import json

from openplugin.core.llms import LLM, Config
from openplugin.core.messages import Message
from openplugin.core.operations.implementations.operation_signature_builder_with_imprompt import (
    ImpromptOperationSignatureBuilder,
)
from openplugin.core.operations.implementations.operation_signature_builder_with_openai import (
    OpenAIOperationSignatureBuilder,
)
from openplugin.core.plugin import Plugin
from openplugin.core.selectors.implementations.plugin_selector_with_imprompt import (
    ImpromptPluginSelector,
)
from openplugin.core.selectors.implementations.plugin_selector_with_openai import (
    OpenAIPluginSelector,
)


# Function to run a plugin selector based on input JSON
def run_plugin_selector(inp_json):
    if isinstance(inp_json, str):
        inp_json = json.loads(inp_json)

    # Convert input JSON into Python objects
    messages = [Message(**m) for m in inp_json["messages"]]
    plugins = [Plugin(**p) for p in inp_json["plugins"]]
    config = Config(**inp_json["config"])
    llm = LLM(**inp_json["llm"])
    pipeline_name = inp_json["pipeline_name"]
    # Check the provider specified in tool_selector_config and select the
    # appropriate plugin selector
    if pipeline_name.lower() == ImpromptPluginSelector.get_pipeline_name().lower():
        selector = ImpromptPluginSelector(plugins=plugins, config=config, llm=llm)
        response = selector.run(messages)
        return response.dict()
    elif pipeline_name.lower() == OpenAIPluginSelector.get_pipeline_name().lower():
        selector = OpenAIPluginSelector(plugins=plugins, config=config, llm=llm)
        response = selector.run(messages)
        return response.dict()
    raise Exception("Unknown tool selector provider")


# Function to run an API signature selector based on input JSON
def run_api_signature_selector(inp_json):
    if isinstance(inp_json, str):
        inp_json = json.loads(inp_json)

    # Convert input JSON into Python objects
    messages = [Message(**m) for m in inp_json["messages"]]
    plugin = Plugin(**inp_json["plugin"])
    config = Config(**inp_json["config"])
    pipeline_name = inp_json["pipeline_name"]
    llm = LLM(**inp_json["llm"])

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
        return response.dict()
    elif pipeline_name.lower() == "LLM Passthrough (Stuffed Swagger)".lower():
        imprompt_selector = ImpromptOperationSignatureBuilder(
            plugin=plugin, config=config, llm=llm, use="stuffed-swagger"
        )
        response = imprompt_selector.run(messages)
        return response.dict()
    elif pipeline_name.lower() == "LLM Passthrough (Bare Swagger)".lower():
        imprompt_selector = ImpromptOperationSignatureBuilder(
            plugin=plugin, config=config, llm=llm, use="bare-swagger"
        )
        response = imprompt_selector.run(messages)
        return response.dict()
    elif (
        pipeline_name.lower()
        == ImpromptOperationSignatureBuilder.get_pipeline_name().lower()
    ):
        selector = ImpromptOperationSignatureBuilder(plugin, config, llm)
        response = selector.run(messages)
        return response.dict()
    elif (
        pipeline_name.lower()
        == OpenAIOperationSignatureBuilder.get_pipeline_name().lower()
    ):
        selector = OpenAIOperationSignatureBuilder(plugin, config, llm)
        response = selector.run(messages)
        return response.dict()
    raise Exception("Unknown tool selector provider")
