import json
from openplugin.interfaces.plugin_selector import Message, Plugin, Config, ToolSelectorConfig, LLM, ToolSelectorProvider


def run_plugin_selector(inp_json):
    if type(inp_json) == str:
        inp_json = json.loads(inp_json)
    messages = [Message(**m) for m in inp_json["messages"]]
    plugins = [Plugin(**p) for p in inp_json["plugins"]]
    config = Config(**inp_json["config"])
    tool_selector_config = ToolSelectorConfig(**inp_json["tool_selector_config"])
    llm = LLM(**inp_json["llm"])

    if tool_selector_config.provider == ToolSelectorProvider.Imprompt:
        from openplugin.bindings.imprompt.imprompt_plugin_selector import ImpromptPluginSelector
        selector = ImpromptPluginSelector(tool_selector_config, plugins, config, llm)
        response = selector.run(messages)
        return response.dict()
    elif tool_selector_config.provider == ToolSelectorProvider.Langchain:
        from openplugin.bindings.langchain.langchain_plugin_selector import LangchainPluginSelector
        selector = LangchainPluginSelector(tool_selector_config, plugins, config, llm)
        response = selector.run(messages)
        return response.dict()
    raise Exception("Unknown tool selector provider")
