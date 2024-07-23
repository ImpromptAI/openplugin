from typing import Any, Dict, List

from pydantic import BaseModel

from .action_group_input import ActionGroupInput


class ActionGroupResponse(BaseModel):
    message: str = ""


class ActionGroupResponseOutput(BaseModel):
    metadata: Dict[str, Any] = {}
    response: ActionGroupResponse
    run_completed: bool = False
    failed_message: str = ""
    traces: List = []


class ActionGroupExecutionPipeline(BaseModel):
    action_group_input: ActionGroupInput

    def start(self) -> ActionGroupResponseOutput:
        print("ActionGroupExecutionPipeline started")
        return ActionGroupResponseOutput(
            run_completed=True,
            response=ActionGroupResponse(
                message="ActionGroupExecutionPipeline started"
            ),
        )
