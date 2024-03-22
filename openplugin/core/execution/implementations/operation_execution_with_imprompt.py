import json
import time
from urllib.parse import urlencode

import requests
from tenacity import RetryError, retry, stop_after_attempt, wait_random_exponential

from openplugin.utils import get_llm_response_from_messages

from ..operation_execution import (
    OperationExecution,
    OperationExecutionParams,
    OperationExecutionResponse,
)

CLARIFYING_QUESTION_PROMPT = "#INPUT_JSON\n This is a json describing what is missing in the API call. Write a clarifying question asking user to provide missing informations. Make sure you prettify the parameter name. Don't mention about JSON or API call."  # noqa: E501
DEFAULT_MODEL_NAME = "gpt-3.5-turbo-0613"


class ExecutionException(Exception):
    def __init__(self, message, metadata=None):
        super().__init__(message)
        self.metadata = metadata if metadata is not None else {}


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(2))
def _call(url, method="GET", headers=None, params=None, body=None):
    try:
        if body is not None and isinstance(body, dict):
            if method.upper() == "POST" and not body and params:
                body = params
                params = None
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
                    raise ExecutionException(
                        "API Execution Failed",
                        metadata={
                            "status_code": response.status_code,
                            "response": response.text,
                        },
                    )
                if response_json.get("error"):
                    raise ExecutionException(
                        "API Execution Failed",
                        metadata={
                            "status_code": response.status_code,
                            "response": response.text,
                        },
                    )
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
        raise ExecutionException(
            "API Execution Failed",
            metadata={
                "status_code": response.status_code,
                "response": response.text,
            },
        )
    except ExecutionException as e:
        raise e
    except Exception as e:
        raise Exception("{}".format(e))


class OperationExecutionWithImprompt(OperationExecution):
    def __init__(self, params: OperationExecutionParams):
        self.config = params.config
        super().__init__(params)

    def run(self) -> OperationExecutionResponse:
        try:
            print(f"API= {self.params.api}")
            print(f"METHOD= {self.params.method}")
            print(f"HEADER= {self.params.header}")
            print(f"QUERY PARAM= {self.params.query_params}")
            print(f"BODY= {self.params.body}")
            response_json, status_code, api_call_response_seconds = _call(
                self.params.api,
                self.params.method,
                self.params.header,
                self.params.query_params,
                self.params.body,
            )
        except RetryError as e:
            original_exception = e.__cause__
            raise ExecutionException(
                str(original_exception),
                metadata={
                    "api_call_status_code": 500,
                    "api_call_response_seconds": 0,
                },
            )
        except Exception as e:
            raise ExecutionException(str(e), metadata={})

        clarifying_question_status_code = None
        clarifying_question_response_seconds = None
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

        llm_calls = []
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
                llm_call_details = response.get("llm_details", {})
                llm_call_details["used_for"] = "clarifying_question"
                llm_calls.append(llm_call_details)
                clarifying_response = response.get("response")
                clarifying_question_status_code = "200"
                clarifying_question_response_seconds = time.time() - start_time
            except Exception as e:
                clarifying_response = f"Failed: {e}"
                clarifying_question_status_code = "500"

        return OperationExecutionResponse(
            original_response=response_json,
            clarifying_response=clarifying_response,
            is_a_clarifying_question=is_a_clarifying_question,
            api_call_status_code=status_code,
            api_call_response_seconds=api_call_response_seconds,
            clarifying_question_status_code=clarifying_question_status_code,
            llm_calls=llm_calls,
            clarifying_question_response_seconds=clarifying_question_response_seconds,
        )
