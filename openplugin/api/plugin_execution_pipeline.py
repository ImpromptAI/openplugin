import datetime
import os
import traceback
from typing import List, Optional

from fastapi import APIRouter, Body, Depends
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKey

from openplugin.api import auth
from openplugin.plugins.models import Config
from openplugin.plugins.plugin import PluginBuilder, PreferredApproach
from openplugin.plugins.plugin_execution_pipeline import PluginExecutionPipeline
from openplugin.plugins.port import Port, PortType

# Create a FastAPI router instance
router = APIRouter(
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


# Define a POST endpoint for plugin-pipeline API
@router.post("/plugin-execution-pipeline")
async def plugin_execution_pipeline(
    preferred_approach: PreferredApproach = Body(..., alias="approach"),
    conversation: list = Body(...),
    openplugin_manifest_url: str = Body(...),
    prompt: str = Body(...),
    config: Optional[Config] = Body(None),
    output_module_ids: Optional[List[str]] = None,
    api_key: APIKey = Depends(auth.get_api_key),
) -> JSONResponse:
    try:
        start = datetime.datetime.now()
        input = Port(data_type=PortType.TEXT, value=prompt)
        if openplugin_manifest_url.startswith("http"):
            plugin_obj = PluginBuilder.build_from_manifest_url(openplugin_manifest_url)
        else:
            plugin_obj = PluginBuilder.build_from_manifest_file(openplugin_manifest_url)

        if config is None:
            config = Config(openai_api_key=os.environ["OPENAI_API_KEY"])
        pipeline = PluginExecutionPipeline(plugin=plugin_obj)
        response_obj = await pipeline.start(
            input=input,
            config=config,
            preferred_approach=preferred_approach,
            output_module_ids=output_module_ids,
        )
        json_data = response_obj.model_dump(
            exclude={"output_ports__type_object", "output_ports__value"}
        )
        end = datetime.datetime.now()
        elapsed_time = end - start
        response = {
            "metadata": {
                "start_time": start.strftime("%Y-%m-%d %H:%M:%S.%f"),
                "end_time": end.strftime("%Y-%m-%d %H:%M:%S.%f"),
                "total_time_taken_seconds": elapsed_time.total_seconds(),
                "total_time_taken_ms": elapsed_time.microseconds,
            },
            "response": json_data,
        }
        return JSONResponse(status_code=200, content=response)
    except Exception as e:
        print(e)
        traceback.print_exc()
        return JSONResponse(
            status_code=500, content={"message": "Failed to run plugin"}
        )
