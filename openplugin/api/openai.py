from typing import List
from fastapi import APIRouter, Depends
from openplugin import OpenAIPluginSelector
from openplugin import Message, LLM, Plugin, ToolSelectorConfig, Config
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKey
from openplugin.api import auth

router = APIRouter(
    prefix="/openai",
    tags=["openai"],
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
        api_key: APIKey = Depends(auth.get_api_key)
):
    selector = OpenAIPluginSelector(tool_selector_config, plugins, config, llm)
    try:
        response = selector.run(messages)
        return response
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500,
                            content={"message": "Failed to run plugin"})
