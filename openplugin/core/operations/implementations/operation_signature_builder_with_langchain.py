import time
from typing import List, Optional

from ...config import Config
from ...function_providers import FunctionProvider, FunctionResponse
from ...functions import Functions
from ...messages import Message, MessageType
from ...plugin import Plugin
from ...plugin_detected import PluginDetectedParams, SelectedApiSignatureResponse
from ..operation_signature_builder import (
    OperationSignatureBuilder,
)


# Custom API Signature Selector for OpenAI
class LangchainOperationSignatureBuilder(OperationSignatureBuilder):
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
        llm_calls: list = []
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
                llm_calls=llm_calls,
            )

        f_messages = [
            msg.get_openai_message()
            for msg in messages
            if msg.get_openai_message() is not None
        ]
        function_json = functions.get_json()
        final_text_response = None
        detected_plugin_operations: list[PluginDetectedParams] = []
        func_response_metadata_json = None
        try:
            func_response: FunctionResponse = self.function_provider.run(
                request_prompt, function_json, self.config
            )
            func_response_metadata_json = func_response.response_metadata
            llm_calls.append(
                {
                    "used_for": "signature_builder",
                    "response": func_response.response_content,
                    "model": self.function_provider.get_model_name(),
                    "cost": func_response.cost,
                    "usage": func_response.usage,
                    "messages": f_messages,
                    "request_prompt": request_prompt,
                    "llm_latency_seconds": func_response.llm_latency_seconds,
                    "response_prompt": func_response.response_content,
                    "temperature": self.function_provider.get_temperature(),
                    "max_tokens": self.function_provider.get_max_tokens(),
                    "top_p": self.function_provider.get_top_p(),
                    "status_code": "200",
                }
            )
        except Exception as e:
            print(e)
            return SelectedApiSignatureResponse(
                run_completed=False,
                modified_input_prompt=request_prompt,
                final_text_response="Reason: " + str(e),
                detected_plugin_operations=[],
                response_time=round(time.time() - start_test_case_time, 2),
                tokens_used=0,
                llm_api_cost=0,
                llm_calls=llm_calls,
                function_request_json=function_json,
            )

        if func_response.is_function_call:
            function_name = func_response.detected_function_name
            detected_plugin = functions.get_plugin_from_func_name(function_name)
            detected_function = functions.get_function_from_func_name(function_name)
            p_detected = PluginDetectedParams(
                plugin=detected_plugin,
                api_called=detected_function.get_api_url(),
                method=detected_function.get_api_method(),
                mapped_operation_parameters=func_response.detected_function_arguments,
            )
            detected_plugin_operations.append(p_detected)
        else:
            final_text_response = func_response.response_content

        response_obj = SelectedApiSignatureResponse(
            run_completed=True,
            modified_input_prompt=request_prompt,
            final_text_response=final_text_response,
            detected_plugin_operations=detected_plugin_operations,
            response_time=time.time() - start_test_case_time,
            tokens_used=func_response.total_tokens,
            llm_api_cost=func_response.cost,
            llm_calls=llm_calls,
            function_request_json=function_json,
            function_response_json=func_response_metadata_json,
        )
        return response_obj

    @classmethod
    def get_pipeline_name(cls) -> str:
        return "oai functions"
