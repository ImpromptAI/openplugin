import json
from typing import List, Optional

from pydantic import BaseModel, HttpUrl


class UserInput(BaseModel):
    name: str
    description: str
    type: str
    is_required: bool


class Output(BaseModel):
    type: str
    url: Optional[HttpUrl] = None


class PromptBlock(BaseModel):
    url: HttpUrl


class Plugin(BaseModel):
    name: str
    description: str
    endpoint: HttpUrl


class ActionGroup(BaseModel):
    name: str
    plugins: List[Plugin]


class PromptPage(BaseModel):
    name: str
    system_prompt: str
    capabilities: List[str]
    user_inputs: List[UserInput]
    outputs: List[Output]
    prompt_blocks: List[PromptBlock]
    action_group: List[ActionGroup]
    examples: List[str]


class PromptResponse(BaseModel):
    prompt_page: PromptPage
    response: str


def create_prompt_page_from_json(file_path: str) -> PromptPage:
    with open(file_path, "r") as file:
        data = json.load(file)
    prompt_page = PromptPage(**data)
    return prompt_page
