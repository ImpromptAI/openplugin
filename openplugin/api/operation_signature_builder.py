from typing import List

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKey

from openplugin.api import auth
from openplugin.bindings.imprompt.imprompt_operation_signature_builder import (
    ImpromptOperationSignatureBuilder,
)
from openplugin.bindings.langchain.langchain_operation_signature_selector import (
    LangchainOperationSignatureBuilder,
)
from openplugin.bindings.openai.openai_operation_signature_builder import (
    OpenAIOperationSignatureBuilder,
)
from openplugin.interfaces.models import (
    LLM,
    Config,
    Message,
    Plugin,
    ToolSelectorConfig,
    ToolSelectorProvider,
)

# Create a FastAPI router instance
router = APIRouter(
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


# Define a POST endpoint for /api-signature-selector
@router.post("/operation-signature-builder")
def operation_signature_builder(
    messages: List[Message],
    tool_selector_config: ToolSelectorConfig,
    plugin: Plugin,
    config: Config,
    llm: LLM,
    api_key: APIKey = Depends(auth.get_api_key),
):
    # Based on the provider specified in tool_selector_config, create the appropriate
    # API signature selector
    try:
        if tool_selector_config.provider == ToolSelectorProvider.Imprompt:
            imprompt_selector = ImpromptOperationSignatureBuilder(
                tool_selector_config, plugin, config, llm
            )
            return imprompt_selector.run(messages)
        elif tool_selector_config.provider == ToolSelectorProvider.Langchain:
            langchain_selector = LangchainOperationSignatureBuilder(
                tool_selector_config, plugin, config, llm
            )
            return langchain_selector.run(messages)
        elif tool_selector_config.provider == ToolSelectorProvider.OpenAI:
            openai_selector = OpenAIOperationSignatureBuilder(
                tool_selector_config, plugin, config, llm
            )
            return openai_selector.run(messages)
        else:
            # If an incorrect ToolSelectorProvider is specified, return a 400 Bad
            # Request response
            return JSONResponse(
                status_code=400,
                content={"message": "Incorrect ToolSelectorProvider"},
            )
    except Exception as e:
        print(e)
        # Return a 500 Internal Server Error response if there's a failure in
        # running the plugin
        return JSONResponse(
            status_code=500, content={"message": "Failed to run plugin"}
        )
