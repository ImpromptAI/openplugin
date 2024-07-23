import json
from typing import Dict, List, Optional, Set

import jsonref
import requests
import yaml
from pydantic import AnyHttpUrl, BaseModel, Field, ValidationError

from .flow_path import FlowPath


class PluginAuth(BaseModel):
    type: Optional[str] = None
    authorization_type: Optional[str] = None
    verification_tokens: Optional[Dict] = None
    scope: Optional[str] = None
    client_url: Optional[str] = None
    authorization_url: Optional[str] = None
    authorization_content_type: Optional[str] = None
    token_validation_url: Optional[str] = None


class PluginOperation(BaseModel):
    """
    Represents the result of a plugin operation.
    """

    human_usage_examples: List[str] = Field(default=[])
    plugin_signature_helpers: List[str] = Field(default=[])
    output_modules: List[FlowPath] = Field(default=[])
    filter: Optional[FlowPath] = Field(default=None)


class Plugin(BaseModel):
    """
    Represents a plugin configuration.
    """

    schema_version: str
    openapi_doc_obj: Dict
    name: str
    contact_email: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    legal_info_url: Optional[str] = None
    permutate_doc_url: Optional[AnyHttpUrl] = None
    permutation_test_url: Optional[AnyHttpUrl] = None
    auth: Optional[PluginAuth] = None
    input_modules: Optional[List[FlowPath]] = []
    output_modules: Optional[List[FlowPath]] = []

    api_endpoints: Optional[Set[str]] = None
    # first str is the path, second str is the method
    plugin_operations: Optional[Dict[str, Dict[str, PluginOperation]]] = None
    plugin_op_property_map: Optional[Dict[str, Dict[str, Dict]]] = None

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

    def get_output_port_types(self):
        return [output.get_output_port_type() for output in self.output_modules]

    def get_supported_output_modules(self, operation: str, method: str):
        supported_output_modules = []
        if self.output_modules:
            supported_output_modules.extend(self.output_modules)
        if self.plugin_operations:
            for key1 in self.plugin_operations.keys():
                if key1.lower() == operation.lower() or operation.lower().endswith(
                    key1.lower()
                ):
                    for key2 in self.plugin_operations[key1].keys():
                        if key2.lower() == method.lower():
                            if self.plugin_operations[key1][key2].output_modules:
                                supported_output_modules.extend(
                                    self.plugin_operations[key1][key2].output_modules
                                )
        return supported_output_modules

    def get_filter_module(self, operation: str, method: str):
        if self.plugin_operations:
            for key1 in self.plugin_operations.keys():
                if key1.lower() == operation.lower() or operation.lower().endswith(
                    key1.lower()
                ):
                    for key2 in self.plugin_operations[key1].keys():
                        if key2.lower() == method.lower():
                            if self.plugin_operations[key1][key2].filter:
                                return self.plugin_operations[key1][key2].filter
        return None


class PluginBuilder:
    @staticmethod
    def build_from_openapi_doc_url(openapi_doc_url: str):
        openapi_doc_obj = requests.get(openapi_doc_url).json()
        return PluginBuilder.build_from_openapi_doc_obj(openapi_doc_obj)

    @staticmethod
    def build_from_openapi_doc_file(openapi_doc_file: str):
        with open(openapi_doc_file, "r") as file:
            data = file.read()
            openapi_doc_json = json.loads(data)
            return PluginBuilder.build_from_openapi_doc_obj(openapi_doc_json)

    @staticmethod
    def build_from_openapi_doc_obj(openapi_doc_obj: dict):
        if openapi_doc_obj and openapi_doc_obj.get("x-plugin-auth"):
            if (
                openapi_doc_obj.get("x-plugin-auth", {}).get("type")
                and openapi_doc_obj.get("x-plugin-auth", {}).get("type") == "none"
            ):
                openapi_doc_obj["x-plugin-auth"] = None
        try:
            x_openplugin = openapi_doc_obj.get("x-openplugin")
            if x_openplugin is None:
                raise Exception("Invalid openapi_doc. x-openplugin is missing.")

            # directly accessing the values from the openapi doc object
            schema_version = x_openplugin.get("schemaVersion")
            name = x_openplugin.get("name")
            description = x_openplugin.get("description")
            contact_email = x_openplugin.get("contactEmail")
            logo_url = x_openplugin.get("logoUrl")
            legal_info_url = x_openplugin.get("legalInfoUrl")
            permutate_doc_url = x_openplugin.get("permutateDocUrl")
            permutation_test_url = x_openplugin.get("permutationTestUrl")

            auth = openapi_doc_obj.get("x-plugin-auth")
            input_modules = openapi_doc_obj.get("x-input-modules", [])
            output_modules = openapi_doc_obj.get("x-output-modules", [])

            plugin_operations: Dict[str, Dict[str, PluginOperation]] = {}
            for path, path_obj in openapi_doc_obj.get("paths", {}).items():
                method_props = {}
                for method, method_obj in path_obj.items():
                    method_props[method] = PluginOperation(
                        human_usage_examples=method_obj.get(
                            "x-human-usage-examples", []
                        ),
                        plugin_signature_helpers=method_obj.get(
                            "x-plugin-signature-helpers", []
                        ),
                        output_modules=method_obj.get("x-output-modules", []),
                        filter=method_obj.get("x-filter"),
                    )
                plugin_operations[path] = method_props

            api_endpoints: set = set()
            server_url = openapi_doc_obj.get("servers", [])[0].get("url")
            for key in openapi_doc_obj.get("paths", {}).keys():
                api_endpoints.add(f"{server_url}{key}")

            plugin_op_property_map: Dict[str, Dict[str, Dict]] = {}
            if openapi_doc_obj:
                openapi_doc_json = to_plain_dict(
                    jsonref.JsonRef.replace_refs(openapi_doc_obj)
                )
                for path in openapi_doc_json.get("paths", {}).keys():
                    path_obj = openapi_doc_json.get("paths", {}).get(path, {})
                    method_properties: Dict[str, Dict] = {}
                    for method in path_obj.keys():
                        method_obj = path_obj.get(method, {})
                        method_props[method] = method_obj
                    plugin_op_property_map[path] = method_properties

            plugin = Plugin(
                schema_version=schema_version,
                name=name,
                contact_email=contact_email,
                description=description,
                openapi_doc_obj=openapi_doc_obj,
                logo_url=logo_url,
                legal_info_url=legal_info_url,
                permutate_doc_url=permutate_doc_url,
                permutation_test_url=permutation_test_url,
                auth=auth,
                input_modules=input_modules,
                output_modules=output_modules,
                api_endpoints=api_endpoints,
                plugin_operations=plugin_operations,
                plugin_op_property_map=plugin_op_property_map,
            )
        except ValidationError as e:
            print(e.errors())
            raise Exception(f"Invalid openplugin openapi doc. {str(e)}")
        return plugin


def to_plain_dict(data):
    if isinstance(data, dict):
        return {key: to_plain_dict(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [to_plain_dict(item) for item in data]
    else:
        return data
