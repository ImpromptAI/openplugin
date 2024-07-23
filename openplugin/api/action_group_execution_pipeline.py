from fastapi import APIRouter, Body, Depends
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKey

from openplugin.actions.action_group_execution_pipeline import (
    ActionGroupExecutionPipeline,
    ActionGroupResponseOutput,
)
from openplugin.actions.action_group_input import ActionGroupInput
from openplugin.api import auth

# Create a FastAPI router instance
router = APIRouter(
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


# Define a POST endpoint for plugin-pipeline API
@router.post("/action-group-execution-pipeline")
def action_group_execution_pipeline(
    action_group_input: ActionGroupInput = Body(...),
    api_key: APIKey = Depends(auth.get_api_key),
) -> JSONResponse:
    pipeline = ActionGroupExecutionPipeline(action_group_input=action_group_input)
    response: ActionGroupResponseOutput = pipeline.start()
    return JSONResponse(status_code=200, content=response.dict())
