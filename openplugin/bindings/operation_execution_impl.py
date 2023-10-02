import json
import os
import traceback

import requests
from tenacity import retry, stop_after_attempt, wait_random_exponential

from openplugin.bindings.openai.openai_helpers import chat_completion_with_backoff
from openplugin.interfaces.models import (
    OperationExecutionParams,
    OperationExecutionResponse,
)
from openplugin.interfaces.operation_execution import OperationExecution


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(2))
def _call(url, method="GET", headers=None, params=None, body=None):
    try:
        if body and isinstance(body, dict):
            body = json.dumps(body)
            headers["Content-Type"] = "application/json"
        # hack for email API
        if params and params.get("content") is not None:
            params["content"] = (
                params["content"]
                .replace("/edit)", "/edit )")
                .replace(".txt)", ".txt )")
            )
        response = requests.request(
            method.upper(), url, headers=headers, params=params, data=body
        )
        # print(response.status_code)
        # print(response.json())
        if response.status_code == 200:
            response_json = response.json()
            if not isinstance(response_json, list):
                if response_json.get("message") and response_json.get(
                    "message"
                ).startswith("Internal Server Error"):
                    failed_message = (
                        f"API: {url}, Params: {params},Status code: "
                        f"{response.status_code}, Response: {response.text[0:100]}..."
                    )
                    raise Exception("{}".format(failed_message))
                if response_json.get("error"):
                    failed_message = (
                        f"API: {url}, Params: {params},Status code: "
                        f"{response.status_code}, Response: {response.text[0:100]}..."
                    )
                    raise Exception("{}".format(failed_message))
            return response.json()
        failed_message = (
            f"API: {url}, Params: {params},Status code: "
            f"{response.status_code}, Response: {response.text[0:100]}..."
        )
        raise Exception("{}".format(failed_message))
    except Exception as e:
        traceback.print_exc()
        raise Exception("{}".format(e))


class OperationExecutionImpl(OperationExecution):
    def __init__(self, params: OperationExecutionParams):
        if params.openai_api_key is not None:
            self.openai_api_key = params.openai_api_key
        else:
            self.openai_api_key = os.environ["OPENAI_API_KEY"]
        super().__init__(params)

    def run(self) -> OperationExecutionResponse:
        try:
            response_json = _call(
                self.params.api,
                self.params.method,
                self.params.header,
                self.params.query_params,
                self.params.body,
            )
        except Exception as e:
            raise Exception("{}".format(e.args[0].result()))
        post_cleanup_text = None
        if self.params.post_processing_cleanup_prompt:
            c_prompt = (
                f"{self.params.post_processing_cleanup_prompt} For: {response_json}"
            )
            model_name = "gpt-3.5-turbo-0613"
            if self.params.llm is not None and self.params.llm.model_name is not None:
                model_name = self.params.llm.model_name
            response = chat_completion_with_backoff(
                openai_api_key=self.openai_api_key,
                model=model_name,
                messages=[{"role": "user", "content": c_prompt}],
            )
            try:
                post_cleanup_text = response["choices"][0]["message"]["content"]
            except Exception as e:
                print(e)
        return OperationExecutionResponse(
            response=response_json, post_cleanup_text=post_cleanup_text
        )
