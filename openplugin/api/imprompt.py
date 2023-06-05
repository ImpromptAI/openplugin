from typing import List, Optional
from fastapi import APIRouter, Depends
from openplugin import ImpromptPluginSelector
from openplugin import Message, LLM, Plugin, ToolSelectorConfig, Config
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKey
from openplugin.api import auth

router = APIRouter(
    prefix="/imprompt",
    tags=["imprompt"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.post("/run-plugin")
def run_plugin(
        messages: List[Message],
        tool_selector_config: ToolSelectorConfig,
        plugins: List[Plugin],
        config: Optional[Config],
        llm: LLM,
        api_key: APIKey = Depends(auth.get_api_key)
):
    selector = ImpromptPluginSelector(tool_selector_config, plugins, config, llm)
    try:
        response = selector.run(messages)
        return response
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"message": "Failed to run plugin"})
