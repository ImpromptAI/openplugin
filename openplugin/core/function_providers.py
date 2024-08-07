import json
import os
import time
import traceback
from abc import abstractmethod
from typing import List, Optional

from dotenv import load_dotenv
from langchain_community.callbacks import get_openai_callback
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from pydantic import BaseModel, validator

from .config import Config

load_dotenv()


class FunctionResponse(BaseModel):
    response_content: str
    usage: dict
    response_metadata: dict
    cost: float
    llm_latency_seconds: float
    total_tokens: Optional[int]
    is_function_call: bool = False
    detected_function_name: Optional[str] = None
    detected_function_arguments: Optional[dict] = None
    system_prompt: Optional[str] = None


class LLMConfig(BaseModel):
    temperature: int = 0
    top_p: float = 0
    max_tokens: int = 4096


class FunctionLLM(BaseModel):
    provider: str
    model_name: str
    configuration: LLMConfig

    def get_callback_manager(self):
        if self.provider.lower() in ["openai", "openaichat"]:
            return get_openai_callback()
        return None

    def convert_to_langchain_llm_model(self, config: Optional[Config]):
        if self.provider.lower() in ["openai", "openaichat"]:
            from langchain_openai import ChatOpenAI

            if os.environ.get("OPENAI_API_KEY") is not None:
                openai_api_key = os.environ["OPENAI_API_KEY"]
            elif config is not None and config.openai_api_key is not None:
                openai_api_key = config.openai_api_key
            else:
                raise Exception("OpenAI API Key not found")
            return ChatOpenAI(
                model=self.model_name,
                temperature=self.configuration.temperature,
                api_key=openai_api_key,
            )
        elif self.provider.lower() == "mistral":
            from langchain_mistralai.chat_models import ChatMistralAI

            if os.environ.get("MISTRAL_API_KEY") is not None:
                mistral_api_key = os.environ["MISTRAL_API_KEY"]
            elif config is not None and config.mistral_api_key is not None:
                mistral_api_key = config.mistral_api_key
            else:
                raise Exception("MISTRAL_API_KEY API Key not found")
            return ChatMistralAI(
                model=self.model_name,
                temperature=self.configuration.temperature,
                max_tokens=self.configuration.max_tokens,
                mistral_api_key=mistral_api_key,
            )
        elif self.provider.lower() == "fireworks":
            from langchain_fireworks import ChatFireworks

            if os.environ.get("FIREWORKS_API_KEY") is not None:
                fireworks_api_key = os.environ["FIREWORKS_API_KEY"]
            elif config is not None and config.fireworks_api_key is not None:
                fireworks_api_key = config.fireworks_api_key
            else:
                raise Exception("Fireworks API Key not found")
            return ChatFireworks(
                model=self.model_name,
                temperature=self.configuration.temperature,
                max_tokens=self.configuration.max_tokens,
                api_key=fireworks_api_key,
            )
        elif self.provider.lower() == "anthropic":
            from langchain_anthropic import ChatAnthropic

            if os.environ.get("ANTHROPIC_API_KEY") is not None:
                anthropic_api_key = os.environ["ANTHROPIC_API_KEY"]
            elif config is not None and config.anthropic_api_key is not None:
                anthropic_api_key = config.anthropic_api_key
            else:
                raise Exception("Anthropic API Key not found")
            return ChatAnthropic(
                model=self.model_name,
                temperature=self.configuration.temperature,
                max_tokens=self.configuration.max_tokens,
                api_key=anthropic_api_key,
            )
        elif self.provider.lower() == "google":
            from langchain_google_vertexai import ChatVertexAI

            return ChatVertexAI(model=self.model_name)
        elif self.provider.lower() == "cohere":
            from langchain_cohere import ChatCohere

            if os.environ.get("COHERE_API_KEY") is not None:
                cohere_api_key = os.environ["COHERE_API_KEY"]
            elif config is not None and config.cohere_api_key is not None:
                cohere_api_key = config.cohere_api_key
            else:
                raise Exception("Cohere API Key not found")
            return ChatCohere(model="command-r", cohere_api_key=cohere_api_key)
        elif self.provider.lower() == "groq":
            from langchain_groq import ChatGroq

            if os.environ.get("GROQ_API_KEY") is not None:
                groq_api_key = os.environ["GROQ_API_KEY"]
            elif config is not None and config.groq_api_key is not None:
                groq_api_key = config.groq_api_key
            else:
                raise Exception("Groq API Key not found")
            return ChatGroq(
                temperature=0, groq_api_key=groq_api_key, model_name=self.model_name
            )
        elif self.provider.lower() == "togetherai":
            from langchain_openai import ChatOpenAI

            if os.environ.get("TOGETHER_API_KEY") is not None:
                together_api_key = os.environ["TOGETHER_API_KEY"]
            elif config is not None and config.together_api_key is not None:
                together_api_key = config.together_api_key
            else:
                raise Exception("Together API Key not found")

            return ChatOpenAI(
                base_url="https://api.together.xyz/v1",
                api_key=together_api_key,
                model=self.model_name,
            )
        else:
            raise ValueError(f"LLM provider {self.provider} not supported")


