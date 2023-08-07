from typing import List
from openplugin.api import auth
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from openplugin import OpenAIApiSignatureSelector
from fastapi.security.api_key import APIKey
from openplugin import ImpromptApiSignatureSelector
from openplugin import LangchainApiSignatureSelector
from openplugin import Message, LLM, Plugin, ToolSelectorConfig, Config, \
    ToolSelectorProvider

router = APIRouter(
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.post("/api-signature-selector")
def run_plugin(
        messages: List[Message],
        tool_selector_config: ToolSelectorConfig,
        plugin: Plugin,
        config: Config,
        llm: LLM,
        api_key: APIKey = Depends(auth.get_api_key)
):
    if tool_selector_config.provider == ToolSelectorProvider.Imprompt:
        selector = ImpromptApiSignatureSelector(tool_selector_config, plugin, config, llm)
    elif tool_selector_config.provider == ToolSelectorProvider.Langchain:
        selector = LangchainApiSignatureSelector(tool_selector_config, plugin, config, llm)
    elif tool_selector_config.provider == ToolSelectorProvider.OpenAI:
        selector = OpenAIApiSignatureSelector(tool_selector_config, plugin, config, llm)
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
