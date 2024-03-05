from typing import Optional

from litellm import completion

from openplugin.core import Config, Port, PortType, PortValueError

from ..llm_engine import LLMEngine


class LLMEngineWithOpenAI(LLMEngine):
    # openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    model_name: str = "gpt-3.5-turbo"
    pre_prompt: Optional[str] = None

    async def process_input(
        self, input: Port, config: Optional[Config] = None
    ) -> Port:
        if input.value is None:
            raise PortValueError("Input value cannot be None")
        if self.pre_prompt:
            prompt = self.pre_prompt + str(input.value)
        else:
            prompt = str(input.value)
        messages = [{"content": prompt, "role": "user"}]
        response = completion(model="gpt-3.5-turbo", messages=messages)
        content = response["choices"][0]["message"]["content"]
        return Port(data_type=PortType.TEXT, value=content)
