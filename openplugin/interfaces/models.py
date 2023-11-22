import json
from enum import Enum
from typing import Any, Dict, List, Optional, Set

import requests
import yaml
from pydantic import BaseModel, root_validator


class PluginAuth(BaseModel):
    type: Optional[str]
    authorization_type: Optional[str]
    verification_tokens: Optional[Dict]
    scope: Optional[str]
    client_url: Optional[str]
    authorization_url: Optional[str]
    authorization_content_type: Optional[str]
    token_validation_url: Optional[str]


class PluginOperation(BaseModel):
    """
    Represents the result of a plugin operation.
    """

    human_usage_examples: Optional[List[str]] = []
    plugin_signature_helpers: Optional[List[str]] = []
    plugin_cleanup_helpers: Optional[List[str]] = []


class Plugin(BaseModel):
    """
    Represents a plugin configuration.
    """

    manifest_url: str
    schema_version: Optional[str]
    name: Optional[str]
    description: Optional[str]
    openapi_doc_url: Optional[str]
    auth: Optional[PluginAuth]
    logo_url: Optional[str]
    contact_email: Optional[str]
    legal_info_url: Optional[str]
    api_endpoints: Optional[Set[str]] = None
    # first str is the path, second str is the method
    plugin_operations: Optional[Dict[str, Dict[str, PluginOperation]]] = None

    @staticmethod
    def build_from_manifest_url(manifest_url: str):
        manifest_obj = requests.get(manifest_url).json()
        values: Dict[str, Any] = {}
        for key in manifest_obj.keys():
            if key not in values.keys():
                values[key] = manifest_obj[key]
            if values.get("openapi_doc_url") is None:
                raise ValueError("Incompatible manifest.")
            openapi_doc_url = str(values.get("openapi_doc_url", ""))
            openapi_doc_json = requests.get(openapi_doc_url).json()
            if openapi_doc_json:
                server_url = openapi_doc_json.get("servers")[0].get("url")
                api_endpoints: set = set()
                paths = openapi_doc_json.get("paths")
                for key in paths:
                    api_endpoints.add(f"{server_url}{key}")
                values["api_endpoints"] = api_endpoints
            else:
                raise ValueError("Incompatible manifest.")
        return Plugin(**values)

    def get_openapi_doc_json(self):
        return requests.get(self.openapi_doc_url).json()

    def get_stuffed_openapi_doc_json(self):
        manifest_obj = requests.get(self.manifest_url).json()
        api_properties = {}
        for path in manifest_obj.get("plugin_operations", {}).keys():
            path_obj = manifest_obj.get("plugin_operations", {}).get(path, {})
            for method in path_obj.keys():
                method_obj = path_obj.get(method, {})
                plugin_signature_helpers = method_obj.get(
                    "plugin_signature_helpers", []
                )
                human_usage_examples = method_obj.get("human_usage_examples", [])
                api_properties[f"{path.lower()}_{method.lower()}"] = {
                    "plugin_signature_helpers": plugin_signature_helpers,
                    "human_usage_examples": human_usage_examples,
                }

        openapi_doc_json = requests.get(self.openapi_doc_url).json()
        for path in openapi_doc_json.get("paths", {}).keys():
            path_obj = openapi_doc_json.get("paths", {}).get(path, {})
            for method in path_obj.keys():
                method_obj = path_obj.get(method, {})
                method_obj["x-plugin-signature-helpers"] = api_properties.get(
                    f"{path.lower()}_{method.lower()}", {}
                ).get("plugin_signature_helpers", [])
                method_obj["x-human-usage-examples"] = api_properties.get(
                    f"{path.lower()}_{method.lower()}", {}
                ).get("human_usage_examples", [])

        return openapi_doc_json

    @root_validator(pre=True)
    def _set_fields(cls, values: dict) -> dict:
        """This is a validator that sets the field values based on the manifest_url"""
        manifest_url = values.get("manifest_url")
        if manifest_url:
            manifest_obj = requests.get(manifest_url).json()
            for key in manifest_obj.keys():
                if key not in values.keys():
                    values[key] = manifest_obj[key]
            if values.get("openapi_doc_url") is None:
                raise ValueError("Incompatible manifest.")
            openapi_doc_url = str(values.get("openapi_doc_url", ""))
            openapi_doc_json = requests.get(openapi_doc_url).json()
            if openapi_doc_json:
                server_url = openapi_doc_json.get("servers")[0].get("url")
                api_endpoints = []
                paths = openapi_doc_json.get("paths")
                for key in paths:
                    api_endpoints.append(f"{server_url}{key}")
                values["api_endpoints"] = api_endpoints
            else:
                raise ValueError("Incompatible manifest.")
        return values

    def has_api_endpoint(self, endpoint) -> bool:
        if self.api_endpoints and endpoint in self.api_endpoints:
            return True
        return False

    def get_manifest_dict(self):
        j = self.dict(exclude={"api_endpoints", "manifest_url", "auth"})
        j["auth"] = self.auth.dict(exclude_none=True)
        return j

    def get_manifest_json(self):
        return json.dumps(self.get_manifest_dict())

    def get_manifest_yaml(self):
        return yaml.dump(self.get_manifest_dict())

    def get_plugin_pre_prompts(self):
        pre_prompt = ""
        index = 1
        if self.plugin_operations:
            for value in self.plugin_operations.values():
                for val in value.values():
                    for helper in val.plugin_signature_helpers:
                        pre_prompt += f"{index}: {helper}\n"
                        index = index + 1
                    for example in val.human_usage_examples:
                        pre_prompt += f"{index}: {example}\n"
                        index = index + 1
        if index > 1:
            pre_prompt = f"For plugin: {self.name}:\n" + pre_prompt
        return pre_prompt.strip()

    def get_plugin_helpers(self):
        pre_prompt = ""
        if self.plugin_operations:
            for value in self.plugin_operations.values():
                for val in value.values():
                    for helper in val.plugin_signature_helpers:
                        pre_prompt += f"signature_helper= {helper}\n"
                    for example in val.human_usage_examples:
                        pre_prompt += f"human_usage_example= {example}\n"
        pre_prompt = f"For plugin: {self.name}:\n" + pre_prompt
        return pre_prompt.strip()


