import json

import os, re
import time
from typing import List, Optional
from openplugin import Config, ToolSelectorConfig, PluginOperation, Plugin, \
    PluginSelector, LLMProvider, Message, Response, LLM, Function, Functions
import openai


class OpenAIPluginSelector(PluginSelector):
    def __init__(
            self,
            tool_selector_config: ToolSelectorConfig,
            plugins: List[Plugin],
            config: Optional[Config],
            llm: Optional[LLM]):
        super().__init__(tool_selector_config, plugins, config, llm)

    def initialize_tool_selector(
            self,
            tool_selector_config: ToolSelectorConfig,
            plugins: List[Plugin],
            config: Config,
            llm: LLM
    ):
        if config.openai_api_key is not None:
            openai.api_key = config.openai_api_key
        else:
            openai.api_key = os.environ["OPENAI_API_KEY"]

    def run(self, messages: List[Message]) -> Response:
        start_test_case_time = time.time()
        f_messages = [msg.get_openai_message() for msg in messages if
                      msg.get_openai_message() is not None]

        functions = Functions()
        for plugin in self.plugins:
            functions.add_from_plugin(plugin)

        function_json = functions.get_json()

        count = 0
        is_a_function_call = True
        final_text_response = None
        total_tokens = 0
        detected_plugin_operations = []
        #while is_a_function_call and count < 5:
        count += 1
        response = openai.ChatCompletion.create(
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
            plugin_operation = PluginOperation(
                plugin=detected_plugin,
                api_called=detected_function.get_api_url(),
                mapped_operation_parameters=arguments
            )
            detected_plugin_operations.append(plugin_operation)
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

        response_obj = Response(
            run_completed=True,
            final_text_response=final_text_response,
            detected_plugin_operations=detected_plugin_operations,
            response_time=round(time.time() - start_test_case_time, 2),
            tokens_used=total_tokens,
            llm_api_cost=0
        )
        return response_obj
