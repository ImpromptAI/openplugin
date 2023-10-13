from typing import Annotated, List, Optional, Union

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKey

from openplugin.api import auth
from openplugin.bindings.imprompt.imprompt_operation_signature_builder import (
    ImpromptOperationSignatureBuilder,
)
from openplugin.bindings.openai.openai_operation_signature_builder import (
    OpenAIOperationSignatureBuilder,
)
from openplugin.interfaces.models import LLM, Config, Message, Plugin

# Create a FastAPI router instance
router = APIRouter(
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


# Define a POST endpoint for /api-signature-selector
@router.post("/operation-signature-builder")
def operation_signature_builder(
    messages: List[Message],
    plugin: Plugin,
    config: Config,
    llm: LLM,
    pipeline_name: Annotated[
        Union[str, None], Query(description="pipeline_nam")
    ] = None,
    pre_prompts: Optional[List[Message]] = None,
    selected_operation: Optional[str] = None,
    api_key: APIKey = Depends(auth.get_api_key),
):
    # Based on the provider specified in tool_selector_config, create the appropriate
    # API signature selector
    try:
        # TODO:Find a way to detect best pipeline for a prompt
        if pipeline_name is None:
            openai_selector = OpenAIOperationSignatureBuilder(
                plugin, config, llm, pre_prompts, selected_operation
            )
            return openai_selector.run(messages)
        if (
            pipeline_name.lower()
            == ImpromptOperationSignatureBuilder.get_pipeline_name().lower()
        ):
            imprompt_selector = ImpromptOperationSignatureBuilder(
                plugin, config, llm, pre_prompts, selected_operation
            )
            return imprompt_selector.run(messages)
        elif (
            pipeline_name.lower()
            == OpenAIOperationSignatureBuilder.get_pipeline_name().lower()
        ):
            openai_selector = OpenAIOperationSignatureBuilder(
                plugin, config, llm, pre_prompts, selected_operation
            )
            return openai_selector.run(messages)
        else:
            # If an incorrect pipeline is specified, return a 400 Bad
            # Request response
            return JSONResponse(
                status_code=400,
                content={"message": "Incorrect pipeline"},
            )
    except Exception as e:
        print(e)
        # Return a 500 Internal Server Error response if there's a failure in
        # running the plugin
        return JSONResponse(
            status_code=500, content={"message": "Failed to run plugin"}
        )