class PluginDetected(BaseModel):
    """
    Represents the result of a plugin operation.
    """

    plugin: Plugin
    api_called: Optional[str]
    method: Optional[str]


class PluginDetectedParams(PluginDetected):
    mapped_operation_parameters: Optional[Dict] = None


class Config(BaseModel):
    """
    Represents the API configuration for a plugin.
    """

    provider: str
    openai_api_key: Optional[str]
    cohere_api_key: Optional[str]
    google_palm_key: Optional[str]
    aws_access_key_id: Optional[str]
    aws_secret_access_key: Optional[str]
    aws_region_name: Optional[str]


class FunctionProperty(BaseModel):
    name: str
    type: str
    description: Optional[str]
    enum: Optional[List[str]]
    items: Optional[dict]
    is_required: bool = False


class API(BaseModel):
    url: str
    method: str

    def call(self, params):
        if self.method.lower() == "get":
            response = requests.request(
                self.method.upper(), self.url, params=params, headers={}
            )
        else:
            response = requests.request(
                self.method.upper(), self.url, data=params, headers={}
            )
        return response.json()


class Function(BaseModel):
    name: Optional[str]
    api: Optional[API]
    description: Optional[str]
    param_type: Optional[str]
    param_properties: Optional[List[FunctionProperty]]
    human_usage_examples: Optional[List[str]] = []
    plugin_signature_helpers: Optional[List[str]] = []

    def get_api_url(self):
        return self.api.url

    def get_api_method(self):
        return self.api.method

    def call_api(self, params):
        return self.api.call(params)

    def get_required_properties(self):
        return []
        """
        return [
            param_property.name
            for param_property in self.param_properties
            if param_property.is_required
        ]
        """

    def get_property_map(self):
        map = {}
        for param_property in self.param_properties:
            obj = {
                "type": param_property.type,
                "description": param_property.description,
            }
            if param_property.type == "array":
                obj["items"] = param_property.items
            if param_property.enum:
                obj["enum"] = param_property.enum
            map[param_property.name] = obj
        return map

    def get_openai_function_json(self):
        json = {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": self.param_type,
                "properties": self.get_property_map(),
                "required": self.get_required_properties(),
            },
        }
        return json


