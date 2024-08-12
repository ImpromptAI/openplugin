import base64
import secrets
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import WebSocket
from pydantic import BaseModel

from .agent_actions import InpResponse
from .agent_execution import AgentExecution, AgentExecutionResponse
from .agent_input import AgentManifest, AgentPrompt, AgentRuntime, MessageType


class AgentExecutionMetadata(BaseModel):
    start_time: str
    end_time: str
    total_time_taken_seconds: float
    total_time_taken_ms: int


class AgentExecutionResponseOutput(BaseModel):
    run_completed: bool = False
    metadata: Optional[AgentExecutionMetadata] = None
    final_response: Optional[str] = None
    tools_called: List[Dict] = []
    code_snippet: Optional[str] = None
    failed_message: Optional[str] = None
    traces: List = []


def generate_id(prefix: str, num_bytes=24):
    random_bytes = secrets.token_bytes(num_bytes)
    random_string = (
        base64.urlsafe_b64encode(random_bytes).rstrip(b"=").decode("utf-8")
    )
    return f"{prefix}_{random_string}"


class AgentExecutionPipeline(BaseModel):
    agent_manifest: AgentManifest
    agent_runtime: AgentRuntime
    websocket: Optional[WebSocket]
    session_prompts: Dict[str, List[AgentPrompt]] = {}
    session_conversations: Dict[str, List[AgentPrompt]] = {}
    current_session_id: Optional[str] = None
    agent_id: str = generate_id("agent")

    agent_execution: Optional[AgentExecution] = None

    def get_tools_json(self):
        if self.agent_execution and self.agent_execution.tool_map:
            tools = []
            for tool in self.agent_execution.tool_map.values():
                tools.append(tool)
            return tools
        return None

    async def setup_agent(self):
        print("=-=-=-=-=-=-=--=-= SETUP AGENT =-=-=-=-=-=-=-=-=-=-=")
        print(self.agent_manifest)
        print(self.agent_runtime)
        print(self.session_prompts)
        print("==========================================================")
        session_id = generate_id("session")
        self.current_session_id = session_id
        self.session_prompts[session_id] = []
        self.session_conversations[session_id] = []
        if self.agent_runtime.implementation.provider == "langchain":
            if self.agent_runtime.implementation.type == "openai_tools_agent":
                if True:
                    from .agent_execution_implementations.agent_execution_with_operation_langchain import (
                        AgentExecutionWithOperationLangchain,
                    )

                    self.agent_execution = AgentExecutionWithOperationLangchain(
                        agent_manifest=self.agent_manifest,
                        agent_runtime=self.agent_runtime,
                        websocket=self.websocket,
                    )
                else:
                    from .agent_execution_implementations.agent_execution_with_plugin_langchain import (
                        AgentExecutionWithPluginLangchain,
                    )

                    self.agent_execution = AgentExecutionWithPluginLangchain(
                        agent_manifest=self.agent_manifest,
                        agent_runtime=self.agent_runtime,
                        websocket=self.websocket,
                    )

        if not self.agent_execution:
            print("====")
            raise NotImplementedError("Agent implementation not supported.")

    async def close_websocket(self):
        if self.websocket:
            await self.websocket.close()

    async def send_json_message(
        self,
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
        if self.websocket:
            await self.websocket.send_json(obj)

    async def batch_run(self, agent_prompt: AgentPrompt, do_new_session=False):
        print("AgentExecutionPipeline started")
        if self.agent_execution is None:
            raise NotImplementedError("Agent builder not set")
        if do_new_session:
            session_id = generate_id("session")
            self.current_session_id = session_id
            self.session_prompts[session_id] = []
            self.session_conversations[session_id] = []
        associated_job_id = generate_id("job")
        agent_prompt.associated_job_id = associated_job_id
        await self.send_json_message(
            InpResponse.AGENT_JOB_STARTED,
            {"job_id": agent_prompt.associated_job_id},
        )
        self.add_to_current_session(agent_prompt)
        if self.agent_runtime.implementation.provider == "langchain":
            if self.agent_runtime.implementation.type == "openai_tools_agent":
                start = datetime.now()
                response_obj: AgentExecutionResponse = (
                    await self.agent_execution.run_agent_batch(
                        self.get_current_session_prompts(),
                        self.get_current_session_conversations(),
                    )
                )
                self.add_to_current_conversation_session(
                    AgentPrompt(
                        prompt=response_obj.final_response,
                        associated_job_id=associated_job_id,
                        message_type=MessageType.AGENT,
                    )
                )
                tools_called = response_obj.tools_called
                end = datetime.now()
                elapsed_time = end - start
                metadata = AgentExecutionMetadata(
                    start_time=start.strftime("%Y-%m-%d %H:%M:%S.%f"),
                    end_time=end.strftime("%Y-%m-%d %H:%M:%S.%f"),
                    total_time_taken_seconds=elapsed_time.total_seconds(),
                    total_time_taken_ms=elapsed_time.microseconds,
                )
                agent_execution_response = AgentExecutionResponseOutput(
                    run_completed=True,
                    metadata=metadata,
                    final_response=response_obj.final_response,
                    tools_called=tools_called,
                )
                result = agent_execution_response.dict(exclude_none=True)
                result["job_id"] = agent_prompt.associated_job_id
                await self.send_json_message(
                    InpResponse.AGENT_JOB_COMPLETED,
                    result,
                    step_name="result",
                )
                return agent_execution_response
        raise NotImplementedError("Agent implementation not supported")

    def add_to_current_session(self, agent_prompt: AgentPrompt):
        if self.current_session_id is None:
            raise ValueError("Current session id not set")
        self.session_prompts[self.current_session_id].append(agent_prompt)
        self.session_conversations[self.current_session_id].append(agent_prompt)

    def add_to_current_conversation_session(self, agent_prompt: AgentPrompt):
        if self.current_session_id is None:
            raise ValueError("Current session id not set")
        self.session_conversations[self.current_session_id].append(agent_prompt)

    async def interactive_run(self, agent_prompt: AgentPrompt):
        print()

    def interactive_run_next(self):
        print()

    def stop(self):
        self.agent_execution.stop()

    def get_current_session_prompts(self):
        return self.session_prompts[self.current_session_id]

    def get_current_session_conversations(self):
        return self.session_conversations[self.current_session_id]

    async def clear_current_session(self):
        self.session_prompts[self.current_session_id] = []
        self.session_conversations[self.current_session_id] = []

    async def clear_all_session(self):
        self.session_prompts = {}
        self.session_conversations = {}

    class Config:
        arbitrary_types_allowed = True
