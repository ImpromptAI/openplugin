import traceback
from typing import Optional

from fastapi import APIRouter, Body, Depends
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKey

from openplugin.api import auth
from openplugin.plugins.models import Config, PreferredApproach
from openplugin.plugins.plugin_runner import run_prompt_on_plugin

# Create a FastAPI router instance
router = APIRouter(
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


# Define a POST endpoint for plugin-pipeline API
@router.post("/plugin-pipeline")
def plugin_pipeline(
    openplugin_manifest: str = Body(...),
    prompt: str = Body(...),
    config: Optional[Config] = Body(None),
    preferred_approach: Optional[PreferredApproach] = Body(None),
    api_key: APIKey = Depends(auth.get_api_key),
):
    try:
        ports = run_prompt_on_plugin(
            openplugin_manifest=openplugin_manifest,
            prompt=prompt,
            config=config,
            preferred_approach=preferred_approach,
        )
        return ports
    except Exception as e:
        print(e)
        traceback.print_exc()
        return JSONResponse(
            status_code=500, content={"message": "Failed to run plugin"}
        )
