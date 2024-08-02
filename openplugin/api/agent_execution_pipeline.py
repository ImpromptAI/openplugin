import traceback

from fastapi import APIRouter, Body, Depends
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKey

from openplugin.agent.agent_execution_pipeline import (
    AgentExecutionPipeline,
    AgentExecutionResponseOutput,
)
from openplugin.agent.agent_input import AgentInput
from openplugin.api import auth

# Create a FastAPI router instance
router = APIRouter(
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


# Define a POST endpoint for plugin-pipeline API
@router.post("/agent-builder")
def agent_builder(
    agent_input: AgentInput = Body(...),
    api_key: APIKey = Depends(auth.get_api_key),
) -> JSONResponse:
    pipeline = AgentExecutionPipeline(agent_input=agent_input)
    try:
        response: AgentExecutionResponseOutput = pipeline.build_agent_script()
        return JSONResponse(
            status_code=200, content=response.dict(exclude_none=True)
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})


@router.post("/agent-execution")
def agent_execution(
    agent_input: AgentInput = Body(...),
    api_key: APIKey = Depends(auth.get_api_key),
) -> JSONResponse:
    pipeline = AgentExecutionPipeline(agent_input=agent_input)
    try:
        response: AgentExecutionResponseOutput = pipeline.run()
        return JSONResponse(
            status_code=200, content=response.dict(exclude_none=True)
        )
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"message": str(e)})
