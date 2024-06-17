from fastapi import APIRouter, Body, Depends
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKey

from openplugin.api import auth
from openplugin.core.functions import Functions
from openplugin.core.plugin import PluginBuilder

# Create a FastAPI router instance
router = APIRouter(
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.post("/plugin-validator")
def plugin_execution_pipeline(
    openplugin_manifest_obj: dict = Body(None),
    api_key: APIKey = Depends(auth.get_api_key),
) -> JSONResponse:
    try:
        plugin = PluginBuilder.build_from_manifest_obj(openplugin_manifest_obj)
        return JSONResponse(
            status_code=200,
            content={"message": "Plugin is valid.", "plugin_name": plugin.name},
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.get("/openapi-parser")
def openapi_parser(
    openplugin_manifest_obj: dict = Body(None),
    api_key: APIKey = Depends(auth.get_api_key),
) -> JSONResponse:
    try:
        plugin = PluginBuilder.build_from_manifest_obj(openplugin_manifest_obj)
        return JSONResponse(
            status_code=200,
            content={"message": "Plugin is valid.", "plugin_name": plugin.name},
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.get("/openapi-param-parser")
def openapi_param_parser(openapi_doc_url: str) -> JSONResponse:
    try:
        functions = Functions()
        functions.add_from_openapi_spec(open_api_spec_url=openapi_doc_url)
        function_json = functions.get_expanded_json()
        return JSONResponse(
            status_code=200,
            content={
                "message": "OpenAPI doc parsed successfully.",
                "functions": function_json,
            },
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
