import json
import re
import time
from typing import List, Optional
from urllib.parse import parse_qs, urlparse

import openai

from openplugin.bindings.llm_manager_handler import get_llm_response_from_messages
from openplugin.interfaces.models import (
    LLM,
    Config,
    LLMProvider,
    Message,
    Plugin,
    PluginDetectedParams,
    SelectedApiSignatureResponse,
)
from openplugin.interfaces.operation_signature_builder import (
    OperationSignatureBuilder,
)

plugin_operation_prompt = """
// You are an AI assistant.
// Here is a tool you can use, named {name_for_model}. The description for this plugin is: {description_for_model}.
// The Plugin rules:
// 1. Assistant ALWAYS asks user's input for ONLY the MANDATORY parameters BEFORE calling the API.
// 2. Assistant pays attention to instructions given below.
// 3. Create an HTTPS API url that represents this query.
// 4. Use this format: <HTTP VERB> <URL>
//   - An example: GET https://api.example.com/v1/products
// 5. Remove any starting periods and new lines.
// 6. Do not structure as a sentence.
// 7. Never use https://api.example.com/ in the API.

{pre_prompt}

The openapi spec file = {openapi_spec}
The instructions are: {prompt}
"""  # noqa: E501


def _extract_urls(text):
    url_pattern = re.compile(
        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    )
    urls = re.findall(url_pattern, text)
    return urls


class ImpromptOperationSignatureBuilder(OperationSignatureBuilder):
    def __init__(
        self,
        plugin: Plugin,
        config: Optional[Config],
        llm: Optional[LLM],
        pre_prompts: Optional[List[Message]] = None,
        selected_operation: Optional[str] = None,
    ):
        if llm is None:
            llm = LLM(
                provider=LLMProvider.OpenAIChat, model_name="gpt-3.5-turbo-0613"
            )

        super().__init__(plugin, config, llm, pre_prompts, selected_operation)
        self.total_tokens_used = 0
        if config and config.openai_api_key:
            openai.api_key = config.openai_api_key
        else:
            raise ValueError("OpenAI API Key is not configured")

    def run(self, messages: List[Message]) -> SelectedApiSignatureResponse:
        start_test_case_time = time.time()
        prompt = ""
        for message in messages:
            prompt += f"{message.message_type}: {message.content}\n"
        detected_plugins = []
        api_called = None
        mapped_operation_parameters = None
        # TODO Find a better way to find the API called
        openapi_spec_json = self.plugin.get_openapi_doc_json()
        formatted_plugin_operation_prompt = plugin_operation_prompt.format(
            name_for_model=self.plugin.name,
            description_for_model=self.plugin.description,
            pre_prompt=self.plugin.get_plugin_pre_prompts(),
            openapi_spec=json.dumps(openapi_spec_json),
            prompt=prompt,
        )
        response = self.run_llm_prompt(formatted_plugin_operation_prompt)
        method = "get"
        if "post" in response.get("response").lower():
            method = "post"
        elif "put" in response.get("response").lower():
            method = "put"
        elif "delete" in response.get("response").lower():
            method = "delete"
        urls = _extract_urls(response.get("response"))
        for url in urls:
            formatted_url = url.split("?")[0].strip()
            if (
                self.plugin.api_endpoints
                and formatted_url in self.plugin.api_endpoints
            ):
                api_called = formatted_url
                query_dict = parse_qs(urlparse(url).query)
                mapped_operation_parameters = {
                    k: v[0] if isinstance(v, list) and len(v) == 1 else v
                    for k, v in query_dict.items()
                }
                break
        detected_plugins.append(
            PluginDetectedParams(
                plugin=self.plugin,
                api_called=api_called,
                method=method,
                mapped_operation_parameters=mapped_operation_parameters,
            )
        )
        response = SelectedApiSignatureResponse(
            run_completed=True,
            final_text_response=None,
            detected_plugin_operations=detected_plugins,
            response_time=round(time.time() - start_test_case_time, 2),
            tokens_used=response.get("usage"),
            llm_api_cost=response.get("cost"),
        )
        return response

    def get_plugin_by_name(self, name: str):
        if self.plugin.name == name:
            return self.plugin
        return None

    def run_llm_prompt(self, prompt: str):
        if self.llm is None:
            raise ValueError("LLM is not configured")
        if self.config is None:
            raise ValueError("Config is not configured")

        llm_api_key = None
        if (
            self.llm.provider == LLMProvider.OpenAI
            or self.llm.provider == LLMProvider.OpenAIChat
        ):
            llm_api_key = self.config.openai_api_key
        elif self.llm.provider == LLMProvider.Cohere:
            llm_api_key = self.config.cohere_api_key
        elif self.llm.provider == LLMProvider.GooglePalm:
            llm_api_key = self.config.google_palm_key

        if llm_api_key is None:
            raise ValueError("LLM API Key is not configured")

        msgs = []

        # add signature helpers
        """
        try:
            if self.plugin.plugin_operations:
                for api_endpoint in self.plugin.plugin_operations.keys():
                    plugin_operation_method_map = self.plugin.plugin_operations.get(
                        api_endpoint
                    )
                    if plugin_operation_method_map:
                        for method in plugin_operation_method_map.keys():
                            ops = plugin_operation_method_map.get(method)
                            if ops and ops.prompt_signature_helpers:
                                for (
                                    prompt_signature_helper
                                ) in ops.prompt_signature_helpers:
                                    content = (
                                        f"For operation={ops} and method={method}, "
                                        f"{prompt_signature_helper}",
                                    )

                                    msgs.append(
                                        {"role": "assistant", "content": content}
                                    )
        except Exception as e:
            print("++++")
            print(e)
        """

        if self.pre_prompts:
            for pre_prompt in self.pre_prompts:
                msgs.append(pre_prompt.get_openai_message())
        msgs.append({"role": "user", "content": prompt})
        return get_llm_response_from_messages(
            msgs=msgs,
            model=self.llm.model_name,
            llm_api_key=llm_api_key,
            temperature=self.llm.temperature,
            max_tokens=self.llm.max_tokens,
            top_p=self.llm.top_p,
            frequency_penalty=self.llm.frequency_penalty,
            presence_penalty=self.llm.presence_penalty,
        )

    @classmethod
    def get_pipeline_name(cls) -> str:
        return "imprompt basic"
