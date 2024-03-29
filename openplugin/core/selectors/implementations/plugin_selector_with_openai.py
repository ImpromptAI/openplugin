import time
import litellm
from typing import List, Optional

from openplugin.core import (
    LLM,
    Config,
    Functions,
    Message,
    Plugin,
    PluginDetected,
    SelectedPluginsResponse,
)

from ..plugin_selector import PluginSelector


class OpenAIPluginSelector(PluginSelector):
    def __init__(
        self,
        plugins: List[Plugin],
        config: Optional[Config],
        llm: Optional[LLM],
    ):
        super().__init__(plugins, config, llm)
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
        if self.llm and self.llm.temperature:
            temperature = self.llm.temperature
        max_tokens = 1024
        if self.llm and self.llm.max_tokens:
            max_tokens = self.llm.max_tokens
        n = 1
        if self.llm and self.llm.n:
            n = self.llm.n
        top_p = 1.0
        if self.llm and self.llm.top_p:
            top_p = self.llm.top_p
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
            function_name = message.get("function_call").name
            detected_plugin = functions.get_plugin_from_func_name(function_name)
            detected_function = functions.get_function_from_func_name(function_name)
            p_detected = PluginDetected(
                plugin=detected_plugin,
                api_called=detected_function.get_api_url(),
                method=detected_function.get_api_method(),
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
