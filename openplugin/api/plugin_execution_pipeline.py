import datetime
import os
import traceback
from typing import List, Optional

from fastapi import APIRouter, Body, Depends
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKey
from pydantic import BaseModel

from openplugin.api import auth
from openplugin.core.config import Config
from openplugin.core.function_providers import FunctionProviders
from openplugin.core.plugin import PluginBuilder
from openplugin.core.plugin_execution_pipeline import PluginExecutionPipeline
from openplugin.core.port import Port, PortType

# Create a FastAPI router instance
router = APIRouter(
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


class FunctionProviderInput(BaseModel):
    name: str


function_providers = FunctionProviders.build()


# Define a POST endpoint for plugin-pipeline API
@router.post("/plugin-execution-pipeline")
async def plugin_execution_pipeline(
    openplugin_manifest_url: Optional[str] = Body(None),
    openplugin_manifest_obj: Optional[dict] = Body(None),
    prompt: str = Body(...),
    header: dict = Body(...),
    function_provider_input: Optional[FunctionProviderInput] = Body(
        None, alias="function_provider"
    ),
    conversation: list = Body(...),
    auth_query_param: Optional[dict] = Body(default=None),
    config: Optional[Config] = Body(None),
    run_all_output_modules: bool = Body(False),
    output_module_names: Optional[List[str]] = None,
    api_key: APIKey = Depends(auth.get_api_key),
) -> JSONResponse:
    try:
        start = datetime.datetime.now()
        input = Port(data_type=PortType.TEXT, value=prompt)
        if openplugin_manifest_obj is not None:
            plugin_obj = PluginBuilder.build_from_manifest_obj(openplugin_manifest_obj)
        elif openplugin_manifest_url is not None:
            if openplugin_manifest_url.startswith("http"):
                plugin_obj = PluginBuilder.build_from_manifest_url(
                    openplugin_manifest_url
                )
            else:
                plugin_obj = PluginBuilder.build_from_manifest_file(
                    openplugin_manifest_url
                )
        else:
            return JSONResponse(
                status_code=400,
                content={
                    "message": "Either manifest URL or manifest object is required"
                },
            )

        if config is None:
            config = Config(openai_api_key=os.environ["OPENAI_API_KEY"])
        pipeline = PluginExecutionPipeline(plugin=plugin_obj)
        if function_provider_input is None:
            function_provider_input = function_providers.get_default_provider()
        response_obj = await pipeline.start(
            input=input,
            config=config,
            function_provider=function_providers.get_by_name(
                function_provider_input.name
            ),
            header=header,
            auth_query_param=auth_query_param,
            output_module_names=output_module_names,
            run_all_output_modules=run_all_output_modules,
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
            status_code=500, content={"message": f"Failed to run plugin. {e}"}
        )
