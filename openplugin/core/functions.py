import json
import re
import traceback
from typing import Any, Dict, List, Optional

import jsonref
import requests
from openapi_parser import parse
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


def build_function_name(name):
    # validate for litellm character restrictions: r"^[a-zA-Z0-9_-]{1,64}$"
    pattern = re.compile("[a-zA-Z0-9_-]{1,64}")
    matches = pattern.findall(name)
    name = "".join(matches)
    return name[:64]


class FunctionProperty(BaseModel):
    name: str
    type: str
    description: Optional[str] = None
    enum: Optional[Any] = None
    items: Optional[Any] = None
    x_helpers: Optional[List[str]] = []
    is_required: bool = False
    example: Optional[Any] = None
    default: Optional[Any] = None
    format: Optional[Any] = None
    pattern: Optional[Any] = None
    minLength: Optional[Any] = None
    maxLength: Optional[Any] = None
    minimum: Optional[Any] = None
    maximum: Optional[Any] = None
    additionalProperties: Optional[Any] = None
    readOnly: Optional[Any] = None
    writeOnly: Optional[Any] = None
    x_dependent: Optional[Dict] = None


class Function(BaseModel):
    name: Optional[str]
    path: Optional[str]
    method: Optional[str]
    api: Optional[API]
    description: Optional[str]
    param_type: Optional[str]
    param_description: Optional[str] = None
    param_properties: Optional[List[FunctionProperty]] = []
    x_helpers: Optional[List[str]] = []
    x_few_shot_examples: Optional[List[Dict]] = []
    human_usage_examples: Optional[List[str]] = []
    plugin_signature_helpers: Optional[List[str]] = []
    x_dependent_parameter_map: Optional[Dict[str, str]] = {}
    response_obj_200: Optional[Dict[str, Any]] = {}

    def get_api_url(self):
        return self.api.url

    def get_path(self):
        return self.path

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
            description = ""
            if param_property.description:
                description = param_property.description

            # appending x helper to description
            for helper in param_property.x_helpers:
                if helper.strip().lower() != description.strip().lower():
                    description = f"{description}\n {helper}"

            obj = {
                "type": param_property.type,
                # "x-helpers": param_property.x_helpers,
                "description": description,
            }
            if param_property.type == "array":
                items = param_property.items
                # function json doesn't take array of items
                if isinstance(items, list) and len(items) > 0:
                    items = items[0]
                obj["items"] = items
            if param_property.enum:
                obj["enum"] = param_property.enum
            if param_property.example:
                obj["example"] = param_property.example
            if param_property.default:
                obj["default"] = param_property.default
            if param_property.format:
                obj["format"] = param_property.format
            if param_property.pattern:
                obj["pattern"] = param_property.pattern
            if param_property.minLength:
                obj["minLength"] = param_property.minLength
            if param_property.maxLength:
                obj["maxLength"] = param_property.maxLength
            if param_property.minimum:
                obj["minimum"] = param_property.minimum
            if param_property.x_dependent:
                obj["x_dependent"] = param_property.x_dependent
            if param_property.maximum:
                obj["maximum"] = param_property.maximum
            if param_property.additionalProperties:
                obj["additionalProperties"] = param_property.additionalProperties
            if param_property.readOnly:
                obj["readOnly"] = param_property.readOnly
            if param_property.writeOnly:
                obj["writeOnly"] = param_property.writeOnly
            map[param_property.name] = obj
        return map

    def get_openai_function_json(self):
        # validate for litellm character restrictions: r"^[a-zA-Z0-9_-]{1,64}$"
        validated_name = build_function_name(self.name)
        description = ""
        if self.description:
            description = self.description

        # appending x helper to description
        for helper in self.x_helpers:
            if helper.strip().lower() != description.strip().lower():
                description = f"{description}\n {helper}"

        json = {
            "name": validated_name,
            "description": description,
            # "x-helpers": self.x_helpers,
            "parameters": {
                "type": self.param_type,
                "properties": self.get_property_map(),
                "required": self.get_required_properties(),
            },
        }
        if self.param_description:
            json["parameters"]["description"] = self.param_description
        return json

    def get_expanded_json(self):
        validated_name = build_function_name(self.name)
        description = ""
        if self.description:
            description = self.description

        # appending x helper to description
        for helper in self.x_helpers:
            if helper.strip().lower() != description.strip().lower():
                description = f"{description}\n {helper}"

        json = {
            "name": validated_name,
            "description": description,
            "path": self.path,
            "method": self.method,
            "x-helpers": self.x_helpers,
            "parameters": {
                "type": self.param_type,
                "properties": self.get_property_map(),
                "required": self.get_required_properties(),
            },
        }
        if self.param_description:
            json["parameters"]["description"] = self.param_description
        return json


