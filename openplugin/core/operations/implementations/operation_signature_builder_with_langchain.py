import time
from typing import List, Optional


from openplugin.core import (
    LLM,
    Config,
    Functions,
    Message,
    FunctionResponse,
    MessageType,
    Plugin,
    PluginDetectedParams,
    SelectedApiSignatureResponse,
)

from ..operation_signature_builder import (
    OperationSignatureBuilder,
)


# Custom API Signature Selector for OpenAI
class LangchainOperationSignatureBuilder(OperationSignatureBuilder):

    def __init__(
        self,
        plugin: Plugin,
        llm: LLM,
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
        self.llm = llm
        if self.llm.provider.lower() not in ["openai", "fireworks", "mistral"]:
            raise ValueError(f"LLM provider {llm.provider} not supported")
        super().__init__(plugin, llm, config, pre_prompts, selected_operation)
        if config and config.openai_api_key:
            self.openai_api_key = config.openai_api_key
        else:
            raise ValueError("OpenAI API Key is not configured")

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
        print("****8")
        print(request_prompt)
        print(function_json)
        final_text_response = None
        detected_plugin_operations: list[PluginDetectedParams] = []
        try:
            func_response: FunctionResponse = self.llm.run_functions(
                request_prompt, function_json
            )
            llm_calls.append(
                {
                    "used_for": "signature_builder",
                    "response": func_response.response_content,
                    "model": self.llm.model_name,
                    "cost": func_response.cost,
                    "usage": func_response.usage,
                    "messages": f_messages,
                    "request_prompt": request_prompt,
                    "llm_latency_seconds": func_response.llm_latency_seconds,
                    "response_prompt": func_response.response_content,
                    "temperature": self.llm.temperature,
                    "max_tokens": self.llm.max_tokens,
                    "top_p": self.llm.top_p,
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
            final_text_response=final_text_response,
            detected_plugin_operations=detected_plugin_operations,
            response_time=time.time() - start_test_case_time,
            tokens_used=func_response.total_tokens,
            llm_api_cost=func_response.cost,
            llm_calls=llm_calls,
        )
        return response_obj

    @classmethod
    def get_pipeline_name(cls) -> str:
        return "oai functions"
