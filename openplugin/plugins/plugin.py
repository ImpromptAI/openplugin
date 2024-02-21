import json
from typing import Dict, List, Optional, Set

import requests
import yaml
from pydantic import BaseModel, root_validator

from openplugin.plugins.flow_path import FlowPath

from .models import PreferredApproach


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
    input_modules: List[FlowPath]
    output_modules: List[FlowPath]
    auth: Optional[PluginAuth]
    logo_url: Optional[str]
    contact_email: Optional[str]
    legal_info_url: Optional[str]
    api_endpoints: Optional[Set[str]] = None
    preferred_approaches: List[PreferredApproach] = []
    # first str is the path, second str is the method
    plugin_operations: Optional[Dict[str, Dict[str, PluginOperation]]] = None

    @staticmethod
    def build_from_manifest_url(manifest_url: str):
        manifest_obj = requests.get(manifest_url).json()
        manifest_obj["manifest_url"] = manifest_url
        if manifest_obj.get("auth"):
            if (
                manifest_obj.get("auth").get("type")
                and manifest_obj.get("auth").get("type") == "none"
            ):
                manifest_obj["auth"] = None
        return Plugin(**manifest_obj)

    @staticmethod
    def build_from_manifest_file(openplugin_manifest_file: str):
        with open(openplugin_manifest_file, "r") as file:
            data = file.read()
            openplugin_manifest_json = json.loads(data)
            openplugin_manifest_json["manifest_url"] = openplugin_manifest_file
            if openplugin_manifest_json.get("auth"):
                if (
                    openplugin_manifest_json.get("auth").get("type")
                    and openplugin_manifest_json.get("auth").get("type") == "none"
                ):
                    openplugin_manifest_json["auth"] = None
            return Plugin(**openplugin_manifest_json)

    @root_validator(pre=True)
    def _set_fields(cls, values: dict) -> dict:
        """This is a validator that sets the field values based on the manifest_url"""
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
        return values

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
