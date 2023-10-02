import os

from openplugin.bindings.imprompt.imprompt_plugin_selector import (
    ImpromptPluginSelector,
)
from openplugin.interfaces.models import (
    LLM,
    Config,
    LLMProvider,
    Message,
    MessageType,
    Plugin,
    ToolSelectorConfig,
    ToolSelectorProvider,
)


def test_klarna_plugins():
    # build messages
    message1 = Message(
        content="Show me t shirts from Klarna?",
        message_type=MessageType.HumanMessage,
    )
    messages = [message1]

    tool_selector_config = ToolSelectorConfig(
        provider=ToolSelectorProvider.Imprompt, pipeline_name="default"
    )

    plugin1 = Plugin(
        manifest_url="https://assistant-management-data.s3.amazonaws.com/Klarna_Shopping.json"
    )
    plugins = [plugin1]
    # ADD YOU OPENAI API KEY HERE
    config = Config(openai_api_key=os.environ["OPENAI_API_KEY"])
    llm = LLM(
        provider=LLMProvider.OpenAIChat,
        model_name="gpt-3.5-turbo",
    )
    selector = ImpromptPluginSelector(
        tool_selector_config=tool_selector_config,
        plugins=plugins,
        config=config,
        llm=llm,
    )
    response = selector.run(messages)
    print(response)
    detected_plugin_names = [
        plugin_operation.plugin.name
        for plugin_operation in response.detected_plugin_operations
    ]
    assert response.run_completed
    assert "Klarna Shopping" in detected_plugin_names
