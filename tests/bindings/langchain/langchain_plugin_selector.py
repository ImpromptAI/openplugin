import os
from dotenv import load_dotenv
from openplugin import LangchainPluginSelector
from openplugin import LLM, LLMProvider, Config, Message, MessageType, ToolSelectorConfig, \
    ToolSelectorProvider, Plugin


def test_klarna_plugins():
    # build messages
    message1 = Message(
        content="Show me t shirts from Klarna?",
        message_type=MessageType.HumanMessage
    )
    messages = [message1]

    tool_selector_config = ToolSelectorConfig(
        provider=ToolSelectorProvider.Langchain,
        pipeline_name="zero-shot-react-description"
    )

    plugin1 = Plugin(manifest_url="https://www.klarna.com/.well-known/ai-plugin.json")
    plugins = [plugin1]
    # ADD YOU OPENAI API KEY HERE
    config = Config(openai_api_key=os.environ["OPENAI_API_KEY"])
    llm = LLM(
        provider=LLMProvider.OpenAIChat,
        model_name="gpt-3.5-turbo",
    )
    selector = LangchainPluginSelector(
        tool_selector_config=tool_selector_config,
        plugins=plugins,
        config=config,
        llm=llm
    )
    response = selector.run(messages)
    print(response)
    detected_plugin_names = [plugin_operation.plugin.name_for_model for plugin_operation in
                             response.detected_plugin_operations]
    assert response.run_completed
    assert 'KlarnaProducts' in detected_plugin_names
