import traceback
from typing import Annotated, List, Optional, Union

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKey
from pydantic import BaseModel, root_validator

from openplugin.api import auth
from openplugin.core.config import Config
from openplugin.core.function_providers import FunctionProvider, FunctionProviders
from openplugin.core.messages import Message
from openplugin.core.operations.implementations.operation_signature_builder_with_imprompt import (
    ImpromptOperationSignatureBuilder,
)
from openplugin.core.operations.implementations.operation_signature_builder_with_openai import (
    OpenAIOperationSignatureBuilder,
)
from openplugin.core.plugin import PluginBuilder

# Create a FastAPI router instance
router = APIRouter(
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


class OperationSignatureParam(BaseModel):
    messages: List[Message]
    # plugin: Plugin
    plugin_manifest_url: str
    config: Config
    function_provider: FunctionProvider
    selected_operation: Optional[str] = None
    pre_prompts: Optional[List[Message]] = None

    @root_validator(pre=True)
    def _set_fields(cls, values: dict) -> dict:
        """This is a validator that sets the field values based on the manifest_url"""
        values["plugin_manifest_url"] = values.get("plugin", {}).get("manifest_url")
        return values


# Define a POST endpoint for /api-signature-selector
@router.post("/operation-signature-builder")
def operation_signature_builder(
    input: OperationSignatureParam,
    pipeline_name: Annotated[
        Union[str, None], Query(description="pipeline_name")
    ] = None,
    api_key: APIKey = Depends(auth.get_api_key),
):
    # Based on the provider specified in tool_selector_config, create the appropriate
    # API signature selector
    plugin = PluginBuilder.build_from_manifest_url(input.plugin_manifest_url)
    try:
        function_provider = FunctionProviders.build().get_default_provider()

        if pipeline_name is None:
            openai_selector = OpenAIOperationSignatureBuilder(
                plugin,
                function_provider,
                input.config,
                input.pre_prompts,
                input.selected_operation,
            )
            return openai_selector.run(input.messages)
        if (
            pipeline_name.lower() == "LLM Passthrough (OpenPlugin and Swagger)".lower()
            or pipeline_name.lower() == "LLM Passthrough (OpenPlugin + Swagger)".lower()
        ):
            imprompt_selector = ImpromptOperationSignatureBuilder(
                plugin,
                function_provider,
                input.config,
                input.pre_prompts,
                input.selected_operation,
                "openplugin-swagger",
            )
            return imprompt_selector.run(input.messages)
        elif pipeline_name.lower() == "LLM Passthrough (Stuffed Swagger)".lower():
            imprompt_selector = ImpromptOperationSignatureBuilder(
                plugin,
                function_provider,
                input.config,
                input.pre_prompts,
                input.selected_operation,
                "stuffed-swagger",
            )
            return imprompt_selector.run(input.messages)
        elif pipeline_name.lower() == "LLM Passthrough (Bare Swagger)".lower():
            imprompt_selector = ImpromptOperationSignatureBuilder(
                plugin,
                function_provider,
                input.config,
                input.pre_prompts,
                input.selected_operation,
                "bare-swagger",
            )
            return imprompt_selector.run(input.messages)
        elif (
            pipeline_name.lower()
            == OpenAIOperationSignatureBuilder.get_pipeline_name().lower()
        ):
            openai_selector = OpenAIOperationSignatureBuilder(
                plugin,
                function_provider,
                input.config,
                input.pre_prompts,
                input.selected_operation,
            )
            return openai_selector.run(input.messages)
        else:
            # If an incorrect pipeline is specified, return a 400 Bad
            # Request response
            return JSONResponse(
                status_code=400,
                content={"message": "Incorrect pipeline"},
            )
    except Exception as e:
        traceback.print_exc()
        print(e)
        # Return a 500 Internal Server Error response if there's a failure in
        # running the plugin
        return JSONResponse(
            status_code=500, content={"message": "Failed to run plugin"}
        )
