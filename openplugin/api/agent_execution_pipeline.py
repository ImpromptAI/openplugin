import traceback
from typing import Dict, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, WebSocket
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKey

from openplugin.agent.agent_actions import InpAction, InpResponse
from openplugin.agent.agent_execution_pipeline import (
    AgentExecutionPipeline,
    AgentExecutionResponseOutput,
)
from openplugin.agent.agent_input import AgentManifest, AgentPrompt, AgentRuntime
from openplugin.api import auth

# Create a FastAPI router instance
router = APIRouter(
    dependencies=[],
    responses={404: {"description": "Not found"}},
    prefix="/agent",
)


def build_agent_script(agent_manifest: AgentManifest, agent_runtime: AgentRuntime):
    if agent_runtime.implementation.provider == "langchain":
        if agent_runtime.implementation.type == "openai_tools_agent":
            code_snippet = agent_manifest.get_langchain_openai_tools_agent()
            return AgentExecutionResponseOutput(
                run_completed=True,
                code_snippet=code_snippet,
            )
    raise NotImplementedError("Agent implementation not supported")


# Define a POST endpoint for plugin-pipeline API
@router.post("/agent-builder")
def agent_builder(
    agent_manifest: AgentManifest = Body(...),
    agent_runtime: AgentRuntime = Body(...),
    api_key: APIKey = Depends(auth.get_api_key),
) -> JSONResponse:
    try:
        response: AgentExecutionResponseOutput = build_agent_script(
            agent_manifest=agent_manifest, agent_runtime=agent_runtime
        )
        return JSONResponse(
            status_code=200, content=response.dict(exclude_none=True)
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})


"""
@router.post("/interactive/run")
def interactive_run(
    agent_input: AgentInput = Body(...),
    api_key: APIKey = Depends(auth.get_api_key),
) -> JSONResponse:
    pipeline = AgentExecutionPipeline(agent_input=agent_input)
    try:
        response: AgentExecutionResponseOutput = pipeline.interactive_run()
        return JSONResponse(
            status_code=200, content=response.dict(exclude_none=True)
        )
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"message": str(e)})


@router.post("/interactive/run/next")
def interactive_run_next(
    agent_input: AgentInput = Body(...),
    api_key: APIKey = Depends(auth.get_api_key),
) -> JSONResponse:
    pipeline = AgentExecutionPipeline(agent_input=agent_input)
    try:
        response: AgentExecutionResponseOutput = pipeline.interactive_run_next()
        return JSONResponse(
            status_code=200, content=response.dict(exclude_none=True)
        )
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"message": str(e)})


@router.post("/stop")
def agent_stop(
    agent_input: AgentInput = Body(...),
    api_key: APIKey = Depends(auth.get_api_key),
) -> JSONResponse:
    pipeline = AgentExecutionPipeline(agent_input=agent_input)
    try:
        response: AgentExecutionResponseOutput = pipeline.stop()
        return JSONResponse(
            status_code=200, content=response.dict(exclude_none=True)
        )
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"message": str(e)})
"""


@router.websocket("/interactive/run")
async def interactive_run_ws(websocket: WebSocket):
    await websocket.accept()
    pipeline = None
    while True:
        data = await websocket.receive_json()
        action = data.get("action")
        if action == "agent_setup":
            agent_manifest_json = data.get("agent_manifest")
            agent_manifest: AgentManifest = AgentManifest(**agent_manifest_json)

            agent_runtime_json = data.get("agent_runtime")
            agent_runtime: AgentRuntime = AgentRuntime(**agent_runtime_json)

            pipeline = AgentExecutionPipeline(
                agent_manifest=agent_manifest,
                agent_runtime=agent_runtime,
                websocket=websocket,
            )
            await pipeline.setup_agent()
        elif action == "agent_prompt":
            agent_prompt_json = data.get("agent_prompt")
            agent_prompt = AgentPrompt(**agent_prompt_json)
            if pipeline:
                await pipeline.interactive_run(agent_prompt)
            else:
                await websocket.send_json(
                    {"message": "Agent setup required", "failed": True}
                )
                await websocket.close()


