import json
import time
import traceback
import urllib.parse
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests
from jsonpath_ng import parse
from loguru import logger
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
        # if isinstance(body, str):
        #    body = json.loads(body)

        response = requests.request(
            method.upper(), url, headers=headers, params=params, data=body
        )
        if str(response.status_code) == "403" and method.lower() == "get":
            query_string = urllib.parse.urlencode(params)
            response = requests.request(
                method.upper(),
                f"{url}?{query_string}",
                headers=headers,
                params=params,
                data=body,
            )
        if response.status_code == 200 or response.status_code == 201:
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
        elif response.status_code == 400 or response.status_code == 422:
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
            f"API Execution Failed: status_code={response.status_code}, response={response.text}",
            metadata={
                "status_code": response.status_code,
                "response": response.text,
            },
        )
    except ExecutionException as e:
        raise e
    except Exception as e:
        raise Exception("{}".format(e))


def build_post_body_obj(op_property):
    body_obj = None
    if op_property and op_property.get("requestBody"):
        body_obj = {}
        body_properties = (
            op_property.get("requestBody", {})
            .get("content", {})
            .get("application/json", {})
            .get("schema", {})
            .get("properties")
        )
        for prop in body_properties.keys():
            body_obj[prop] = None
    return body_obj


def process_x_dep_array(
    response_json: list,
    server: Optional[str],
    path: str,
    method: str,
    lookup_parameter: str,
    lookup_additional_parameters: dict = {},
    plugin_op_property_map: Optional[Dict[str, Dict[str, Dict]]] = None,
    headers=None,
    parameter_name=None,
):
    responses = []
    op_property = None
    if plugin_op_property_map:
        for p in plugin_op_property_map.keys():
            for m in plugin_op_property_map[p].keys():
                if p == path and m == method:
                    op_property = plugin_op_property_map[p][m]

    query_params_obj: Optional[Dict[str, Any]] = None
    if op_property and op_property.get("parameters"):
        for prop in op_property.get("parameters", []):
            if prop.get("in") == "query":
                if query_params_obj is None:
                    query_params_obj = {}
                query_params_obj[prop.get("name")] = None

    body_obj: Optional[Dict[str, Any]] = None
    if op_property and op_property.get("requestBody"):
        body_obj = {}
        body_properties = (
            op_property.get("requestBody", {})
            .get("content", {})
            .get("application/json", {})
            .get("schema", {})
            .get("properties")
        )
        for prop in body_properties.keys():
            body_obj[prop] = None

    response_json = response_json[:5]
    traces = []
    for r_obj in response_json:
        x_lookup_tracing: Dict[str, Any] = {}
        try:
            mapped_value = None
            mapped_value_original = None
            if isinstance(r_obj, int) or isinstance(r_obj, str):
                mapped_value = str(r_obj)
                mapped_value_original = r_obj
            elif parameter_name and isinstance(r_obj, dict):
                mapped_value = str(r_obj.get(parameter_name))
                mapped_value_original = r_obj.get(parameter_name)

            if mapped_value:
                server_url = path
                if server:
                    if server.endswith("/") and server_url.startswith("/"):
                        server_url = server + server_url[1:]
                    else:
                        server_url = server + server_url

                if lookup_parameter.startswith("$request.path."):
                    param = lookup_parameter.split("$request.path.")[1]
                    server_url = server_url.replace(
                        "{" + f"{param.strip()}" + "}", mapped_value
                    )
                if lookup_additional_parameters:
                    for key, value in lookup_additional_parameters.items():
                        if key.startswith("$request.path."):
                            param = key.split("$request.path.")[1]
                            server_url = server_url.replace(f"{param}", str(value))

                if query_params_obj:
                    if lookup_parameter.startswith("$request.query."):
                        jsonpath_expression = parse(
                            "$." + lookup_parameter.split("$request.query.")[1]
                        )
                        jsonpath_expression.update(query_params_obj, mapped_value)
                    if lookup_additional_parameters:
                        for key, value in lookup_additional_parameters.items():
                            if key.startswith("$request.query."):
                                jsonpath_expression = parse(
                                    "$."
                                    + lookup_parameter.split("$request.query.")[1]
                                )
                                jsonpath_expression.update(
                                    query_params_obj, str(value)
                                )
                    server_url = (
                        server_url + "?" + urllib.parse.urlencode(query_params_obj)
                    )

                if body_obj:
                    if lookup_parameter.startswith("$request.body."):
                        jsonpath_expression = parse(
                            "$." + lookup_parameter.split("$request.body.")[1]
                        )
                        jsonpath_expression.update(body_obj, mapped_value_original)
                    if lookup_additional_parameters:
                        for key, value in lookup_additional_parameters.items():
                            if key.startswith("$request.body."):
                                jsonpath_expression = parse(
                                    "$." + lookup_parameter.split("$request.body")[1]
                                )
                                jsonpath_expression.update(body_obj, str(value))

                rj, status_code, api_call_response_seconds = _call(
                    server_url,
                    method=method,
                    headers=headers,
                    params=None,
                    body=body_obj,
                )

                # add tracing
                x_lookup_tracing["resolving_obj"] = r_obj
                x_lookup_tracing["lookup_parameter"] = lookup_parameter
                x_lookup_tracing["lookup_additional_parameters"] = (
                    lookup_additional_parameters
                )
                x_lookup_tracing["path"] = path
                x_lookup_tracing["method"] = method
                if parameter_name:
                    x_lookup_tracing["parameter_name"] = parameter_name
                x_lookup_tracing["server_url"] = server_url
                if body_obj:
                    x_lookup_tracing["body"] = body_obj
                x_lookup_tracing["api_call_response_seconds"] = (
                    api_call_response_seconds
                )
                x_lookup_tracing["status_code"] = status_code
                x_lookup_tracing["response"] = rj

                if status_code and (status_code == 200 or status_code == 201):
                    key = f"{parameter_name}_op_resolved_key"
                    if isinstance(r_obj, dict):
                        r_obj[key] = rj
                    else:
                        r_obj = rj
                else:
                    x_lookup_tracing["error"] = (
                        f"Error: API Return Code= {status_code}"
                    )
                responses.append(r_obj)
        except Exception as e:
            traceback.print_exc()
            print(e)
            x_lookup_tracing["error"] = f"Error: {e}"
            responses.append(r_obj)
        traces.append(x_lookup_tracing)
    return responses, traces


