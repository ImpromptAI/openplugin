import json
import time
from math import e
from typing import List, Optional

from litellm import completion, completion_cost

from ...config import Config
from ...function_providers import FunctionProvider, FunctionResponse
from ...functions import Functions
from ...messages import Message, MessageType
from ...plugin import Plugin
from ...plugin_detected import PluginDetectedParams, SelectedApiSignatureResponse
from ..operation_signature_builder import (
    OperationSignatureBuilder,
)
from .operation_signature_builder_with_langchain import (
    LangchainOperationSignatureBuilder,
)


# Custom API Signature Selector for OpenAI
class CustomOperationSignatureBuilder(OperationSignatureBuilder):
    def __init__(
        self,
        plugin: Plugin,
        function_provider: FunctionProvider,
        config: Optional[Config],
        pre_prompts: Optional[List[Message]] = None,
        selected_operation: Optional[str] = None,
    ):
        if pre_prompts is None:
            pre_prompts = []

        pre_prompts.append(
            Message(
                message_type=MessageType.SystemMessage,
                content="Maintain the plurality of mapped parameters and the test sentence throughout the generated text.",  # noqa: E501
            )
        )
        self.function_provider = function_provider
        super().__init__(
            plugin, function_provider, config, pre_prompts, selected_operation
        )
        if config and config.openai_api_key:
            self.openai_api_key = config.openai_api_key
        else:
            raise ValueError("OpenAI API Key is not configured")

    def run(self, messages: List[Message]) -> SelectedApiSignatureResponse:
        start_test_case_time = time.time()
        functions = Functions()
        functions.add_from_plugin(self.plugin, self.selected_operation)
        # request_prompt = functions.get_x_helpers()
        request_prompt = ""
        for message in messages:
            if message.message_type == MessageType.HumanMessage:
                request_prompt += f"\n#PROMPT={message.content}"
        if len(functions.functions) == 0:
            return SelectedApiSignatureResponse(
                run_completed=True,
                modified_input_prompt=request_prompt,
                final_text_response="No functions found",
                detected_plugin_operations=[],
                response_time=round(time.time() - start_test_case_time, 2),
                tokens_used=0,
                llm_api_cost=0,
                llm_calls=[],
            )
        f_messages = [
            msg.get_openai_message()
            for msg in messages
            if msg.get_openai_message() is not None
        ]
        if self.function_provider.get_provider_name().lower() in [
            "cohere",
            "google",
        ]:
            llm_api_key = None
            if self.config is not None:
                if self.function_provider.get_provider_name().lower() == "cohere":
                    if not self.config.cohere_api_key:
                        raise ValueError("Cohere API Key is not configured")
                    else:
                        llm_api_key = self.config.cohere_api_key
                if self.function_provider.get_provider_name().lower() == "google":
                    if not self.config.gemini_api_key:
                        raise ValueError("Google API Key is not configured")
                    else:
                        llm_api_key = self.config.gemini_api_key
            else:
                raise ValueError("API Key is not configured")

            detected_plugin_operations: list[PluginDetectedParams] = []
            function_json = functions.get_litellm_json()
            model = self.function_provider.get_model_name()
            start_completion_time = time.time()
            response = completion(
                model=model,
                messages=f_messages,
                tools=function_json,
                api_key=llm_api_key,
                tool_choice="auto",  # auto is default, but we'll be explicit
            )
            # print("\nFirst LLM Response:\n", response)

            response_message = response.choices[0].message
            response_content = response_message.content
            tool_calls = response_message.tool_calls
            cost = completion_cost(completion_response=response)
            llm_calls: list = []
            llm_calls.append(
                {
                    "used_for": "signature_builder",
                    "response": response_content,
                    "model": self.function_provider.get_model_name(),
                    "cost": cost,
                    "usage": response.usage.total_tokens,
                    "messages": f_messages,
                    "request_prompt": request_prompt,
                    "llm_latency_seconds": time.time() - start_completion_time,
                    "response_prompt": response_content,
                    "temperature": self.function_provider.get_temperature(),
                    "max_tokens": self.function_provider.get_max_tokens(),
                    "top_p": self.function_provider.get_top_p(),
                    "status_code": "200",
                }
            )
            if tool_calls and len(tool_calls) > 0:
                function_name = tool_calls[0].function.name
                detected_plugin = functions.get_plugin_from_func_name(function_name)
                detected_function = functions.get_function_from_func_name(
                    function_name
                )
                mapped_parameters = json.loads(tool_calls[0].function.arguments)
                p_detected = PluginDetectedParams(
                    plugin=detected_plugin,
                    api_called=detected_function.get_api_url(),
                    method=detected_function.get_api_method(),
                    mapped_operation_parameters=mapped_parameters,
                )
                detected_plugin_operations.append(p_detected)
                final_text_response = ""
            else:
                final_text_response = response_content

            func_response = response.dict()
            response_obj = SelectedApiSignatureResponse(
                run_completed=True,
                modified_input_prompt=request_prompt,
                final_text_response=final_text_response,
                detected_plugin_operations=detected_plugin_operations,
                response_time=time.time() - start_test_case_time,
                tokens_used=response.usage.total_tokens,
                llm_api_cost=cost,
                llm_calls=llm_calls,
                function_request_json=function_json,
                function_response_json=func_response,
            )
            return response_obj
        else:
            oai_selector = LangchainOperationSignatureBuilder(
                plugin=self.plugin,
                function_provider=self.function_provider,
                config=self.config,
            )
            response = oai_selector.run(messages)
            return response

    @classmethod
    def get_pipeline_name(cls) -> str:
        return "oai functions"
