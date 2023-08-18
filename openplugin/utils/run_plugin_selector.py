import json
from openplugin import Message, Plugin, Config, ToolSelectorConfig, \
    LLM, ToolSelectorProvider


def run_plugin_selector(inp_json):
    if type(inp_json) == str:
        inp_json = json.loads(inp_json)
    messages = [Message(**m) for m in inp_json["messages"]]
    plugins = [Plugin(**p) for p in inp_json["plugins"]]
    config = Config(**inp_json["config"])
    tool_selector_config = ToolSelectorConfig(**inp_json["tool_selector_config"])
    llm = LLM(**inp_json["llm"])

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


def run_api_signature_selector(inp_json):
    if type(inp_json) == str:
        inp_json = json.loads(inp_json)
    messages = [Message(**m) for m in inp_json["messages"]]
    plugins = [Plugin(**p) for p in inp_json["plugins"]]
    config = Config(**inp_json["config"])
    tool_selector_config = ToolSelectorConfig(**inp_json["tool_selector_config"])
    llm = LLM(**inp_json["llm"])
    if tool_selector_config.provider == ToolSelectorProvider.Imprompt:
        from openplugin.bindings.imprompt.imprompt_api_signature_selector import \
            ImpromptApiSignatureSelector
        selector = ImpromptApiSignatureSelector(tool_selector_config, plugins[0],
                                                config, llm)
        response = selector.run(messages)
        return response.dict()
    elif tool_selector_config.provider == ToolSelectorProvider.Langchain:
        from openplugin.bindings.langchain.langchain_api_signature_selector import \
            LangchainApiSignatureSelector
        selector = LangchainApiSignatureSelector(tool_selector_config, plugins[0],
                                                 config, llm)
        response = selector.run(messages)
        return response.dict()
    elif tool_selector_config.provider == ToolSelectorProvider.OpenAI:
        from openplugin.bindings.openai.openai_api_signature_selector import \
            OpenAIApiSignatureSelector
        selector = OpenAIApiSignatureSelector(tool_selector_config, plugins[0],
                                              config, llm)
        response = selector.run(messages)
        return response.dict()
    raise Exception("Unknown tool selector provider")
