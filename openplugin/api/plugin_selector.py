import traceback
from typing import List

from fastapi import APIRouter, Body, Depends
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKey

from openplugin.api import auth
from openplugin.core.config import Config
from openplugin.core.function_providers import FunctionProviders
from openplugin.core.messages import Message
from openplugin.core.plugin import Plugin, PluginBuilder
from openplugin.core.selectors.implementations.plugin_selector_with_openai import (
    OpenAIPluginSelector,
)

# Create a FastAPI router instance
router = APIRouter(
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


# Define a POST endpoint for plugin-selector API
@router.post("/plugin-selector")
def plugin_selector(
    messages: List[Message] = Body(...),
    openapi_doc_urls: List[str] = Body(...),
    config: Config = Body(...),
    pipeline_name: str = Body(...),
    api_key: APIKey = Depends(auth.get_api_key),
):
    try:
        # Based on the provider specified in tool_selector_config, create the
        # appropriate plugin selector
        plugins: List[Plugin] = []
        for openapi_doc_url in openapi_doc_urls:
            plugin_obj = PluginBuilder.build_from_openapi_doc_url(openapi_doc_url)
            plugins.append(plugin_obj)
        function_provider = FunctionProviders.build().get_default_provider()
        if pipeline_name.lower() == OpenAIPluginSelector.get_pipeline_name().lower():
            openai_selector = OpenAIPluginSelector(plugins, config, function_provider)
            return openai_selector.run(messages)
        else:
            # If an incorrect ToolSelectorProvider is specified, return a 400
            # Bad Request response
            return JSONResponse(
                status_code=400,
                content={"message": "Incorrect ToolSelectorProvider"},
            )
    except Exception as e:
        print(e)
        traceback.print_exc()
        # Return a 500 Internal Server Error response if there's a failure in
        # running the plugin
        return JSONResponse(
            status_code=500, content={"message": "Failed to run plugin"}
        )
