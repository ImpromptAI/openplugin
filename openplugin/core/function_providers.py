import json
import os
import time
from abc import abstractmethod
from typing import List, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, validator

load_dotenv()


class FunctionResponse(BaseModel):
    response_content: str
    usage: dict
    cost: int
    llm_latency_seconds: float
    total_tokens: Optional[int]
    is_function_call: bool = False
    detected_function_name: Optional[str] = None
    detected_function_arguments: Optional[dict] = None


class LLMConfig(BaseModel):
    temperature: int = 0
    top_p: float = 0
    max_tokens: int = 4096


class FunctionLLM(BaseModel):
    provider: str
    model_name: str
    configuration: LLMConfig

    def convert_to_langchain_llm_model(self):
        if self.provider.lower() in ["openai", "openaichat"]:
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                model=self.model_name,
                temperature=self.configuration.temperature,
            )
        elif self.provider.lower() == "mistral":
            from langchain_mistralai.chat_models import ChatMistralAI

            return ChatMistralAI(
                model=self.model_name,
                temperature=self.configuration.temperature,
                max_tokens=self.configuration.max_tokens,
                mistral_api_key=os.environ["MISTRAL_API_KEY"],
            )
        elif self.provider.lower() == "fireworks":
            from langchain_fireworks import ChatFireworks

            return ChatFireworks(
                model=self.model_name,
                temperature=self.configuration.temperature,
                max_tokens=self.configuration.max_tokens,
                fireworks_api_key=os.environ["FIREWORKS"],
            )
        elif self.provider.lower() == "anthropic":
            from langchain_anthropic import ChatAnthropic

            return ChatAnthropic(
                model=self.model_name,
                temperature=self.configuration.temperature,
                max_tokens=self.configuration.max_tokens,
                anthropic_api_key=os.environ["ANTHROPIC_API_KEY"],
            )
        elif self.provider.lower() == "google":
            from langchain_google_vertexai import ChatVertexAI

            return ChatVertexAI(model=self.model_name)
        elif self.provider.lower() == "cohere":
            from langchain_cohere import ChatCohere

            os.environ["COHERE_API_KEY"] = os.environ.get("COHERE_API_KEY")
            return ChatCohere(model="command-r")
        elif self.provider.lower() == "groq":
            from langchain_groq import ChatGroq

            chat = ChatGroq(
                temperature=0,
                groq_api_key=os.environ.get("GROQ_API_KEY"),
                model_name="mixtral-8x7b-32768",
            )
            return chat
        else:
            raise ValueError(f"LLM provider {self.provider} not supported")


class FunctionProvider(BaseModel):
    name: str
    required_auth_keys: set
    type: str
    is_supported: bool = False

    @validator("is_supported", pre=True, always=True)
    def set_is_supported(cls, v, values):
        required_auth_keys = values.get("required_auth_keys")
        for key in required_auth_keys:
            if key not in os.environ:
                return False
        return True

    @abstractmethod
    def get_temperature(self) -> int:
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        pass

    @abstractmethod
    def get_top_p(self) -> float:
        pass

    @abstractmethod
    def get_max_tokens(self) -> int:
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        pass

    @abstractmethod
    def run(self, request_prompt: str, function_json) -> FunctionResponse:
        pass


class LLMBasedFunctionProvider(FunctionProvider):
    llm: FunctionLLM

    def run(self, request_prompt: str, function_json) -> FunctionResponse:
        start_time = time.time()
        llm_model = self.llm.convert_to_langchain_llm_model()
        llm_with_tools = llm_model.bind_tools(function_json)
        print("==-=-=-=-=-= FUNCTION JSON =-=-=-=-=-=-=")
        print(function_json)

        response = llm_with_tools.invoke(request_prompt)
        print("==-=-=-=-=-= FUNCTION RESPONSE =-=-=-=-=-=-=")
        print(response)

        llm_latency_seconds = time.time() - start_time
        # llm_api_cost = litellm.completion_cost(completion_response=response)
        # TODO
        llm_api_cost = 0
        total_tokens = response.response_metadata.get("token_usage", {}).get(
            "total_tokens"
        )

        tool_calls = response.additional_kwargs.get("tool_calls")
        if not tool_calls:
            tool_calls = response.tool_calls
        print("==-=-=-=-=-= TOOL CALLS =-=-=-=-=-=-=")
        print(tool_calls)

        is_function_call = False
        function_name = None
        arguments = None
        if tool_calls and len(tool_calls) > 0:
            if tool_calls[0].get("type") == "function":
                is_function_call = True
                message_json = tool_calls[0]
                function_name = message_json.get("function").get("name")
                arguments = json.loads(message_json["function"]["arguments"])
            else:
                is_function_call = True
                message_json = tool_calls[0]
                function_name = message_json.get("name")
                arguments = message_json["args"]

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

    def get_temperature(self) -> int:
        return self.llm.configuration.temperature

    def get_top_p(self) -> float:
        return self.llm.configuration.top_p

    def get_provider_name(self) -> str:
        return self.llm.provider

    def get_max_tokens(self) -> int:
        return self.llm.configuration.max_tokens

    def get_model_name(self) -> str:
        return self.llm.model_name


class FunctionProviders(BaseModel):
    providers: List[FunctionProvider]

    @staticmethod
    def build(file_location: Optional[str] = None):
        if file_location is None:
            file_location = (
                f"{os.getcwd()}/openplugin/resources/function_providers.json"
            )
        with open(file_location, "r") as file:
            function_providers = json.load(file)
            fps = []
            for fp in function_providers:
                if fp.get("type") == "llm-based":
                    provider = LLMBasedFunctionProvider(**fp)
                    fps.append(provider)
            return FunctionProviders(providers=fps)

    def get_by_name(self, name: str) -> FunctionProvider:
        for provider in self.providers:
            if name.lower() == provider.name.lower():
                return provider
        raise ValueError("Incorrect provider name")

    def get_default_provider(self):
        return self.llm_based_function_providers[0]
