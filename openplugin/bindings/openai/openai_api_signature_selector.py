import os
import json
import time
from typing import List, Optional
from .openai_helpers import chat_completion_with_backoff
from openplugin import Config, ToolSelectorConfig, PluginDetectedParams, Plugin, \
    ApiSignatureSelector, Message, SelectedApiSignatureResponse, LLM, Functions


class OpenAIApiSignatureSelector(ApiSignatureSelector):
    def __init__(
            self,
            tool_selector_config: ToolSelectorConfig,
            plugin: Plugin,
            config: Optional[Config],
            llm: Optional[LLM]):
        super().__init__(tool_selector_config, plugin, config, llm)
        if config.openai_api_key is not None:
            self.openai_api_key = config.openai_api_key
        else:
            self.openai_api_key = os.environ["OPENAI_API_KEY"]

    def run(self, messages: List[Message]) -> SelectedApiSignatureResponse:
        start_test_case_time = time.time()
        f_messages = [msg.get_openai_message() for msg in messages if
                      msg.get_openai_message() is not None]
        functions = Functions()
        functions.add_from_plugin(self.plugin)
        if len(functions.functions) == 0:
            return SelectedApiSignatureResponse(
                run_completed=True,
                final_text_response="No functions found",
                detected_plugin_operations=[],
                response_time=round(time.time() - start_test_case_time, 2),
                tokens_used=0,
                llm_api_cost=0
            )
        helper_pre_prompt = functions.get_prompt_signatures_prompt()
        if helper_pre_prompt and len(helper_pre_prompt) > 0:
            f_messages.insert(0, {"role": "assistant", "content": helper_pre_prompt})
        function_json = functions.get_json()
        count = 0
        is_a_function_call = True
        final_text_response = None
        total_tokens = 0
        detected_plugin_operations = []
        # while is_a_function_call and count < 5:
        count += 1
        response = chat_completion_with_backoff(
            openai_api_key=self.openai_api_key,
            model=self.llm.model_name,
            messages=f_messages,
            functions=function_json,
            function_call="auto"
        )
        message = response["choices"][0]["message"]
        if message.get("function_call"):
            is_a_function_call = True
            function_name = message["function_call"]["name"]
            detected_plugin = functions.get_plugin_from_func_name(function_name)
            detected_function = functions.get_function_from_func_name(function_name)
            arguments = json.loads(message["function_call"]["arguments"])
            p_detected = PluginDetectedParams(
                plugin=detected_plugin,
                api_called=detected_function.get_api_url(),
                method=detected_function.get_api_method(),
                mapped_operation_parameters=arguments
            )
            detected_plugin_operations.append(p_detected)
            f_messages.append(message)
            # function_response = str(detected_function.call_api(arguments))
            function_response = f"This is a response from function {function_name}"
            f_messages.append({
                "role": "function",
                "name": function_name,
                "content": function_response,
            })
        else:
            is_a_function_call = False
            final_text_response = response.get("choices")[0].get("message").get(
                "content")
        total_tokens += response.get("usage").get("total_tokens")

        response_obj = SelectedApiSignatureResponse(
            run_completed=True,
            final_text_response=final_text_response,
            detected_plugin_operations=detected_plugin_operations,
            response_time=round(time.time() - start_test_case_time, 2),
            tokens_used=total_tokens,
            llm_api_cost=0
        )
        return response_obj
