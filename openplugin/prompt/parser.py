from loguru import logger
from pydantic import BaseModel

from .prompt_page import PromptPage, PromptResponse


class PromptParser(BaseModel):
    prompt_page: PromptPage

    def parse(self, prompt: str, user_input_map: dict) -> PromptResponse:
        logger.info(f"\n[PROMPT_PAGE] {self.prompt_page}")
        logger.info(f"\n[USER_PROMPT] {prompt}")
        logger.info(f"\n[USER_INPUT_MAP] {user_input_map}")
        response = PromptResponse(prompt_page=self.prompt_page, response="")
        return response