class OperationExecutionWithImprompt(OperationExecution):
    def __init__(self, params: OperationExecutionParams):
        self.config = params.config
        super().__init__(params)

    def run(self) -> OperationExecutionResponse:
        missing_parameters = self.get_missing_required_parameter()
        if missing_parameters and len(missing_parameters) > 0:
            is_a_clarifying_question = True
            start_time = time.time()
            if self.params.enable_ui_form_controls:
                clarifying_response = missing_parameters
            else:
                missing_param_str = ", ".join(
                    [item["name"] for item in missing_parameters]
                )
                clarifying_response = f"[CLARIFYING_QUESTION] Please provide the following missing parameters: {missing_param_str}"

            clarifying_question_status_code = "200"
            clarifying_question_response_seconds = time.time() - start_time

            return OperationExecutionResponse(
                original_response={},
                clarifying_response=clarifying_response,
                is_a_clarifying_question=is_a_clarifying_question,
                api_call_status_code=None,
                api_call_response_seconds=0,
                clarifying_question_status_code=clarifying_question_status_code,
                llm_calls=[],
                clarifying_question_response_seconds=clarifying_question_response_seconds,
                x_lookup_tracing=[],
                missing_params=missing_parameters,
            )

        try:
            x_lookup_tracing = []
            logger.info(
                f"\n[API EXECUTION_DATA] API= {self.params.api}, METHOD= {self.params.method}, HEADER= {self.params.header}, QUERY PARAM= {self.params.query_params}, BODY= {self.params.body}"
            )
            response_json, status_code, api_call_response_seconds = _call(
                self.params.api,
                self.params.method,
                self.params.header,
                self.params.query_params,
                self.params.body,
            )
            if (
                status_code == 200
                and response_json
                and self.params.response_obj_200
                and isinstance(response_json, list)
            ):
                if (
                    self.params.response_obj_200.get("schema", {}).get("type")
                    == "array"
                ):
                    items = self.params.response_obj_200.get("schema", {}).get(
                        "items", {}
                    )
                    if items.get("x-lookup") is not None:
                        if items.get("type") in [
                            "string",
                            "number",
                            "integer",
                            "boolean",
                        ]:
                            path = items.get("x-lookup").get("path")
                            method = items.get("x-lookup").get("method")
                            lookup_parameter = items.get("x-lookup").get("parameter")
                            lookup_additional_parameters = items.get("x-lookup").get(
                                "additional_parameters"
                            )
                            response_json, tracing = process_x_dep_array(
                                response_json,
                                self.params.response_obj_200.get("server"),
                                path,
                                method,
                                lookup_parameter,
                                lookup_additional_parameters,
                                self.params.plugin_op_property_map,
                                self.params.header,
                            )
                            x_lookup_tracing.extend(tracing)
                    elif items.get("properties"):
                        item_properties = items.get("properties", {})
                        for item_property in item_properties:
                            item_obj = item_properties.get(item_property)
                            path = item_obj.get("x-lookup", {}).get("path")
                            method = item_obj.get("x-lookup", {}).get("method")
                            lookup_parameter = item_obj.get("x-lookup", {}).get(
                                "parameter"
                            )
                            lookup_additional_parameters = item_obj.get(
                                "x-lookup", {}
                            ).get("additional_parameters")

                            if item_obj and lookup_parameter:
                                response_json, tracing = process_x_dep_array(
                                    response_json,
                                    self.params.response_obj_200.get("server"),
                                    path,
                                    method,
                                    lookup_parameter,
                                    lookup_additional_parameters,
                                    self.params.plugin_op_property_map,
                                    self.params.header,
                                    item_property,
                                )
                                x_lookup_tracing.extend(tracing)
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
        if status_code == 400 or status_code == 422:
            is_a_clarifying_question = True
            try:
                start_time = time.time()
                model_name = DEFAULT_MODEL_NAME
                if (
                    self.params.function_provider is not None
                    and self.params.function_provider.get_model_name() is not None
                ):
                    model_name = self.params.function_provider.get_model_name()
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
                traceback.print_exc()
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
            x_lookup_tracing=x_lookup_tracing,
            missing_params=[],
        )

    def get_missing_required_parameter(self):
        required_parameters = []
        try:
            op_property = None
            plugin_op_property_map = self.params.plugin_op_property_map
            if plugin_op_property_map:
                for p in plugin_op_property_map.keys():
                    for m in plugin_op_property_map[p].keys():
                        if p == self.params.path and m == self.params.method:
                            op_property = plugin_op_property_map[p][m]
            if op_property:
                if op_property.get("parameters"):
                    for prop in op_property.get("parameters", []):
                        if prop.get("required"):
                            obj = {
                                "name": prop.get("name"),
                                "type": prop.get("schema", {}).get("type"),
                                "format": prop.get("schema", {}).get("format"),
                                "description": prop.get("description"),
                                "title": prop.get("schema", {}).get("title"),
                            }
                            if prop.get("schema", {}).get("enum"):
                                obj["enum"] = prop.get("schema", {}).get("enum")
                            if prop.get("label"):
                                obj["label"] = prop.get("label")
                            required_parameters.append(obj)

                if op_property.get("requestBody"):
                    body_properties = (
                        op_property.get("requestBody", {})
                        .get("content", {})
                        .get("application/json", {})
                        .get("schema", {})
                        .get("properties")
                    )
                    required = (
                        op_property.get("requestBody", {})
                        .get("content", {})
                        .get("application/json", {})
                        .get("schema", {})
                        .get("required")
                    )
                    for prop in body_properties.keys():
                        pval = body_properties[prop]
                        if pval.get("required"):
                            obj = {
                                "name": prop,
                                "type": pval.get("type"),
                                "description": pval.get("description"),
                                "title": pval.get("title"),
                                "format": pval.get("format"),
                            }
                            if pval.get("label"):
                                obj["label"] = pval.get("label")
                            if pval.get("enum"):
                                obj["enum"] = pval.get("enum")
                            required_parameters.append(obj)
                        elif required and prop in required:
                            obj = {
                                "name": prop,
                                "type": pval.get("type"),
                                "description": pval.get("description"),
                                "title": pval.get("title"),
                                "format": pval.get("format"),
                            }
                            if pval.get("label"):
                                obj["label"] = pval.get("label")
                            if pval.get("enum"):
                                obj["enum"] = pval.get("enum")
                            required_parameters.append(obj)
        except Exception as e:
            logger.error(f"Error: {e}")
            logger.error(f"Error: {traceback.format_exc()}")

        qp = {}
        if self.params.query_params:
            qp = self.params.query_params
        bp = {}
        if self.params.body:
            bp = self.params.body

        combined_parameters = {**qp, **bp}

        missing_parameters = []
        for param in required_parameters:
            pn = param.get("name")
            if pn not in combined_parameters:
                missing_parameters.append(param)
            elif not combined_parameters.get(pn):
                missing_parameters.append(param)

        return missing_parameters