class FunctionProvider(BaseModel):
    provider: str
    model: str
    name: str
    required_auth_keys: set
    type: str
    is_supported: bool = False
    is_default: bool = False

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
    def run(
        self,
        request_prompt: str,
        function_json,
        config: Optional[Config],
        conversation: Optional[List] = [],
        x_few_shot_examples: Optional[List] = [],
    ) -> FunctionResponse:
        pass


class LLMBasedFunctionProvider(FunctionProvider):
    llm: FunctionLLM
    system_prompt: str = (
        """You are an expert tool user. Never hallucinate or make up information on parameters. Extract values from the given context. Always provide accurate and relevant information."""
    )

    def run(
        self,
        request_prompt: str,
        function_json,
        config: Optional[Config],
        conversation: Optional[List] = [],
        x_few_shot_examples: Optional[List] = [],
    ) -> FunctionResponse:
        try:
            start_time = time.time()
            llm_model = self.llm.convert_to_langchain_llm_model(config)

            examples_and_conversation = (
                self.build_few_shot_examples_and_conversation(
                    x_few_shot_examples, conversation=conversation
                )
            )
            few_shot_prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", self.system_prompt),
                    *examples_and_conversation,
                    ("human", "{query}"),
                ]
            )
            call_back_manager = self.llm.get_callback_manager()
            if call_back_manager:
                with call_back_manager as cb:
                    llm_with_tools = llm_model.bind_tools(function_json)
                    chain = (
                        {"query": RunnablePassthrough()}
                        | few_shot_prompt
                        | llm_with_tools
                    )
                    response = chain.invoke(request_prompt)
                    llm_api_cost = cb.total_cost
            else:
                llm_with_tools = llm_model.bind_tools(function_json)
                chain = (
                    {"query": RunnablePassthrough()}
                    | few_shot_prompt
                    | llm_with_tools
                )
                response = chain.invoke(request_prompt)
                llm_api_cost = 0

            llm_latency_seconds = time.time() - start_time
            total_tokens = response.response_metadata.get("token_usage", {}).get(
                "total_tokens"
            )
            tool_calls = response.additional_kwargs.get("tool_calls")
            if not tool_calls:
                tool_calls = response.tool_calls

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
            response_metadata = {
                "response": response.additional_kwargs,
                "metadata": response.response_metadata,
            }
            return FunctionResponse(
                response_content=str(response.content),
                usage=response.response_metadata,
                cost=llm_api_cost,
                llm_latency_seconds=llm_latency_seconds,
                total_tokens=total_tokens,
                is_function_call=is_function_call,
                detected_function_name=function_name,
                detected_function_arguments=arguments,
                response_metadata=response_metadata,
                system_prompt=self.system_prompt,
            )
        except Exception as e:
            traceback.print_exc()
            print(e)
            raise e

    def build_few_shot_examples_and_conversation(
        self, x_few_shot_examples: Optional[List], conversation: Optional[List]
    ) -> List:
        messages: List = []
        if x_few_shot_examples:
            for example in x_few_shot_examples:
                messages.append(
                    HumanMessage(
                        content=example.get("prompt"),
                        name="example_user",
                    )
                )
                messages.append(
                    AIMessage(
                        content="",
                        tool_calls=[
                            {
                                "name": example.get("name"),
                                "args": example.get("parameter_mapping"),
                                "id": example.get("tool_call_id"),
                            }
                        ],
                        name="example_assistant",
                    )
                )
                if example.get("response"):
                    messages.append(
                        ToolMessage(
                            content=example.get("response"),
                            tool_call_id=example.get("tool_call_id"),
                        )
                    )

        if conversation:
            for conv in conversation:
                if conv.get("role") == "user":
                    messages.append(AIMessage(content=conv.get("content")))
                else:
                    messages.append(HumanMessage(content=conv.get("content")))
        return messages

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
        return self.providers[0]
