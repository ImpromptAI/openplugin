from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from fastapi import WebSocket
from pydantic import BaseModel

from .agent_actions import InpResponse
from .agent_input import AgentManifest, AgentPrompt, AgentRuntime


class AgentExecutionResponse(BaseModel):
    final_response: str
    tools_called: List[Dict] = []


class AgentInteractiveExecutionResponse(BaseModel):
    tool_called: Dict = {}


class AgentExecution(ABC):
    def __init__(
        self,
        agent_manifest: AgentManifest,
        agent_runtime: AgentRuntime,
        tool_map: Dict[str, Dict],
    ):
        self.agent_manifest = agent_manifest
        self.agent_runtime = agent_runtime
        self.tool_map = tool_map

    @abstractmethod
    async def run_agent_batch(
        self, agent_prompts: List[AgentPrompt]
    ) -> AgentExecutionResponse:
        pass

    @abstractmethod
    def interactive_run(
        self, agent_prompt: AgentPrompt
    ) -> AgentInteractiveExecutionResponse:
        pass

    @abstractmethod
    def stop(self):
        pass

    @classmethod
    async def send_json_message(
        self,
        response: InpResponse,
        websocket: Optional[WebSocket] = None,
        value: Optional[Dict] = None,
        step_name: Optional[str] = None,
    ):
        """Helper function to send JSON message via websocket."""
        obj = {"response": response.value, "description": response.description}  # type: ignore
        if step_name:
            obj["step_name"] = step_name
        if value:
            obj["value"] = value
        if websocket:
            await websocket.send_json(obj)
