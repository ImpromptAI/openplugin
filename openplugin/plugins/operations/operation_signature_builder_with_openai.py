import json
import time
from typing import List, Optional

import litellm

from openplugin.plugins.functions import Functions
from openplugin.plugins.models import LLM, Config, Message, MessageType
from openplugin.plugins.plugin import Plugin
from openplugin.plugins.plugin_detected import (
    PluginDetectedParams,
    SelectedApiSignatureResponse,
)

from .operation_signature_builder import (
    OperationSignatureBuilder,
)


# Custom API Signature Selector for OpenAI
class OpenAIOperationSignatureBuilder(OperationSignatureBuilder):
    def __init__(
        self,
        plugin: Plugin,
        config: Optional[Config],
        llm: Optional[LLM],
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

        if llm is None:
            llm = LLM(provider="openai", model_name="gpt-3.5-turbo-0613")
        if llm.provider.lower() != "openai":
            # only support openai for functions now
            llm = LLM(provider="openai", model_name="gpt-3.5-turbo-0613")
            # raise ValueError(f"LLM provider {llm.provider} not supported")
        super().__init__(plugin, config, llm, pre_prompts, selected_operation)
        if config and config.openai_api_key:
            self.openai_api_key = config.openai_api_key
        else:
            raise ValueError("OpenAI API Key is not configured")
        litellm.api_key = self.openai_api_key

    def run(self, messages: List[Message]) -> SelectedApiSignatureResponse:
        start_test_case_time = time.time()

        functions = Functions()
        functions.add_from_plugin(self.plugin, self.selected_operation)
        llm_calls: list = []
        if len(functions.functions) == 0:
            return SelectedApiSignatureResponse(
                run_completed=True,
                final_text_response="No functions found",
                detected_plugin_operations=[],
                response_time=round(time.time() - start_test_case_time, 2),
                tokens_used=0,
                llm_api_cost=0,
                llm_calls=llm_calls,
            )
        helper_pre_prompt = functions.get_prompt_signatures_prompt()
        # if helper_pre_prompt and len(helper_pre_prompt) > 0:
        #    f_messages.insert(0, {"role": "assistant", "content": helper_pre_prompt})

        request_prompt = helper_pre_prompt
        index = 0
        for message in messages:
            if message.message_type == MessageType.HumanMessage:
                if index == len(messages) - 1:
                    message.content = f"#PROMPT={message.content}"
                request_prompt = request_prompt + " " + message.content
            index += 1

        f_messages = [
            msg.get_openai_message()
            for msg in messages
            if msg.get_openai_message() is not None
        ]
        function_json = functions.get_json()
        count = 0
        final_text_response = None
        total_tokens = 0
        llm_api_cost = 0
        detected_plugin_operations: list[PluginDetectedParams] = []
        # while is_a_function_call and count < 5:
        count += 1
        try:
            temperature = 0.0
            if self.llm and self.llm.temperature:
                temperature = self.llm.temperature

            max_tokens = 4096
            if self.llm and self.llm.max_tokens:
                max_tokens = self.llm.max_tokens
            n = 1
            if self.llm and self.llm.n:
                n = self.llm.n
            top_p = 1.0
            if self.llm and self.llm.top_p:
                top_p = self.llm.top_p

            start_time = time.time()
            response = litellm.completion(
                model=self.llm.model_name if self.llm else None,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                n=n,
                messages=f_messages,
                functions=function_json,
                function_call="auto",
            )
            if response.get("choices")[0].get("finish_reason") != "function_call":
                response = litellm.completion(
                    model="gpt-4",
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=top_p,
                    n=n,
                    messages=f_messages,
                    functions=function_json,
                    function_call="auto",
                )
            llm_api_cost = litellm.completion_cost(completion_response=response)
            choices = response.get("choices")

            response_prompt = ""
            if choices and len(choices) > 0:
                response_prompt = choices[0].get("message", {}).get("content")
            llm_latency_seconds = time.time() - start_time

            llm_calls.append(
                {
                    "used_for": "signature_builder",
                    "response": response["choices"],
                    "model": self.llm.model_name if self.llm else None,
                    "cost": llm_api_cost,
                    "usage": response.get("usage"),
                    "messages": f_messages,
                    "request_prompt": request_prompt,
                    "llm_latency_seconds": llm_latency_seconds,
                    "response_prompt": response_prompt,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "top_p": top_p,
                    "status_code": "200",
                }
            )
        except Exception as e:
            print(e)
            return SelectedApiSignatureResponse(
                run_completed=True,
                final_text_response="Failed to run plugin",
                detected_plugin_operations=[],
                response_time=round(time.time() - start_test_case_time, 2),
                tokens_used=0,
                llm_api_cost=0,
                llm_calls=llm_calls,
            )

        message = response["choices"][0]["message"]
        message_json = message.json()
        if (
            message_json
            and isinstance(message_json, dict)
            and message_json.get("function_call")
        ):
            function_name = message_json["function_call"]["name"]
            detected_plugin = functions.get_plugin_from_func_name(function_name)
            detected_function = functions.get_function_from_func_name(function_name)
            arguments = json.loads(message_json["function_call"]["arguments"])

            p_detected = PluginDetectedParams(
                plugin=detected_plugin,
                api_called=detected_function.get_api_url(),
                method=detected_function.get_api_method(),
                mapped_operation_parameters=arguments,
            )
            detected_plugin_operations.append(p_detected)
            f_messages.append(message_json)
            # function_response = str(detected_function.call_api(arguments))
            function_response = f"This is a response from function {function_name}"
            f_messages.append(
                {
                    "role": "function",
                    "name": function_name,
                    "content": function_response,
                }
            )
        else:
            final_text_response = (
                response.get("choices")[0].get("message").get("content")
            )
        total_tokens += response.get("usage").get("total_tokens")

        response_obj = SelectedApiSignatureResponse(
            run_completed=True,
            final_text_response=final_text_response,
            detected_plugin_operations=detected_plugin_operations,
            response_time=time.time() - start_test_case_time,
            tokens_used=total_tokens,
            llm_api_cost=llm_api_cost,
            llm_calls=llm_calls,
        )
        return response_obj

    @classmethod
    def get_pipeline_name(cls) -> str:
        return "oai functions"
