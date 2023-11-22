import os

from dotenv import load_dotenv

from openplugin.bindings.imprompt.imprompt_plugin_selector import (
    ImpromptPluginSelector,
)
from openplugin.interfaces.models import (
    LLM,
    Config,
    Message,
    MessageType,
    Plugin,
)


def test_klarna_plugins():
    load_dotenv()
    # build messages
    message1 = Message(
        content="Show me t shirts from Klarna?",
        message_type=MessageType.HumanMessage,
    )
    messages = [message1]

    plugin1 = Plugin(
        manifest_url="https://assistant-management-data.s3.amazonaws.com/Klarna_Shopping.json"
    )
    plugins = [plugin1]
    # ADD YOU OPENAI API KEY HERE
    config = Config(openai_api_key=os.environ["OPENAI_API_KEY"])
    llm = LLM(
        provider="openai",
        model_name="gpt-3.5-turbo",
    )
    selector = ImpromptPluginSelector(
        plugins=plugins,
        config=config,
        llm=llm,
    )
    response = selector.run(messages)
    detected_plugin_names = [
        plugin_operation.plugin.name
        for plugin_operation in response.detected_plugin_operations
    ]
    assert response.run_completed
    assert "Klarna Shopping" in detected_plugin_names
