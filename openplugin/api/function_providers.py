from typing import Dict, Optional

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from openplugin.core import FunctionProviders
from openplugin.core.functions import Functions
from openplugin.core.plugin import PluginBuilder

router = APIRouter(
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

function_providers = FunctionProviders.build()


@router.get("/function-providers")
def get_function_providers(type: str = "all"):
    if type == "all":
        return function_providers.providers
    elif type == "llm-based":
        return function_providers.providers
    else:
        return JSONResponse(
            status_code=400, content={"message": "incorrect type parameter"}
        )


@router.get("/function-provider-request")
def get_function_provider_request(
    function_provider_name: str, openplugin_manifest_url: str
):
    try:
        function_providers.get_by_name(function_provider_name)
        functions = Functions()
        plugin = PluginBuilder.build_from_manifest_url(openplugin_manifest_url)
        functions.add_from_plugin(plugin)
        function_json = functions.get_json()
        return JSONResponse(status_code=200, content={"fc_request_json": function_json})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Failed: {e}"})


class RunFunctionInput(BaseModel):
    prompt: str
    function_provider_name: str
    openplugin_manifest_url: str
    function_json: Optional[Dict] = None


@router.post("/run-function-provider")
def run_function_provider(run_function_input: RunFunctionInput):
    try:
        function_provider = function_providers.get_by_name(
            run_function_input.function_provider_name
        )
        if run_function_input.function_json is None:
            functions = Functions()
            plugin = PluginBuilder.build_from_manifest_url(
                run_function_input.openplugin_manifest_url
            )
            functions.add_from_plugin(plugin)
            function_json = functions.get_json()
        func_response = function_provider.run(run_function_input.prompt, function_json)
        response=func_response.dict()
        response["detected_operation"]=""
        response["detected_method"]="get"
        return JSONResponse(
            status_code=200, content={"fc_resonse":response}
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Failed: {e}"})