class Functions(BaseModel):
    functions: List[Function] = []
    helpers: dict = {}
    plugin_map: dict = {}
    function_map: dict = {}

    # adhere to function calling format
    def get_json(self):
        json = []
        for function in self.functions:
            json.append(function.get_openai_function_json())
        return json

    def get_expanded_json(self):
        json = []
        for function in self.functions:
            json.append(function.get_expanded_json())
        return json

    def get_litellm_json(self):
        json = []
        for function in self.functions:
            json.append(
                {"type": "function", "function": function.get_openai_function_json()}
            )
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
        manifest_url: Optional[str],
        plugin: Optional[Plugin],
        selected_operation: Optional[str] = None,
    ):
        if manifest_url:
            if manifest_url.startswith("http"):
                manifest_obj = requests.get(manifest_url).json()
            else:
                with open(manifest_url, "r") as file:
                    data = file.read()
                    manifest_obj = json.loads(data)
        elif plugin and plugin.manifest_object:
            manifest_obj = plugin.manifest_object
        else:
            raise ValueError(
                "Manifest URL or Plugin object with manifest object is required"
            )

        open_api_spec_url = manifest_obj.get("openapi_doc_url")
        valid_operations = []

        selected_op_key = None
        if selected_operation and "_" in selected_operation:
            selected_operation_path = selected_operation.split("<PATH>")[1]
            selected_operation_method = selected_operation.split("<PATH>")[0]
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
            prompt = "#SYSTEM=( " + prompt + ") "
        return prompt.strip()

    def get_x_helpers(self):
        prompt = "#SYSTEM=( "
        for key, value in self.helpers.items():
            prompt += f"{key}, helpers={value} "
        prompt += ") "
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
        plugin: Optional[Plugin] = None,
        header: Optional[dict] = None,
        plugin_operations_map: Optional[dict] = None,
        valid_operations: Optional[List[str]] = None,
    ):
        """
        try:
            functions = self._add_from_openapi_spec_using_parser(
                open_api_spec_url,
                plugin,
                header,
                plugin_operations_map,
                valid_operations,
            )
            self.functions.extend(functions)
            return
        except Exception as e:
            print(f"Failed to parse OPENAPI spec using parser: {e}")
        """
        try:
            functions = self._add_from_openapi_spec_custom(
                open_api_spec_url,
                plugin,
                header,
                plugin_operations_map,
                valid_operations,
            )
            self.functions.extend(functions)
        except Exception as e:
            traceback.print_exc()
            print(f"Failed to parse OPENAPI spec custom: {e}")
            raise Exception(f"[OPENAI_PARSE_ERROR] {e}")

    def _add_from_openapi_spec_custom(
        self,
        open_api_spec_url: str,
        plugin: Optional[Plugin],
        header: Optional[dict],
        plugin_operations_map: Optional[dict],
        valid_operations: Optional[List[str]],
    ):
        functions = []
        openapi_doc_json = requests.get(open_api_spec_url).json()
        openapi_doc_json = to_plain_dict(
            jsonref.JsonRef.replace_refs(openapi_doc_json)
        )
        if openapi_doc_json is None:
            raise ValueError("Could not fetch OpenAPI json from URL")

        servers = openapi_doc_json.get("servers")

        if isinstance(servers, dict) and servers.get("url"):
            server_url = servers.get("url", "")
        else:
            if servers is None or len(servers) == 0:
                raise ValueError("No server found in OpenAPI json")
            server_url = servers[0].get("url")

        paths = openapi_doc_json.get("paths")
        if paths is None:
            raise ValueError("No paths found in OpenAPI json")

        reference_map = self._build_reference_map(openapi_doc_json)

        for path in paths:
            for method in paths[path]:
                if method.lower() not in [
                    "get",
                    "post",
                    "put",
                    "delete",
                    "patch",
                    "head",
                    "options",
                    "x-amazon-apigateway-any-method",
                ]:
                    continue
                if valid_operations is not None:
                    if f"{path}_{method}" not in valid_operations:
                        continue
                # print("\n\n=-=-=-=-=-=-=-=-=-==-=-=-=-=-=-=-=-=-=")
                # print(f"RUNNING FOR: path={path}, method={method}")
                # print("=-=-=-=-=-=-=-=-=-==-=-=-=-=-=-=-=-=-=")
                operation_obj = paths[path][method]
                function_values = self._parse_openapi_operation(
                    operation_obj, server_url, path, method, reference_map
                )

                # add human usage examples
                human_usage_examples = []
                if plugin_operations_map is not None:
                    human_usage_examples = (
                        plugin_operations_map.get(path, {})
                        .get(method, {})
                        .get("human_usage_examples", [])
                    )
                function_values["human_usage_examples"] = human_usage_examples

                # add plugin signature helpers
                plugin_signature_helpers = []
                if plugin_operations_map is not None:
                    plugin_signature_helpers = (
                        plugin_operations_map.get(path, {})
                        .get(method, {})
                        .get("plugin_signature_helpers", [])
                    )
                function_values["plugin_signature_helpers"] = (
                    plugin_signature_helpers
                )
                function_values["path"] = path
                function_values["method"] = method
                response_obj_200 = (
                    operation_obj.get("responses", {})
                    .get("200", {})
                    .get("content", {})
                    .get("application/json")
                )
                if response_obj_200:
                    response_obj_200["server"] = server_url
                function_values["response_obj_200"] = response_obj_200

                function_values["x_few_shot_examples"] = operation_obj.get(
                    "x-few-shot-examples", []
                )
                func = Function(**function_values)
                if plugin:
                    self.plugin_map[func.name] = plugin
                self.function_map[func.name] = func

                functions.append(func)
        return functions

    def _build_reference_map(self, openapi_doc_json: dict):
        ref_map: Dict[str, Any] = {}
        components = openapi_doc_json.get("components", {})
        for key in components.keys():
            for obj in components[key].keys():
                path = "#/components/{}/{}".format(key, obj)
                ref_map[path] = components[key][obj]
        return ref_map

    def _parse_param_obj(self, param_obj: dict):
        # print("<<BEFORE_PARSED_PARAM>> ", param_obj)
        op_property: dict = {}
        if param_obj.get("$ref"):
            raise Exception(f"Reference not found: {param_obj.get('$ref')}")

        op_property["name"] = str(param_obj.get("name"))
        type = "string"
        if param_obj.get("type"):
            type = str(param_obj.get("type"))
        elif param_obj.get("schema", {}).get("type"):
            type = param_obj.get("schema", {}).get("type")

        if type == "array":
            op_property["items"] = param_obj.get("items", [])
        op_property["type"] = type

        if param_obj.get("schema", {}).get("items"):
            op_property["items"] = param_obj.get("schema", {}).get("items")

        description = ""
        param_description = param_obj.get("description")
        if param_description:
            description += f"{param_description}\n"
        for helper in param_obj.get("x-helpers", []):
            if (
                param_description
                and helper.strip().lower() == param_description.strip().lower()
            ):
                continue
            description += f"{helper}\n"
        op_property["description"] = description
        if param_obj.get("required") is True:
            op_property["is_required"] = True
        else:
            op_property["is_required"] = False

        if param_obj.get("enum") is not None:
            op_property["enum"] = param_obj.get("enum")

        if param_obj.get("example"):
            op_property["example"] = str(param_obj.get("example"))

        if param_obj.get("default"):
            op_property["default"] = param_obj.get("default")

        if param_obj.get("format"):
            op_property["format"] = param_obj.get("format")

        if param_obj.get("pattern"):
            op_property["pattern"] = param_obj.get("pattern")

        if param_obj.get("minLength"):
            op_property["minLength"] = param_obj.get("minLength")

        if param_obj.get("maxLength"):
            op_property["maxLength"] = param_obj.get("maxLength")

        if param_obj.get("minimum"):
            op_property["minimum"] = param_obj.get("minimum")

        if param_obj.get("x-dependent"):
            op_property["x_dependent"] = param_obj.get("x-dependent")

        if param_obj.get("maximum"):
            op_property["maximum"] = param_obj.get("maximum")

        if param_obj.get("maximum"):
            op_property["maximum"] = param_obj.get("maximum")

        if param_obj.get("additionalProperties"):
            op_property["additionalProperties"] = param_obj.get(
                "additionalProperties"
            )

        if param_obj.get("readOnly"):
            op_property["readOnly"] = param_obj.get("readOnly")

        if param_obj.get("writeOnly"):
            op_property["writeOnly"] = param_obj.get("writeOnly")

        # print("<<AFTER_PARSED_PARAM>> ", op_property)
        return op_property

    def _parse_openapi_operation(
        self,
        operation_obj: dict,
        server_url: str,
        path: str,
        method: str,
        reference_map: dict,
    ):

        # print(json.dumps(operation_obj, indent=2))
        function_values: Dict[str, Any] = {}
        if server_url.endswith("/") and path.startswith("/"):
            u = f"{server_url}{path[1:]}"
        else:
            u = f"{server_url}{path}"

        function_values["api"] = API(url=u, method=method)

        validated_name = build_function_name(f"{method}{path.replace('/', '_')}")

        function_values["name"] = validated_name

        path_description = operation_obj.get("description")
        path_summary = operation_obj.get("summary")
        function_description = ""
        if path_description:
            function_description += f"{path_description}\n"
        if path_summary:
            function_description += f"{path_summary}\n"
        for helper in operation_obj.get("x-helpers", []):
            if (
                path_description
                and helper.strip().lower() == path_description.strip().lower()
            ):
                continue
            if (
                path_summary
                and helper.strip().lower() == path_summary.strip().lower()
            ):
                continue
            function_description += f"{helper}\n"
        function_values["description"] = function_description
        function_values["param_type"] = "object"
        op_properties = []
        param_description = None
        # parse parameter object
        if operation_obj.get("parameters"):
            for param in operation_obj.get("parameters", []):
                op_property = self._parse_param_obj(param)
                op_properties.append(FunctionProperty(**op_property))

        # parse request object
        if operation_obj.get("requestBody"):
            param_description = operation_obj.get("requestBody", {}).get(
                "description"
            )
            content = operation_obj.get("requestBody", {}).get("content")
            if content is None:
                if "$ref" in operation_obj.get("requestBody", {}):
                    content = reference_map.get(
                        operation_obj.get("requestBody", {}).get("$ref"), {}
                    ).get("content")
                if content is None:
                    raise Exception("Request body content not found")

            if "application/json" in content:
                body_content = content.get("application/json").get("schema")
            elif "application/xml" in content:
                body_content = content.get("application/xml").get("schema")
            elif "multipart/form-data" in content:
                body_content = content.get("multipart/form-data").get("schema")
            elif "application/x-www-form-urlencoded" in content:
                body_content = content.get("application/x-www-form-urlencoded").get(
                    "schema"
                )
            elif "application/octet-stream" in content:
                body_content = content.get("application/octet-stream").get("schema")
            else:
                raise Exception(f"Request body content type not found: {content}")

            params: List[Dict] = []
            # required_params = {}
            if "properties" in body_content:
                param_properties = body_content.get("properties")
                if isinstance(param_properties, dict):
                    params = []
                    for key in param_properties.keys():
                        param_properties[key]["name"] = key
                        params.append(param_properties[key])
                else:
                    params = param_properties
                # required_params = body_content.get("required", {})
            elif "$ref" in body_content:
                if body_content.get("$ref") not in reference_map:
                    raise Exception(
                        f"Reference not found: {body_content.get('$ref')}"
                    )
                ref_obj = reference_map.get(body_content.get("$ref"), {})
                params = []
                if "properties" in ref_obj:
                    param_properties = ref_obj.get("properties")
                    if isinstance(param_properties, dict):
                        params = []
                        for key in param_properties.keys():
                            param_properties[key]["name"] = key
                            params.append(param_properties[key])
                    else:
                        params = param_properties
                # required_params = params.get("required", {})
            elif "allOf" in body_content:
                allOf = body_content.get("allOf")
                for obj in allOf:
                    if "properties" in obj:
                        p_props = obj.get("properties")
                        if isinstance(p_props, dict):
                            params = []
                            for key in p_props.keys():
                                p_props[key]["name"] = key
                                params.append(p_props[key])
                        elif isinstance(p_props, list):
                            params.extend(obj.get("properties", []))
                        # required_params = obj.get("required", {})
            for param in params:
                op_property = self._parse_param_obj(param)
                op_properties.append(FunctionProperty(**op_property))

        function_values["param_description"] = param_description
        function_values["param_properties"] = op_properties
        return function_values

    def _add_from_openapi_spec_using_parser(
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
        paths = openapi_doc_json.get("paths")

        functions = []
        content = parse(open_api_spec_url)
        for content_path in content.paths:
            for content_operation in content_path.operations:
                path = content_path.url
                method = content_operation.method.value
                if valid_operations is not None:
                    if f"{path}_{method}" not in valid_operations:
                        continue
                details = paths[path][method]
                function_values: Dict[str, Any] = {}

                if server_url.endswith("/") and path.startswith("/"):
                    u = f"{server_url}{path[1:]}"
                else:
                    u = f"{server_url}{path}"

                function_values["api"] = API(url=u, method=method)
                validated_name = build_function_name(
                    f"{method}{path.replace('/', '_')}"
                )
                function_values["name"] = validated_name
                if details.get("summary") is None:
                    function_values["description"] = function_values["name"]
                else:
                    function_values["description"] = details.get("summary")
                function_values["param_type"] = "object"
                if method.lower() == "get":
                    g_properties = []
                    # for param in details.get("parameters"):
                    for parameter in content_operation.parameters:

                        properties_values: Dict = {}
                        properties_values["name"] = parameter.name
                        properties_values["type"] = parameter.schema.type.value
                        if parameter.description:
                            properties_values["description"] = parameter.description
                        if parameter.required:
                            properties_values["is_required"] = "True"
                        else:
                            properties_values["is_required"] = "False"
                        if parameter.extensions:
                            helpers = parameter.extensions.get("helpers", [])
                            properties_values["x_helpers"] = helpers
                            key = f"For path={path}, method={method}, parameter={parameter.name}"
                            self.helpers[key] = helpers
                        g_properties.append(FunctionProperty(**properties_values))
                    function_values["param_properties"] = g_properties
                elif method.lower() == "post" or method.lower() == "put":
                    p_properties = []
                    application_json_schema = (
                        details.get("requestBody", {})
                        .get("content", {})
                        .get("application/json", {})
                        .get("schema", {})
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
                function_values["plugin_signature_helpers"] = (
                    plugin_signature_helpers
                )

                if content_operation.extensions:
                    helpers = content_operation.extensions.get("helpers", [])
                    key = f"For path={path}, method={method}"
                    self.helpers[key] = helpers
                    function_values["x_helpers"] = helpers
                else:
                    function_values["x_helpers"] = []
                function_values["path"] = path
                function_values["method"] = method
                if plugin_operations_map is not None:
                    function_values["x_few_shot_examples"] = (
                        plugin_operations_map.get(path, {})
                        .get(method, {})
                        .get("plugin_signature_helpers", [])
                    )
                func = Function(**function_values)
                if plugin:
                    self.plugin_map[func.name] = plugin
                self.function_map[func.name] = func
                functions.append(func)
        return functions


def to_plain_dict(data):
    if isinstance(data, dict):
        return {key: to_plain_dict(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [to_plain_dict(item) for item in data]
    else:
        return data
