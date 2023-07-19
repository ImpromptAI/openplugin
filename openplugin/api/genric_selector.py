from typing import List
from fastapi import APIRouter, Depends
from openplugin import LangchainPluginSelector
from openplugin import Message, LLM, Plugin, ToolSelectorConfig, Config, \
    ToolSelectorProvider
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKey
from openplugin.api import auth
from openplugin import ImpromptPluginSelector
from openplugin import OpenAIPluginSelector

router = APIRouter(
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.post("/plugin-selector")
def run_plugin(
        messages: List[Message],
        tool_selector_config: ToolSelectorConfig,
        plugins: List[Plugin],
        config: Config,
        llm: LLM,
        api_key: APIKey = Depends(auth.get_api_key)
):
    if tool_selector_config.provider == ToolSelectorProvider.Imprompt:
        selector = ImpromptPluginSelector(tool_selector_config, plugins, config, llm)
    elif tool_selector_config.provider == ToolSelectorProvider.Langchain:
        selector = LangchainPluginSelector(tool_selector_config, plugins, config, llm)
    elif tool_selector_config.provider == ToolSelectorProvider.OpenAI:
        selector = OpenAIPluginSelector(tool_selector_config, plugins, config, llm)
    else:
        return JSONResponse(status_code=400,
                            content={"message": "Incorrect ToolSelectorProvider"})
    try:
        response = selector.run(messages)
        return response
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500,
                            content={"message": "Failed to run plugin"})
