import traceback

import requests
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security.api_key import APIKey
from pydantic import BaseModel

from openplugin.api import auth
from openplugin.core.functions import Functions
from openplugin.core.plugin import PluginBuilder

# Create a FastAPI router instance
router = APIRouter(
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


class PluginValidationResponse(BaseModel):
    message: str
    plugin_name: str


@router.post(
    "/plugin-validator",
    tags=["plugin-validator"],
    description="Enpoint to validate a plugin manifest",
    response_model=PluginValidationResponse,
)
def plugin_validator(
    openapi_doc_url: dict = Body(None),
    api_key: APIKey = Depends(auth.get_api_key),
):
    plugin = PluginBuilder.build_from_openapi_doc_obj(openapi_doc_url)
    return PluginValidationResponse(message="Plugin is valid.", plugin_name=plugin.name)


class FunctionResponse(BaseModel):
    message: str
    functions: dict


@router.get(
    "/openapi-param-parser",
    tags=["openapi-param-parse"],
    description="Enpoint to parse OpenAPI doc and extract functions",
    response_model=FunctionResponse,
)
def openapi_param_parser(openapi_doc_url: str):
    try:
        functions = Functions()
        openapi_doc_obj = requests.get(openapi_doc_url).json()
        functions.add_from_openapi_spec(openapi_doc_obj=openapi_doc_obj)
        function_json = functions.get_expanded_json()
        return FunctionResponse(
            message="OpenAPI doc parsed successfully.", functions=function_json
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
