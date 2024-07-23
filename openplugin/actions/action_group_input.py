from typing import List

from pydantic import BaseModel, Field


class ActionOperation(BaseModel):
    operation_path: str
    operation_method: str


class ActionPlugin(BaseModel):
    manifest_url: str
    operations: List[ActionOperation]


class ActionGroupInput(BaseModel):
    name: str
    action_plugins: List[ActionPlugin] = Field(..., alias="plugins")
