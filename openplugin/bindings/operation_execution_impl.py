import json
import time
import traceback
from urllib.parse import urlencode

import jinja2
import requests
from tenacity import retry, stop_after_attempt, wait_random_exponential

from openplugin.bindings.llm_manager_handler import get_llm_response_from_messages
from openplugin.interfaces.models import (
    OperationExecutionParams,
    OperationExecutionResponse,
)
from openplugin.interfaces.operation_execution import OperationExecution

CLARIFYING_QUESTION_PROMPT = "#INPUT_JSON\n This is a json describing what is missing in the API call. Write a clarifying question asking user to provide missing informations. Make sure you prettify the parameter name. Don't mention about JSON or API call."
DEFAULT_MODEL_NAME = "gpt-3.5-turbo-0613"


class ExecutionException(Exception):
    def __init__(self, message, metadata=None):
        super().__init__(message)
        self.metadata = metadata if metadata is not None else {}


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
            return (
                response.json(),
                response.status_code,
                response.elapsed.total_seconds(),
            )
        elif response.status_code == 400:
            return (
                response.text,
                response.status_code,
                response.elapsed.total_seconds(),
            )
        elif method.upper() == "GET":
            encoded_params = urlencode(params)
            full_url = f"{url}?{encoded_params}"
            response = requests.get(full_url)
            if response.status_code == 200:
                return (
                    response.json(),
                    response.status_code,
                    response.elapsed.total_seconds(),
                )
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
        self.config = params.config
        super().__init__(params)

    def run(self) -> OperationExecutionResponse:
        try:
            response_json, status_code, api_call_response_seconds = _call(
                self.params.api,
                self.params.method,
                self.params.header,
                self.params.query_params,
                self.params.body,
            )

        except Exception as e:
            raise ExecutionException(str(e), metadata={})

        template_response = None
        template_str = self.params.plugin_response_template
        template_execution_status_code = "200"
        template_execution_response_seconds = None
        if template_str and len(template_str) > 0:
            try:
                # response time
                start_time = time.time()
                template = jinja2.Template(template_str)
                template_response = template.render(json_data=response_json)
                template_execution_response_seconds = time.time() - start_time
            except Exception as e:
                template_execution_status_code = "500"
                raise ExecutionException(
                    str(e),
                    metadata={
                        "api_call_status_code": status_code,
                        "api_call_response_seconds": api_call_response_seconds,
                    },
                )

        cleanup_helper_status_code = None
        cleanup_helper_response_seconds = None

        clarifying_question_status_code = None
        clarifying_question_response_seconds = None

        summary_response_status_code = None
        summary_response_seconds = None

        cleanup_response = None
        is_a_clarifying_question = False
        clarifying_response = None

        llm_api_key = None
        if self.config.provider.lower() == "cohere":
            llm_api_key = self.config.cohere_api_key
        elif self.config.provider.lower() == "openai":
            llm_api_key = self.config.openai_api_key
        elif self.config.provider.lower() == "google":
            llm_api_key = self.config.google_palm_key
        elif self.config.provider.lower() == "aws":
            llm_api_key = self.config.aws_secret_access_key

        if status_code == 400:
            is_a_clarifying_question = True
            try:
                start_time = time.time()
                model_name = DEFAULT_MODEL_NAME
                if (
                    self.params.llm is not None
                    and self.params.llm.model_name is not None
                ):
                    model_name = self.params.llm.model_name

                response = get_llm_response_from_messages(
                    msgs=[
                        {
                            "role": "user",
                            "content": CLARIFYING_QUESTION_PROMPT.replace(
                                "#INPUT_JSON", response_json
                            ),
                        }
                    ],
                    temperature=self.params.get_temperature(),
                    max_tokens=self.params.get_max_tokens(),
                    top_p=self.params.get_top_p(),
                    frequency_penalty=self.params.get_frequency_penalty(),
                    presence_penalty=self.params.get_presence_penalty(),
                    model=model_name,
                    llm_api_key=llm_api_key,
                    aws_access_key_id=self.config.aws_access_key_id,
                    aws_region_name=self.config.aws_region_name,
                )
                clarifying_response = response.get("response")
                clarifying_question_status_code = "200"
                clarifying_question_response_seconds = time.time() - start_time
            except Exception as e:
                clarifying_response = f"Failed: {e}"
                clarifying_question_status_code = "500"
        elif self.params.post_processing_cleanup_prompt:
            try:
                start_time = time.time()
                if template_response:
                    c_prompt = f"{self.params.post_processing_cleanup_prompt} For: {template_response}"
                else:
                    c_prompt = f"{self.params.post_processing_cleanup_prompt} For: {response_json}"

                model_name = DEFAULT_MODEL_NAME
                if (
                    self.params.llm is not None
                    and self.params.llm.model_name is not None
                ):
                    model_name = self.params.llm.model_name
                response = get_llm_response_from_messages(
                    msgs=[{"role": "user", "content": c_prompt}],
                    model=model_name,
                    llm_api_key=llm_api_key,
                    aws_access_key_id=self.config.aws_access_key_id,
                    aws_region_name=self.config.aws_region_name,
                    max_tokens=self.params.get_max_tokens(),
                    top_p=self.params.get_top_p(),
                    frequency_penalty=self.params.get_frequency_penalty(),
                    presence_penalty=self.params.get_presence_penalty(),
                )
                cleanup_response = response.get("response")
                cleanup_helper_response_seconds = time.time() - start_time
                cleanup_helper_status_code = "200"
            except Exception as e:
                cleanup_helper_status_code = "500"
                cleanup_response = f"Failed: {e}"

        summary_response = None
        if (
            self.params.post_call_evaluator_prompt
            and len(self.params.post_call_evaluator_prompt) > 0
        ):
            try:
                start_time = time.time()
                if cleanup_response:
                    summary_snippet = cleanup_response
                elif template_response:
                    summary_snippet = template_response
                else:
                    summary_snippet = response_json

                summary_prompt = f"""{self.params.post_call_evaluator_prompt}
                {summary_snippet}
                """
                model_name = DEFAULT_MODEL_NAME
                summary_response = get_llm_response_from_messages(
                    msgs=[{"role": "user", "content": summary_prompt}],
                    model=model_name,
                    llm_api_key=llm_api_key,
                    aws_access_key_id=self.config.aws_access_key_id,
                    aws_region_name=self.config.aws_region_name,
                    max_tokens=self.params.get_max_tokens(),
                    top_p=self.params.get_top_p(),
                    frequency_penalty=self.params.get_frequency_penalty(),
                    presence_penalty=self.params.get_presence_penalty(),
                )
                summary_response = summary_response.get("response")
                summary_response_status_code = "200"
                summary_response_seconds = time.time() - start_time
            except Exception as e:
                summary_response_status_code = "500"
                summary_response = f"Failed: {e}"

        return OperationExecutionResponse(
            original_response=response_json,
            clarifying_response=clarifying_response,
            cleanup_response=cleanup_response,
            template_response=template_response,
            summary_response=summary_response,
            is_a_clarifying_question=is_a_clarifying_question,
            api_call_status_code=status_code,
            api_call_response_seconds=api_call_response_seconds,
            template_execution_status_code=template_execution_status_code,
            template_execution_response_seconds=template_execution_response_seconds,
            cleanup_helper_status_code=cleanup_helper_status_code,
            cleanup_helper_response_seconds=cleanup_helper_response_seconds,
            summary_response_status_code=summary_response_status_code,
            summary_response_seconds=summary_response_seconds,
            clarifying_question_status_code=clarifying_question_status_code,
            clarifying_question_response_seconds=clarifying_question_response_seconds,
        )