class Functions(BaseModel):
    functions: List[Function] = []
    plugin_map: dict = {}
    function_map: dict = {}

    def get_json(self):
        json = []
        for function in self.functions:
            json.append(function.get_openai_function_json())
        return json

    def get_plugin_from_func_name(self, function_name):
        return self.plugin_map.get(function_name)

    def get_function_from_func_name(self, function_name):
        return self.function_map.get(function_name)

    def add_from_plugin(
        self, plugin: Plugin, selected_operation: Optional[str] = None
    ):
        self.add_from_manifest(plugin.manifest_url, plugin, selected_operation)

    def add_from_manifest(
        self,
        manifest_url: str,
        plugin: Optional[Plugin],
        selected_operation: Optional[str] = None,
    ):
        manifest_obj = requests.get(manifest_url).json()
        open_api_spec_url = manifest_obj.get("openapi_doc_url")
        valid_operations = []

        selected_op_key = None
        if selected_operation and " " in selected_operation:
            selected_operation_path = selected_operation.split(" ")[1]
            selected_operation_method = selected_operation.split(" ")[0]
            selected_op_key = (
                f"{selected_operation_path}_{selected_operation_method}"
            )

        for key in manifest_obj.get("plugin_operations"):
            methods = manifest_obj.get("plugin_operations").get(key).keys()
            for method in methods:
                if selected_op_key:
                    if selected_op_key.lower() == f"{key}_{method}".lower():
                        valid_operations.append(selected_op_key)
                else:
                    valid_operations.append(key + "_" + method)

        self.add_from_openapi_spec(
            open_api_spec_url,
            plugin=plugin,
            plugin_operations_map=manifest_obj.get("plugin_operations"),
            valid_operations=valid_operations,
            header=None,
        )

    def get_prompt_signatures_prompt(self):
        prompt = ""
        index = 1
        for function in self.functions:
            for helper in function.plugin_signature_helpers:
                if not helper.endswith("."):
                    helper = f"{helper}."
                prompt += f"{helper} "
                index = index + 1
        prompt = prompt.strip()
        if len(prompt) > 0:
            prompt = "#system=( " + prompt + ") "
        return prompt.strip()

    def get_examples_prompt(self):
        prompt = ""
        index = 1
        for function in self.functions:
            for example in function.human_usage_examples:
                prompt += f"example= {example} \n"
                index = index + 1
        prompt = prompt.strip()
        if len(prompt) > 0:
            prompt = "The usage examples to predict the plugin:  " + prompt
        return prompt.strip()

    def add_from_openapi_spec(
        self,
        open_api_spec_url: str,
        plugin: Optional[Plugin],
        header: Optional[dict],
        plugin_operations_map: Optional[dict],
        valid_operations: Optional[List[str]],
    ):
        openapi_doc_json = requests.get(open_api_spec_url).json()
        if openapi_doc_json is None:
            return ValueError("Could not get OpenAPI spec from URL")
        server_url = openapi_doc_json.get("servers")[0].get("url")
        api_endpoints = []
        paths = openapi_doc_json.get("paths")
        functions = []

        for path in paths:
            api_endpoints.append(f"{server_url}{path}")
            for method in paths[path]:
                if valid_operations is not None:
                    if f"{path}_{method}" not in valid_operations:
                        continue
                details = paths[path][method]
                function_values: Dict[str, Any] = {}
                function_values["api"] = API(
                    url=f"{server_url}{path}", method=method
                )
                function_values["name"] = f"{method}{path.replace('/', '_')}"
                if details.get("summary") is None:
                    function_values["description"] = function_values["name"]
                else:
                    function_values["description"] = details.get("summary")
                function_values["param_type"] = "object"
                if method.lower() == "get":
                    g_properties = []
                    for param in details.get("parameters"):
                        properties_values = {}
                        properties_values["name"] = param.get("name")
                        type = "string"
                        if param.get("schema").get("type"):
                            type = param.get("schema").get("type")
                        properties_values["type"] = type
                        if param.get("description") is None:
                            properties_values["description"] = param.get("name")
                        else:
                            properties_values["description"] = param.get(
                                "description"
                            )
                        properties_values["is_required"] = param.get("required")
                        g_properties.append(FunctionProperty(**properties_values))
                    function_values["param_properties"] = g_properties
                elif method.lower() == "post" or method.lower() == "put":
                    p_properties = []
                    application_json_schema = (
                        details.get("requestBody")
                        .get("content")
                        .get("application/json")
                        .get("schema")
                    )
                    required_params = {}
                    if "properties" in application_json_schema:
                        params = application_json_schema.get("properties")
                        required_params = application_json_schema.get("required", {})
                    elif "$ref" in application_json_schema:
                        ref = application_json_schema.get("$ref")
                        ref = ref.replace("#/components/schemas/", "")
                        params = (
                            openapi_doc_json.get("components")
                            .get("schemas")
                            .get(ref)
                            .get("properties")
                        )
                        required_params = (
                            openapi_doc_json.get("components")
                            .get("schemas")
                            .get(ref)
                            .get("required", {})
                        )
                    for param in params:
                        properties_values_put: dict[str, Any] = {}
                        properties_values_put["name"] = param

                        type = "string"
                        if params.get(param).get("type"):
                            type = params.get(param).get("type")
                        properties_values_put["type"] = type
                        if params.get(param).get("type") == "array":
                            properties_values_put["items"] = params.get(param).get(
                                "items"
                            )
                        if params.get(param).get("description") is None:
                            properties_values_put["description"] = param
                        else:
                            properties_values_put["description"] = params.get(
                                param
                            ).get("description")
                        if param in required_params:
                            properties_values_put["is_required"] = True
                        else:
                            properties_values_put["is_required"] = False
                        p_properties.append(properties_values_put)
                    function_values["param_properties"] = p_properties

                human_usage_examples = []
                if plugin_operations_map is not None:
                    human_usage_examples = (
                        plugin_operations_map.get(path, {})
                        .get(method, {})
                        .get("human_usage_examples", [])
                    )
                function_values["human_usage_examples"] = human_usage_examples
                plugin_signature_helpers = []
                if plugin_operations_map is not None:
                    plugin_signature_helpers = (
                        plugin_operations_map.get(path, {})
                        .get(method, {})
                        .get("plugin_signature_helpers", [])
                    )
                function_values[
                    "plugin_signature_helpers"
                ] = plugin_signature_helpers
                func = Function(**function_values)
                if plugin:
                    self.plugin_map[func.name] = plugin
                self.function_map[func.name] = func
                functions.append(func)
        self.functions.extend(functions)


