import os
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException
from httpx import request
from pydantic import BaseModel

from openplugin.core import FunctionProvider, FunctionProviders
from openplugin.core.config import Config
from openplugin.core.functions import Functions
from openplugin.core.plugin import PluginBuilder

router = APIRouter(
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

function_providers = FunctionProviders.build()


def is_llm_supported(required_auth_keys, user_key_map):
    for key in required_auth_keys:
        if key not in user_key_map:
            return False
    return True


@router.get(
    "/function-providers",
    tags=["function-providers"],
    description="Enpoint to retrieve list of available function providers",
    response_model=List[FunctionProvider],
)
def get_function_providers(
    type: str = "all",
    openai_api_key: Optional[str] = None,
    anthropic_api_key: Optional[str] = None,
    gemini_api_key: Optional[str] = None,
    cohere_api_key: Optional[str] = None,
    fireworks_api_key: Optional[str] = None,
    mistral_api_key: Optional[str] = None,
    together_api_key: Optional[str] = None,
    groq_api_key: Optional[str] = None,
    openplugin_manifest_url: Optional[str] = None,
):
    user_key_map = {}
    if openai_api_key and openai_api_key.lower() == "true":
        user_key_map["OPENAI_API_KEY"] = True
    if anthropic_api_key and anthropic_api_key.lower() == "true":
        user_key_map["ANTHROPIC_API_KEY"] = True
    if gemini_api_key and gemini_api_key.lower() == "true":
        user_key_map["GEMINI_API_KEY"] = True
    if cohere_api_key and cohere_api_key.lower() == "true":
        user_key_map["COHERE_API_KEY"] = True
    if fireworks_api_key and fireworks_api_key.lower() == "true":
        user_key_map["FIREWORKS_API_KEY"] = True
    if mistral_api_key and mistral_api_key.lower() == "true":
        user_key_map["MISTRAL_API_KEY"] = True
    if together_api_key and together_api_key.lower() == "true":
        user_key_map["TOGETHER_API_KEY"] = True
    if groq_api_key and groq_api_key.lower() == "true":
        user_key_map["GROQ_API_KEY"] = True

    default_fp = os.environ.get("DEFAULT_FUNCTION_PROVIDER", "OpenAI [gpt-4]")
    if openplugin_manifest_url is not None:
        openplugin_manifest_json = request("GET", openplugin_manifest_url).json()
        if openplugin_manifest_json.get("default_function_provider") is not None:
            default_fp = openplugin_manifest_json.get("default_function_provider")

    if type == "all" or type == "llm-based":
        providers = function_providers.providers
        for provider in providers:
            if not provider.is_supported and is_llm_supported(
                provider.required_auth_keys, user_key_map
            ):
                provider.is_supported = True
            if provider.name == default_fp:
                provider.is_default = True
        return providers
    else:
        raise HTTPException(status_code=404, detail="Function provider not found.")


class FunctionProviderResponse(BaseModel):
    fc_request_json: List[Dict]


@router.get(
    "/function-provider-request",
    tags=["function-provider-request"],
    description="Enpoint to retrieve function provider request JSON",
    response_model=FunctionProviderResponse,
)
def get_function_provider_request(
    function_provider_name: str, openplugin_manifest_url: str
):
    try:
        function_providers.get_by_name(function_provider_name)
        functions = Functions()
        plugin = PluginBuilder.build_from_manifest_url(openplugin_manifest_url)
        functions.add_from_plugin(plugin)
        function_json = functions.get_json()
        return FunctionProviderResponse(fc_request_json=function_json)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed: {e}")


class RunFunctionInput(BaseModel):
    prompt: str
    function_provider_name: str
    openplugin_manifest_url: str
    config: Config
    function_json: Optional[Dict] = None


class FunctionProviderRunResponse(BaseModel):
    fc_response_json: dict


@router.post(
    "/run-function-provider",
    tags=["run-function-provider"],
    description="Enpoint to run a function provider",
    response_model=FunctionProviderRunResponse,
)
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
        func_response = function_provider.run(
            run_function_input.prompt, function_json, run_function_input.config
        )
        response = func_response.dict()
        response["detected_operation"] = ""
        response["detected_method"] = "get"
        return FunctionProviderRunResponse(fc_response_json=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed: {e}")
