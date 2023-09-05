import json
from openplugin import Message, Plugin, Config, ToolSelectorConfig, \
    LLM, ToolSelectorProvider


# Function to run a plugin selector based on input JSON
def run_plugin_selector(inp_json):
    if type(inp_json) == str:
        inp_json = json.loads(inp_json)

    # Convert input JSON into Python objects
    messages = [Message(**m) for m in inp_json["messages"]]
    plugins = [Plugin(**p) for p in inp_json["plugins"]]
    config = Config(**inp_json["config"])
    tool_selector_config = ToolSelectorConfig(**inp_json["tool_selector_config"])
    llm = LLM(**inp_json["llm"])

    # Check the provider specified in tool_selector_config and select the appropriate plugin selector
    if tool_selector_config.provider == ToolSelectorProvider.Imprompt:
        from openplugin.bindings.imprompt.imprompt_plugin_selector import \
            ImpromptPluginSelector
        selector = ImpromptPluginSelector(tool_selector_config, plugins, config, llm)
        response = selector.run(messages)
        return response.dict()
    elif tool_selector_config.provider == ToolSelectorProvider.Langchain:
        from openplugin.bindings.langchain.langchain_plugin_selector import \
            LangchainPluginSelector
        selector = LangchainPluginSelector(tool_selector_config, plugins, config, llm)
        response = selector.run(messages)
        return response.dict()
    elif tool_selector_config.provider == ToolSelectorProvider.OpenAI:
        from openplugin.bindings.openai.openai_plugin_selector import \
            OpenAIPluginSelector
        selector = OpenAIPluginSelector(tool_selector_config, plugins, config, llm)
        response = selector.run(messages)
        return response.dict()
    raise Exception("Unknown tool selector provider")


# Function to run an API signature selector based on input JSON
def run_api_signature_selector(inp_json):
    if type(inp_json) == str:
        inp_json = json.loads(inp_json)

    # Convert input JSON into Python objects
    messages = [Message(**m) for m in inp_json["messages"]]
    plugin = Plugin(**inp_json["plugin"])
    config = Config(**inp_json["config"])
    tool_selector_config = ToolSelectorConfig(**inp_json["tool_selector_config"])
    llm = LLM(**inp_json["llm"])

    # Check the provider specified in tool_selector_config and select the appropriate API signature selector
    if tool_selector_config.provider == ToolSelectorProvider.Imprompt:
        from openplugin.bindings.imprompt.imprompt_operation_signature_builder import \
            ImpromptOperationSignatureBuilder
        selector = ImpromptOperationSignatureBuilder(tool_selector_config, plugin,
                                                     config, llm)
        response = selector.run(messages)
        return response.dict()
    elif tool_selector_config.provider == ToolSelectorProvider.Langchain:
        from openplugin.bindings.langchain.langchain_operation_signature_selector import \
            LangchainOperationSignatureBuilder
        selector = LangchainOperationSignatureBuilder(tool_selector_config, plugin,
                                                      config, llm)
        response = selector.run(messages)
        return response.dict()
    elif tool_selector_config.provider == ToolSelectorProvider.OpenAI:
        from openplugin.bindings.openai.openai_operation_signature_builder import \
            OpenAIOperationSignatureBuilder
        selector = OpenAIOperationSignatureBuilder(tool_selector_config, plugin,
                                                   config, llm)
        response = selector.run(messages)
        return response.dict()
    raise Exception("Unknown tool selector provider")