class LLM(BaseModel):
    """
    Represents the configuration for an LLM (Language Model) provider.
    """

    provider: str
    model_name: str
    temperature: float = 0
    max_tokens: int = 2048
    top_p: float = 1
    frequency_penalty: float = 0
    presence_penalty: float = 0
    n: int = 1
    best_of: int = 1
    max_retries: int = 6


class SelectedPluginsResponse(BaseModel):
    """
    Represents the response from executing prompts.
    """

    run_completed: bool
    final_text_response: Optional[str]
    detected_plugin_operations: Optional[List[PluginDetected]]
    response_time: Optional[float]
    tokens_used: Optional[int]
    llm_api_cost: Optional[float]


class SelectedApiSignatureResponse(BaseModel):
    """
    Represents the response from executing prompts.
    """

    run_completed: bool
    final_text_response: Optional[str]
    detected_plugin_operations: Optional[List[PluginDetectedParams]]
    response_time: Optional[float]
    tokens_used: Optional[int]
    llm_api_cost: Optional[float]


class MessageType(str, Enum):
    HumanMessage = "HumanMessage"
    AIMessage = "AIMessage"
    SystemMessage = "SystemMessage"
    FunctionMessage = "FunctionMessage"


class Message(BaseModel):
    """
    Represents a prompt to be executed.
    """

    content: str
    message_type: MessageType

    def get_openai_message(self):
        if self.message_type == MessageType.HumanMessage:
            return {"role": "user", "content": self.content}
        elif self.message_type == MessageType.AIMessage:
            return {"role": "assistant", "content": self.content}
        elif self.message_type == MessageType.SystemMessage:
            return {"role": "system", "content": self.content}


class OperationExecutionParams(BaseModel):
    config: Config
    api: str
    method: str
    query_params: Optional[dict]
    body: Optional[dict]
    header: Optional[dict]
    post_processing_cleanup_prompt: Optional[str]
    llm: Optional[LLM]
    plugin_response_template: Optional[str]
    post_call_evaluator_prompt: Optional[str]

    def get_temperature(self):
        if self.llm:
            return self.llm.temperature
        return None

    def get_top_p(self):
        if self.llm:
            return self.llm.top_p
        return None

    def get_max_tokens(self):
        if self.llm:
            return self.llm.max_tokens
        return None

    def get_frequency_penalty(self):
        if self.llm:
            return self.llm.frequency_penalty
        return None

    def get_presence_penalty(self):
        if self.llm:
            return self.llm.presence_penalty
        return None


class OperationExecutionResponse(BaseModel):
    original_response: Optional[Any]
    cleanup_response: Optional[str]
    template_response: Optional[str]
    summary_response: Optional[str]
    clarifying_response: Optional[str]
    is_a_clarifying_question: Optional[bool] = False
    api_call_status_code: Optional[str]
    api_call_response_seconds: Optional[float]
    template_execution_status_code: Optional[str]
    template_execution_response_seconds: Optional[float]
    cleanup_helper_status_code: Optional[str]
    cleanup_helper_response_seconds: Optional[float]
    summary_response_status_code: Optional[str]
    summary_response_seconds: Optional[float]
    clarifying_question_status_code: Optional[str]
    clarifying_question_response_seconds: Optional[float]