@router.websocket("/batch/run")
async def batch_run_ws(websocket: WebSocket):
    async def send_json_message(
        response: InpResponse,
        value: Optional[Dict] = None,
        step_name: Optional[str] = None,
    ):
        """Helper function to send JSON message via websocket."""
        obj = {"message_type": response.value, "description": response.description}  # type: ignore
        if step_name:
            obj["step_name"] = step_name
        if value:
            obj["value"] = value
        await websocket.send_json(obj)

    await websocket.accept()
    x_api_key = websocket.headers.get("x-api-key", "")
    try:
        await auth.get_api_key(x_api_key)
    except HTTPException as e:
        await send_json_message(
            InpResponse.INVALID_API_KEY, value={"message": str(e)}
        )
        await websocket.close()
        return

    pipeline = None

    while True:
        data = await websocket.receive_json()
        action_str = data.get("action")
        if not action_str:
            await send_json_message(InpResponse.MISSING_ACTION)
            continue
        try:
            action = InpAction(data.get("action"))
        except ValueError:
            await send_json_message(InpResponse.INCORRECT_ACTION)
            continue

        if action == InpAction.AGENT_SETUP:
            if pipeline:
                await send_json_message(InpResponse.AGENT_ALREADY_SETUP)
                continue
            agent_manifest_json = data.get("agent_manifest")
            agent_manifest: AgentManifest = AgentManifest(**agent_manifest_json)

            agent_runtime_json = data.get("agent_runtime")
            agent_runtime: AgentRuntime = AgentRuntime(**agent_runtime_json)
            try:
                pipeline = AgentExecutionPipeline(
                    agent_manifest=agent_manifest,
                    agent_runtime=agent_runtime,
                    websocket=websocket,
                )
                await pipeline.setup_agent()
                await send_json_message(
                    InpResponse.AGENT_JOB_STEP,
                    value={
                        "agent_id": pipeline.agent_id,
                        "session_id:": pipeline.current_session_id,
                        "tools": pipeline.get_tools_json(),
                        "message": "Agent setup completed",
                    },
                    step_name="setup",
                )
                if agent_runtime_json.get("prompt"):
                    agent_prompt = AgentPrompt(
                        prompt=agent_runtime_json.get("prompt")
                    )
                    await pipeline.batch_run(agent_prompt)
            except Exception as e:
                traceback.print_exc()
                print(e)
                pipeline = None
                await send_json_message(
                    InpResponse.AGENT_JOB_FAILED, value={"message": str(e)}
                )
            continue
        else:
            if pipeline is None:
                await send_json_message(InpResponse.AGENT_NOT_SETUP)
                continue
            if action == InpAction.AGENT_PROMPT:
                try:
                    agent_prompt = data.get("prompt", "")
                    agent_prompt = AgentPrompt(prompt=agent_prompt)
                    await pipeline.batch_run(agent_prompt)
                except Exception as e:
                    await send_json_message(
                        InpResponse.AGENT_JOB_FAILED, value={"message": str(e)}
                    )
                continue
            elif action == InpAction.AGENT_STOP:
                await pipeline.stop()
                await send_json_message(InpResponse.AGENT_STOPPED)
                continue
            elif action == InpAction.AGENT_CURRENT_SESSION_CLEAR:
                await pipeline.clear_current_session()
                await send_json_message(InpResponse.AGENT_SESSION_CLEARED)
                continue
            elif action == InpAction.AGENT_CURRENT_SESSION_PROMPTS:
                prompts = pipeline.get_current_session_prompts()
                await send_json_message(
                    InpResponse.AGENT_SESSION_PROMPTS, value={"prompts": prompts}
                )
                continue
            else:
                await send_json_message(InpResponse.INCORRECT_ACTION)
                continue
