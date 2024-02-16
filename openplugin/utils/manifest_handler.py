from typing import Any, Dict

import requests

from openplugin.plugins.plugin import Plugin, PluginOperation


# Function to retrieve OpenPlugin manifest from an OpenAI manifest URL
def get_openplugin_manifest_from_openai_manifest(
    openai_manifest_url: str,
    selected_operations: Dict[str, Dict[str, PluginOperation]] = {},
):
    # Retrieve the OpenAI manifest JSON from the provided URL
    manifest_url = openai_manifest_url
    manifest_obj = requests.get(manifest_url).json()

    schema_version = manifest_obj["schema_version"]
    if manifest_obj.get("name_for_model") is None:
        name = manifest_obj["name_for_model"]
    else:
        name = manifest_obj["name_for_human"]

    if manifest_obj.get("description_for_model") is not None:
        description = manifest_obj["description_for_model"]
    else:
        description = manifest_obj["description_for_human"]

    openapi_doc_url = manifest_obj["api"]["url"]
    auth = manifest_obj["auth"]
    logo_url = manifest_obj.get("logo_url")
    contact_email = manifest_obj.get("contact_email")
    legal_info_url = manifest_obj.get("legal_info_url")

    # Retrieve the OpenAPI documentation JSON from the OpenAPI URL
    openapi_doc_json = requests.get(openapi_doc_url).json()
    api_endpoints: set = set()
    plugin_operations: Dict[str, Any] = {}
    if openapi_doc_json:
        server_url = openapi_doc_json.get("servers")[0].get("url")
        paths = openapi_doc_json.get("paths")
        for key in paths:
            for method in paths.get(key):
                api_endpoints.add(f"{server_url}{key}")
                plugin_operations[key] = {}
                plugin_operations[key][method] = PluginOperation(
                    human_usage_examples=["hello", "world"],
                    plugin_signature_helpers=["hello", "world"],
                )
    # If selected_operations is provided, use it; otherwise, use the extracted ops
    if selected_operations and len(selected_operations) > 0:
        plugin_operations = selected_operations

    # Create a Plugin object with the extracted information
    plugin_obj = Plugin(
        manifest_url=manifest_url,
        schema_version=schema_version,
        name=name,
        description=description,
        openapi_doc_url=openapi_doc_url,
        auth=auth,
        logo_url=logo_url,
        input_modules=[],
        output_modules=[],
        contact_email=contact_email,
        legal_info_url=legal_info_url,
        api_endpoints=api_endpoints,
        plugin_operations=plugin_operations,
    )
    return plugin_obj


# Function to create an OpenPlugin manifest from OpenAPI documentation and other details
def get_openplugin_manifest_from_openapi_doc(
    openapi_doc_url: str,
    schema_version: str,
    name: str,
    description: str,
    auth: dict,
    logo_url: str,
    contact_email: str,
    legal_info_url: str,
    selected_operations: Dict[str, Dict[str, PluginOperation]],
):
    # Create a dictionary representing the OpenPlugin manifest
    manifest_obj = {
        "schema_version": schema_version,
        "name": name,
        "description": description,
        "openapi_doc_url": openapi_doc_url,
        "auth": auth,
        "logo_url": logo_url,
        "contact_email": contact_email,
        "legal_info_url": legal_info_url,
        "plugin_operations": selected_operations,
    }
    return manifest_obj
