from typing import List
from fastapi import APIRouter
from bindings.langchain.langchain_plugin_selector import LangchainPluginSelector
from interfaces.plugin_selector import Message, LLM, Plugin, ToolSelectorConfig, Config

router = APIRouter(
    prefix="/langchain",
    tags=["langchain"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.post("/run-plugin")
def run_plugin(
        messages: List[Message],
        tool_selector_config: ToolSelectorConfig,
        plugins: List[Plugin],
        config: Config,
        llm: LLM,
):
    selector = LangchainPluginSelector(tool_selector_config, plugins, config, llm)
    response = selector.run(messages)
    return response
