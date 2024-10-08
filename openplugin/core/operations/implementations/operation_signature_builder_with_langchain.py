import time
from typing import List, Optional

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
        selected_operations: Optional[List[str]] = None,
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
            selected_operations,
            header,
        )
        if config and config.openai_api_key:
            self.openai_api_key = config.openai_api_key
        else:
            raise ValueError("OpenAI API Key is not configured")

    def run(
        self, messages: List[Message], conversation: Optional[List] = []
    ) -> SelectedApiSignatureResponse:
        system_prompt = None
        x_few_shot_examples: List = []

        start_test_case_time = time.time()
        functions = Functions()
        functions.add_from_plugin(self.plugin, self.selected_operations)
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
                system_prompt=system_prompt,
                conversations=conversation,
                examples=x_few_shot_examples,
            )

        f_messages = [
            msg.get_openai_message()
            for msg in messages
            if msg.get_openai_message() is not None
        ]

        function_json = functions.get_json()

        tool_id = 1
        for function in functions.functions:
            if function.x_few_shot_examples:
                for x in function.x_few_shot_examples:
                    vals = {k: v for k, v in x.items()}
                    vals["tool_call_id"] = tool_id
                    vals["name"] = function.name
                    x_few_shot_examples.append(vals)
            tool_id += 1

        final_text_response = None
        detected_plugin_operations: list[PluginDetectedParams] = []
        func_response_metadata_json = None
        try:
            # add x-helpers as conversation
            if conversation:
                for func in functions.functions:
                    x_helper_prompt = ""
                    if func.x_helpers and len(func.x_helpers) > 0:
                        x_helper_prompt += f"For API Path={func.path} and method={func.method}, \n#HELPERS={func.x_helpers}"
                    if func.param_properties:
                        for prop in func.param_properties:
                            if prop.x_helpers and len(prop.x_helpers) > 0:
                                x_helper_prompt += f"\nFor property: {prop.name}, #HELPERS={prop.x_helpers}"
                    if x_helper_prompt and len(x_helper_prompt) > 0:
                        conversation.append(
                            {"role": "system", "content": x_helper_prompt.strip()}
                        )

            func_response: FunctionResponse = self.function_provider.run(
                request_prompt,
                function_json,
                self.config,
                conversation=conversation,
                x_few_shot_examples=x_few_shot_examples,
            )
            func_response_metadata_json = func_response.response_metadata
            system_prompt = func_response.system_prompt
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
                system_prompt=system_prompt,
                conversations=conversation,
                examples=x_few_shot_examples,
            )

        x_dep_tracing = None
        response_obj_200 = None
        if func_response.is_function_call:
            function_name = func_response.detected_function_name
            detected_plugin = functions.get_plugin_from_func_name(function_name)
            detected_function = functions.get_function_from_func_name(function_name)
            response_obj_200 = detected_function.response_obj_200
            mapped_parameters = func_response.detected_function_arguments
            x_dependent_params, x_dep_tracing = self.get_x_dependent_parameters(
                request_prompt, detected_function, function_json, mapped_parameters
            )
            if x_dependent_params and len(x_dependent_params) > 0:
                mapped_parameters = x_dependent_params
            p_detected = PluginDetectedParams(
                plugin=detected_plugin,
                api_called=detected_function.get_api_url(),
                path=detected_function.get_path(),
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
            response_obj_200=response_obj_200,
            system_prompt=system_prompt,
            conversations=conversation,
            examples=x_few_shot_examples,
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
        try:
            if detected_function and detected_function.param_properties:
                for prop in detected_function.param_properties:
                    # for every x-depednent property
                    if prop.x_dependent:
                        try:
                            start_time1 = time.time()
                            functions = Functions()
                            path = f"{prop.x_dependent.get('method')}<PATH>{prop.x_dependent.get('path')}"
                            functions.add_from_plugin(self.plugin, [path])
                            function_json = functions.get_json()
                            prompt = f"Resolve this parameter:{prop.name}, I have already extracted these parameters: {mapped_parameters}, {request_prompt}".strip()
                            # run function calling with function json and
                            func_response: FunctionResponse = (
                                self.function_provider.run(
                                    prompt,
                                    function_json,
                                    self.config,
                                    conversation=[],
                                )
                            )
                            api_response = None
                            api_parameter_mapping = None
                            tokens_used = func_response.total_tokens
                            llm_api_cost = func_response.cost
                            if func_response.is_function_call:
                                detected_function = (
                                    functions.get_function_from_func_name(
                                        func_response.detected_function_name
                                    )
                                )
                                # call the API

                                config = Config()
                                if self.config:
                                    config = self.config
                                params = OperationExecutionParams(
                                    config=config,
                                    api=detected_function.get_api_url(),
                                    method=detected_function.get_api_method(),
                                    query_params=func_response.detected_function_arguments,
                                    body=None,
                                    path=detected_function.get_path(),
                                    header=self.header,
                                    response_obj_200=detected_function.response_obj_200,
                                    function_provider=self.function_provider,
                                    plugin_op_property_map=self.plugin.plugin_op_property_map,
                                )
                                ex = OperationExecutionWithImprompt(params)
                                response = ex.run()
                                # update the mapped_parameters with the response
                                if response and response.original_response:
                                    api_response = response.original_response
                                    x_params_map[prop.name] = (
                                        response.original_response
                                    )
                                    api_parameter_mapping = (
                                        func_response.detected_function_arguments
                                    )
                            tracing.append(
                                {
                                    "step": "x_dependent_resolution",
                                    "property_name": prop.name,
                                    "x_dependent_values": prop.x_dependent,
                                    "prompt": prompt,
                                    "api_parameter_mapping": api_parameter_mapping,
                                    "api_response": api_response,
                                    "processing_time_seconds": time.time()
                                    - start_time1,
                                    "tokens_used": tokens_used,
                                    "llm_api_cost": llm_api_cost,
                                }
                            )
                        except Exception as e:
                            tracing.append(
                                {
                                    "processing_time_seconds": time.time()
                                    - start_time1,
                                    "error": f"Failed to resolve the x parameter: {e}",
                                    "property_name": prop.name,
                                    "x_dependent_values": prop.x_dependent,
                                }
                            )
                            print(f"Failed to resolve the x parameter: {e}")

            if x_params_map and len(x_params_map) > 0:
                start_time2 = time.time()
                prompt = f"Use these values: {x_params_map}, Rerun {request_prompt}".strip()
                # run function calling with function json and
                f_response: FunctionResponse = self.function_provider.run(
                    prompt,
                    original_function_json,
                    self.config,
                    conversation=[],
                )
                tracing.append(
                    {
                        "step": "parameter_remapping",
                        "processing_time_seconds": time.time() - start_time2,
                        "prompt": prompt,
                        "api_parameter_mapping": f_response.detected_function_arguments,
                        "tokens_used": f_response.total_tokens,
                        "llm_api_cost": f_response.cost,
                    }
                )
                if f_response and f_response.is_function_call:
                    return f_response.detected_function_arguments, tracing
        except Exception as e:
            print(f"Failed to resolve the x parameter: {e}")
            tracing.append(
                {
                    "error": f"Failed to run the x parameter resolution: {e}",
                    "mapped_parameters": mapped_parameters,
                }
            )
        return None, tracing

    @classmethod
    def get_pipeline_name(cls) -> str:
        return "oai functions"
