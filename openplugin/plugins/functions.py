import json
from typing import Any, Dict, List, Optional

import requests
from pydantic import BaseModel

from .plugin import Plugin


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


class FunctionProperty(BaseModel):
    name: str
    type: str
    description: Optional[str] = None
    enum: Optional[List[str]] = None
    items: Optional[dict] = None
    is_required: bool = False


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

    def add_from_plugin(self, plugin: Plugin, selected_operation: Optional[str] = None):
        self.add_from_manifest(plugin.manifest_url, plugin, selected_operation)

    def add_from_manifest(
        self,
        manifest_url: str,
        plugin: Optional[Plugin],
        selected_operation: Optional[str] = None,
    ):
        if manifest_url.startswith("http"):
            manifest_obj = requests.get(manifest_url).json()
        else:
            with open(manifest_url, "r") as file:
                data = file.read()
                manifest_obj = json.loads(data)
        open_api_spec_url = manifest_obj.get("openapi_doc_url")
        valid_operations = []

        selected_op_key = None
        if selected_operation and " " in selected_operation:
            selected_operation_path = selected_operation.split(" ")[1]
            selected_operation_method = selected_operation.split(" ")[0]
            selected_op_key = f"{selected_operation_path}_{selected_operation_method}"

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
                function_values["api"] = API(url=f"{server_url}{path}", method=method)
                function_values["name"] = f"{method}{path.replace('/', '_')}"
                if details.get("summary") is None:
                    function_values["description"] = function_values["name"]
                else:
                    function_values["description"] = details.get("summary")
                function_values["param_type"] = "object"
                if method.lower() == "get":
                    g_properties = []
                    for param in details.get("parameters"):
                        if param.get("$ref"):
                            ref = param.get("$ref")
                            ref = ref.replace("#/components/parameters/", "")
                            param = (
                                openapi_doc_json.get("components")
                                .get("parameters")
                                .get(ref)
                            )
                        properties_values = {}
                        properties_values["name"] = param.get("name")
                        type = "string"
                        if param.get("schema").get("type"):
                            type = param.get("schema").get("type")
                        properties_values["type"] = type
                        if param.get("description") is None:
                            properties_values["description"] = param.get("name")
                        else:
                            properties_values["description"] = param.get("description")
                        properties_values["is_required"] = param.get("required", False)
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
                function_values["plugin_signature_helpers"] = plugin_signature_helpers
                func = Function(**function_values)
                if plugin:
                    self.plugin_map[func.name] = plugin
                self.function_map[func.name] = func
                functions.append(func)
        self.functions.extend(functions)
