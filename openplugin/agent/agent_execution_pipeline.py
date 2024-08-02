from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from .agent_input import AgentInput
from .langchain_agent_execution_with_plugin import run_agent, setup_agent


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


class AgentExecutionPipeline(BaseModel):
    agent_input: AgentInput

    def run(self):
        print("AgentExecutionPipeline started")
        if self.agent_input.agent_implementation.provider == "langchain":
            if self.agent_input.agent_implementation.type == "openai_tools_agent":
                start = datetime.now()

                agent_executor = setup_agent(self.agent_input)
                response = run_agent(agent_executor, self.agent_input.prompt)
                tools_called = response.get("tools_called", [])

                end = datetime.now()
                elapsed_time = end - start
                metadata = AgentExecutionMetadata(
                    start_time=start.strftime("%Y-%m-%d %H:%M:%S.%f"),
                    end_time=end.strftime("%Y-%m-%d %H:%M:%S.%f"),
                    total_time_taken_seconds=elapsed_time.total_seconds(),
                    total_time_taken_ms=elapsed_time.microseconds,
                )

                return AgentExecutionResponseOutput(
                    run_completed=True,
                    metadata=metadata,
                    final_response=response.get("final_response"),
                    tools_called=tools_called,
                )
        raise NotImplementedError("Agent implementation not supported")

    def build_agent_script(self):
        print("AgentExecutionPipeline started")
        if self.agent_input.agent_implementation.provider == "langchain":
            if self.agent_input.agent_implementation.type == "openai_tools_agent":
                code_snippet = self.agent_input.get_langchain_openai_tools_agent()
                return AgentExecutionResponseOutput(
                    run_completed=True,
                    code_snippet=code_snippet,
                )
        raise NotImplementedError("Agent implementation not supported")
