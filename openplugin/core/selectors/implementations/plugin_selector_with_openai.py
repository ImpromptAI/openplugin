import time
from typing import List, Optional

import litellm

from ...config import Config
from ...function_providers import FunctionProvider
from ...functions import Functions, build_function_name
from ...messages import Message
from ...plugin import Plugin
from ...plugin_detected import PluginDetected, SelectedPluginsResponse
from ..plugin_selector import PluginSelector


class OpenAIPluginSelector(PluginSelector):
    def __init__(
        self,
        plugins: List[Plugin],
        config: Optional[Config],
        function_provider: Optional[FunctionProvider],
    ):
        super().__init__(plugins, config, function_provider)
        # Initialize the OpenAI API key from the configuration or environment variable
        if config and config.openai_api_key:
            self.openai_api_key = config.openai_api_key
        else:
            raise ValueError("OpenAI API Key is not configured")

    def run(self, messages: List[Message]) -> SelectedPluginsResponse:
        start_test_case_time = time.time()

        f_messages = [
            msg.get_openai_message()
            for msg in messages
            if msg.get_openai_message() is not None
        ]
        functions = Functions()
        for plugin in self.plugins:
            functions.add_from_plugin(plugin)
        if len(functions.functions) == 0:
            return SelectedPluginsResponse(
                run_completed=True,
                final_text_response="No functions found",
                detected_plugin=None,
                response_time=round(time.time() - start_test_case_time, 2),
                tokens_used=0,
                llm_api_cost=0,
            )
        helper_pre_prompt = functions.get_examples_prompt()
        if helper_pre_prompt and len(helper_pre_prompt) > 0:
            f_messages.insert(0, {"role": "assistant", "content": helper_pre_prompt})
        function_json = functions.get_json()

        count = 0
        final_text_response = None
        total_tokens = 0

        # while is_a_function_call and count < 5:
        count += 1
        temperature = 0.0
        if self.function_provider:
            temperature = self.function_provider.get_temperature()
        max_tokens = 1024
        if self.function_provider:
            max_tokens = self.function_provider.get_max_tokens()
        n = 1
        top_p = 1.0
        if self.function_provider:
            top_p = self.function_provider.get_top_p()
        litellm.api_key = self.openai_api_key
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
        message = response["choices"][0]["message"]
        detected_plugins = []
        if message.get("function_call"):
            # validate for litellm character restrictions: r"^[a-zA-Z0-9_-]{1,64}$"
            function_name = build_function_name(message.get("function_call").name)
            detected_plugin = functions.get_plugin_from_func_name(function_name)
            detected_function = functions.get_function_from_func_name(function_name)
            PluginDetected(
                plugin=detected_plugin,
                api_called=detected_function.get_api_url(),
                method=detected_function.get_api_method(),
                path=detected_function.get_api_path(),
            )
            detected_plugins.append(detected_plugin.manifest_url)
            f_messages.append(message)
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

        detected_plugin = None
        if detected_plugins and len(detected_plugins) > 0:
            detected_plugin = detected_plugins[0]
        response_obj = SelectedPluginsResponse(
            run_completed=True,
            final_text_response=final_text_response,
            detected_plugin=detected_plugin,
            response_time=round(time.time() - start_test_case_time, 2),
            tokens_used=total_tokens,
            llm_api_cost=0,
        )
        return response_obj

    @classmethod
    def get_pipeline_name(cls) -> str:
        return "oai functions"
