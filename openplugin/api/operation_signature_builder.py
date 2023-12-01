from typing import Annotated, List, Optional, Union

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKey
from pydantic import BaseModel

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


class OperationSignatureParam(BaseModel):
    messages: List[Message]
    plugin: Plugin
    config: Config
    llm: LLM
    selected_operation: Optional[str] = None
    pre_prompts: Optional[List[Message]] = None


# Define a POST endpoint for /api-signature-selector
@router.post("/operation-signature-builder")
def operation_signature_builder(
    input: OperationSignatureParam,
    pipeline_name: Annotated[
        Union[str, None], Query(description="pipeline_nam")
    ] = None,
    api_key: APIKey = Depends(auth.get_api_key),
):
    # Based on the provider specified in tool_selector_config, create the appropriate
    # API signature selector
    try:
        # TODO:Find a way to detect best pipeline for a prompt
        if pipeline_name is None:
            openai_selector = OpenAIOperationSignatureBuilder(
                input.plugin,
                input.config,
                input.llm,
                input.pre_prompts,
                input.selected_operation,
            )
            return openai_selector.run(input.messages)
        if (
            pipeline_name.lower()
            == "LLM Passthrough (OpenPlugin and Swagger)".lower()
            or pipeline_name.lower()
            == "LLM Passthrough (OpenPlugin + Swagger)".lower()
        ):
            imprompt_selector = ImpromptOperationSignatureBuilder(
                input.plugin,
                input.config,
                input.llm,
                input.pre_prompts,
                input.selected_operation,
                "openplugin-swagger",
            )
            return imprompt_selector.run(input.messages)
        elif pipeline_name.lower() == "LLM Passthrough (Stuffed Swagger)".lower():
            imprompt_selector = ImpromptOperationSignatureBuilder(
                input.plugin,
                input.config,
                input.llm,
                input.pre_prompts,
                input.selected_operation,
                "stuffed-swagger",
            )
            return imprompt_selector.run(input.messages)
        elif pipeline_name.lower() == "LLM Passthrough (Bare Swagger)".lower():
            imprompt_selector = ImpromptOperationSignatureBuilder(
                input.plugin,
                input.config,
                input.llm,
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
                input.plugin,
                input.config,
                input.llm,
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
        print(e)
        # Return a 500 Internal Server Error response if there's a failure in
        # running the plugin
        return JSONResponse(
            status_code=500, content={"message": "Failed to run plugin"}
        )
