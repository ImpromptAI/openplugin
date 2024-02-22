import traceback
from typing import List, Optional

from fastapi import APIRouter, Body, Depends
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKey

from openplugin.api import auth
from openplugin.plugins.models import Config, PreferredApproach
from openplugin.plugins.plugin_runner import run_prompt_on_plugin
from openplugin.plugins.port import PORT_TYPE_MAPPING, PortType

# Create a FastAPI router instance
router = APIRouter(
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


# Define a POST endpoint for plugin-pipeline API
@router.post("/plugin-pipeline")
async def plugin_pipeline(
    openplugin_manifest: str = Body(...),
    prompt: str = Body(...),
    config: Optional[Config] = Body(None),
    output_port_types: Optional[List[str]] = None,
    preferred_approach: Optional[PreferredApproach] = Body(None),
    api_key: APIKey = Depends(auth.get_api_key),
) -> JSONResponse:
    try:
        selected_output_ports: Optional[List[PortType]] = (
            [PORT_TYPE_MAPPING[port_type.lower()] for port_type in output_port_types]
            if output_port_types
            else None
        )
        ports = await run_prompt_on_plugin(
            openplugin_manifest=openplugin_manifest,
            prompt=prompt,
            config=config,
            output_port_types=selected_output_ports,
            preferred_approach=preferred_approach,
        )
        outputs = [port.to_dict() for port in ports]
        return JSONResponse(status_code=200, content=outputs)
    except Exception as e:
        print(e)
        traceback.print_exc()
        return JSONResponse(
            status_code=500, content={"message": "Failed to run plugin"}
        )
