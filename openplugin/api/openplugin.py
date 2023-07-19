from typing import List
from fastapi import APIRouter, Depends
from openplugin import OpenAIPluginSelector
from openplugin import Message, LLM, Plugin, ToolSelectorConfig, Config
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKey
from openplugin.api import auth
from openplugin import PluginOperation, Plugin
from openplugin.utils.manifest_handler import \
    get_openplugin_manifest_from_openai_manifest

router = APIRouter(
    prefix="/openplugin",
    tags=["openplugin"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.post("/openai-to-openplugin-manifest")
def openai_to_openplugin(
        openai_manifest_url: str,
        selected_operations: List[PluginOperation],
        api_key: APIKey = Depends(auth.get_api_key)
):
    try:
        response = get_openplugin_manifest_from_openai_manifest(
            openai_manifest_url=openai_manifest_url,
            selected_operations=selected_operations
        )
        return response
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500,
                            content={"message": "Failed to run plugin"})
