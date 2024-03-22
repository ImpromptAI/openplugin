from typing import Optional
import os, time, json
from langchain_openai import ChatOpenAI
from pydantic import BaseConfig, BaseModel


class Config(BaseModel):
    """
    Represents the API configuration for a plugin.
    """

    provider: str = "openai"
    openai_api_key: Optional[str] = None
    cohere_api_key: Optional[str] = None
    google_palm_key: Optional[str] = None
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region_name: Optional[str] = None
    azure_api_key: Optional[str] = None

    def replace_missing_with_system_keys(self):
        if not self.openai_api_key and os.environ.get("OPENAI_API_KEY"):
            self.openai_api_key = os.environ["OPENAI_API_KEY"]


class FunctionResponse(BaseModel):
    response_content: str
    usage: dict
    cost: int
    llm_latency_seconds: float
    total_tokens: int
    is_function_call: bool = False
    detected_function_name: Optional[str] = None
    detected_function_arguments: Optional[dict] = None


class LLM(BaseModel):
    """
    Represents the configuration for an LLM (Language Model) provider.
    """

    provider: str
    model_name: str
    temperature: float = 0
    max_tokens: int = 2048
    top_p: float = 1
    frequency_penalty: float = 0
    presence_penalty: float = 0
    n: int = 1
    best_of: int = 1
    max_retries: int = 6

    class Config(BaseConfig):
        # Set protected_namespaces to an empty tuple to resolve the conflict
        protected_namespaces = ()

    def get_langchain_llm_model(self):
        if self.provider.lower() in ["openai", "openaichat"]:
            return ChatOpenAI(
                model=self.model_name,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
        elif self.provider.lower() == "mistral":
            from langchain_mistralai.chat_models import ChatMistralAI

            return ChatMistralAI(
                model=self.model_name,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                mistral_api_key=self.api_key,
            )
        elif self.provider.lower() == "fireworks":
            from langchain_fireworks import ChatFireworks

            return ChatFireworks(
                model=self.model_name,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                fireworks_api_key=self.api_key,
            )
        else:
            raise ValueError(f"LLM provider {self.provider} not supported")

    def run_functions(self, message: str, function_json: list) -> FunctionResponse:
        start_time = time.time()
        llm_model = self.get_langchain_llm_model()
        llm_with_tools = llm_model.bind_tools(function_json)
        response = llm_with_tools.invoke(message)
        llm_latency_seconds = time.time() - start_time
        # llm_api_cost = litellm.completion_cost(completion_response=response)
        # TODO
        llm_api_cost = 0
        total_tokens = response.response_metadata.get("token_usage", {}).get(
            "total_tokens"
        )

        tool_calls = response.additional_kwargs.get("tool_calls")
        is_function_call = False
        function_name = None
        arguments = None
        if (
            tool_calls
            and len(tool_calls) > 0
            and tool_calls[0].get("type") == "function"
        ):
            is_function_call = True
            message_json = tool_calls[0]
            function_name = message_json.get("function").get("name")
            arguments = json.loads(message_json["function"]["arguments"])

        return FunctionResponse(
            response_content=str(response.content),
            usage=response.response_metadata,
            cost=llm_api_cost,
            llm_latency_seconds=llm_latency_seconds,
            total_tokens=total_tokens,
            is_function_call=is_function_call,
            detected_function_name=function_name,
            detected_function_arguments=arguments,
        )
