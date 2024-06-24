import time
from typing import List, Optional, final

from ...config import Config
from ...execution.implementations.operation_execution_with_imprompt import (
    OperationExecutionParams,
    OperationExecutionWithImprompt,
)
from ...function_providers import FunctionProvider, FunctionResponse
from ...functions import Function, Functions
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
        header: Optional[dict] = None,
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
            plugin,
            function_provider,
            config,
            pre_prompts,
            selected_operation,
            header,
        )
        if config and config.openai_api_key:
            self.openai_api_key = config.openai_api_key
        else:
            raise ValueError("OpenAI API Key is not configured")

    def run(
        self, messages: List[Message], conversation: Optional[List] = []
    ) -> SelectedApiSignatureResponse:
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
                request_prompt, function_json, self.config, conversation=conversation
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
        x_dep_tracing = None
        if func_response.is_function_call:
            function_name = func_response.detected_function_name
            detected_plugin = functions.get_plugin_from_func_name(function_name)
            detected_function = functions.get_function_from_func_name(function_name)
            mapped_parameters = func_response.detected_function_arguments
            x_dependent_params, x_dep_tracing = self.get_x_dependent_parameters(
                request_prompt, detected_function, function_json, mapped_parameters
            )
            if x_dependent_params and len(x_dependent_params) > 0:
                mapped_parameters = x_dependent_params

            p_detected = PluginDetectedParams(
                plugin=detected_plugin,
                api_called=detected_function.get_api_url(),
                method=detected_function.get_api_method(),
                mapped_operation_parameters=mapped_parameters,
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
            x_dep_tracing=x_dep_tracing,
        )
        return response_obj

    def get_x_dependent_parameters(
        self,
        request_prompt: str,
        detected_function: Function,
        original_function_json: dict,
        mapped_parameters: Optional[dict],
    ):
        # extract x-dependent properties: Support only level 1
        x_params_map = {}
        tracing = []
        if detected_function and detected_function.param_properties:
            for prop in detected_function.param_properties:
                # for every x-depednent property
                if prop.x_dependent:
                    try:

                        functions = Functions()
                        path = f"{prop.x_dependent.get('method')}<PATH>{prop.x_dependent.get('path')}"
                        functions.add_from_plugin(self.plugin, path)
                        function_json = functions.get_json()
                        prompt = f"Resolve this parameter:{prop.name}, I have already extracted these parameters: {mapped_parameters}, {request_prompt}".strip()
                        # run function calling with function json and
                        func_response: FunctionResponse = self.function_provider.run(
                            prompt,
                            function_json,
                            self.config,
                            conversation=[],
                        )
                        api_response = None
                        if func_response.is_function_call:
                            detected_function = (
                                functions.get_function_from_func_name(
                                    func_response.detected_function_name
                                )
                            )
                            # call the API
                            params = OperationExecutionParams(
                                config=self.config,
                                api=detected_function.get_api_url(),
                                method=detected_function.get_api_method(),
                                query_params=func_response.detected_function_arguments,
                                body=None,
                                header=self.header,
                                function_provider=self.function_provider,
                            )
                            ex = OperationExecutionWithImprompt(params)
                            response = ex.run()
                            # update the mapped_parameters with the response
                            if response and response.original_response:
                                api_response = response.original_response
                                x_params_map[prop.name] = response.original_response
                        tracing.append(
                            {
                                "property_name": prop.name,
                                "x_dependent_values": prop.x_dependent,
                                "prompt": prompt,
                                "api_response": api_response,
                            }
                        )
                    except Exception as e:
                        print(f"Failed to resolve the x parameter: {e}")

        if x_params_map and len(x_params_map) > 0:
            prompt = (
                f"Use these values: {x_params_map}, Rerun {request_prompt}".strip()
            )
            # run function calling with function json and
            f_response: FunctionResponse = self.function_provider.run(
                prompt,
                original_function_json,
                self.config,
                conversation=[],
            )
            if f_response and f_response.is_function_call:
                return f_response.detected_function_arguments, tracing
        return None, tracing

    @classmethod
    def get_pipeline_name(cls) -> str:
        return "oai functions"
