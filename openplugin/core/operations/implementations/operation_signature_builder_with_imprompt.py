"""
import json
import re
import time
from typing import List, Optional
from urllib.parse import parse_qs, urlparse

from loguru import logger

from openplugin.utils import get_llm_response_from_messages


from ...config import Config
from ...function_providers import FunctionProvider
from ...messages import Message
from ...plugin import Plugin
from ...plugin_detected import PluginDetectedParams, SelectedApiSignatureResponse
from ..operation_signature_builder import (
    OperationSignatureBuilder,
)

DEBUG = False
plugin_operation_prompt = '''
You are an AI assistant.
Here is a tool you can use, named {name_for_model}.

The Plugin rules:
 1. Assistant ALWAYS asks user's input for ONLY the MANDATORY parameters BEFORE calling the API.
 2. Assistant pays attention to instructions given below.
 3. Create an HTTPS API url that represents this query.
 4. Use this format: <HTTP VERB> <URL>
    - An example: GET https://api.example.com/v1/products
 5. Remove any starting periods and new lines.
 6. Do not structure as a sentence.
 7. Never use https://api.example.com/ in the API.

{pre_prompt}

The openapi spec file = {openapi_spec}

The instructions are: {prompt}
'''  # noqa: E501


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
        function_provider: FunctionProvider,
        config: Optional[Config],
        pre_prompts: Optional[List[Message]] = None,
        selected_operation: Optional[str] = None,
        use: Optional[str] = None,
        header: Optional[dict] = None,
    ):
        super().__init__(
            plugin,
            function_provider,
            config,
            pre_prompts,
            selected_operation,
            header,
        )
        self.total_tokens_used = 0
        self.use = use

    def run(
        self, messages: List[Message], conversation: Optional[List] = []
    ) -> SelectedApiSignatureResponse:
        start_test_case_time = time.time()
        prompt = ""
        for message in messages:
            prompt += f"{message.message_type}: {message.content}\n"
        detected_plugins = []
        api_called = None
        mapped_operation_parameters = None
        # TODO Find a better way to find the API called
        openapi_spec_json = self.plugin.get_openapi_doc_json()

        if self.use == "bare-swagger":
            formatted_plugin_operation_prompt = plugin_operation_prompt.format(
                name_for_model=self.plugin.name,
                pre_prompt="",
                openapi_spec=json.dumps(openapi_spec_json),
                prompt=prompt,
            )
        elif self.use == "stuffed-swagger":
            stuffed_openapi_spec_json = self.plugin.get_stuffed_openapi_doc_json()
            formatted_plugin_operation_prompt = plugin_operation_prompt.format(
                name_for_model=self.plugin.name,
                pre_prompt="",
                openapi_spec=json.dumps(stuffed_openapi_spec_json),
                prompt=prompt,
            )
        else:
            formatted_plugin_operation_prompt = plugin_operation_prompt.format(
                name_for_model=self.plugin.name,
                pre_prompt=self.plugin.get_plugin_helpers(),
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
            if self.plugin.api_endpoints and formatted_url in self.plugin.api_endpoints:
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
                path=None,
            )
        )
        response = SelectedApiSignatureResponse(
            run_completed=True,
            final_text_response=None,
            detected_plugin_operations=detected_plugins,
            response_time=round(time.time() - start_test_case_time, 2),
            tokens_used=response.get("usage"),
            llm_api_cost=response.get("cost"),
            llm_calls=[],
        )
        return response

    def get_plugin_by_name(self, name: str):
        if self.plugin.name == name:
            return self.plugin
        return None

    def run_llm_prompt(self, prompt: str):
        if self.function_provider is None:
            raise ValueError("LLM is not configured")
        if self.config is None:
            raise ValueError("Config is not configured")
        msgs = []
        if self.pre_prompts:
            for pre_prompt in self.pre_prompts:
                msgs.append(pre_prompt.get_openai_message())
        msgs.append({"role": "user", "content": prompt})
        if DEBUG:
            logger.info(f"=-=-=-=-=-= LLM -=--=-=-=-=-=--=\n{self.function_provider}")
            logger.info(f"\n=-=-=-=-=-=- PROMPT =--=-=-=-=-=--=\n{prompt}")
        response = get_llm_response_from_messages(
            msgs=msgs,
            model=self.function_provider.get_model_name(),
            llm_api_key=None,
            temperature=self.function_provider.get_temperature(),
            max_tokens=self.function_provider.get_max_tokens(),
            top_p=self.function_provider.get_top_p(),
            aws_access_key_id=self.config.aws_access_key_id,
            aws_region_name=self.config.aws_region_name,
        )
        if DEBUG:
            logger.info(
                f"=-=-=-=-=-=-=--=-=-=-=-=--=\nuse= {self.use}\nresponse= {response}"
            )
        return response

    @classmethod
    def get_pipeline_name(cls) -> str:
        return "imprompt basic"
"""
