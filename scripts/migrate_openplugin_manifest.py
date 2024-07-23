import json

import requests


def start(openplugin_manifest_url):
    openplugin_manifest_json = requests.get(openplugin_manifest_url).json()
    openapi_doc_url = openplugin_manifest_json["openapi_doc_url"]
    openapi_doc_json = requests.get(openapi_doc_url).json()

    openapi_doc_json["x-openplugin"] = {
        "schemaVersion": "0.0.1",
        "name": openplugin_manifest_json["name"],
        "description": openplugin_manifest_json["description"],
        "contactEmail": openplugin_manifest_json["contact_email"],
        "logoUrl": openplugin_manifest_json["logo_url"],
        "legalInfoUrl": openplugin_manifest_json["legal_info_url"],
        "permutateDocUrl": openplugin_manifest_json["permutate_doc_url"],
    }
    openapi_doc_json["x-plugin-auth"] = openplugin_manifest_json["auth"]

    plugin_operation_map = {}

    if openplugin_manifest_json.get("plugin_selector_helpers"):
        openapi_doc_json["x-plugin-selector-helpers"] = openplugin_manifest_json[
            "plugin_selector_helpers"
        ]
    for operation, operation_obj in openplugin_manifest_json[
        "plugin_operations"
    ].items():
        for method, method_obj in operation_obj.items():
            key = f"{operation}_{method}"
            plugin_operation_map[key] = method_obj

    for operation, operation_obj in openapi_doc_json["paths"].items():
        for method, method_obj in operation_obj.items():
            key = f"{operation}_{method}"
            op_obj = plugin_operation_map.get(key)
            if "output_modules" in op_obj:
                method_obj["x-output-modules"] = op_obj["output_modules"]
            if "human_usage_examples" in op_obj:
                method_obj["x-human-usage-examples"] = op_obj["human_usage_examples"]
            if "filter" in op_obj:
                if (
                    method_obj.get("responses") is not None
                    and method_obj["responses"].get("200") is not None
                ):
                    method_obj["responses"]["200"]["x-filter"] = op_obj["filter"]

    # print(json.dumps(plugin_operation_map, indent=4))
    print(json.dumps(openapi_doc_json, indent=4))


openplugin_manifest_url = "https://openplugin.s3.amazonaws.com/cb63497cbc0544c3a9a3eceac9daee99/manifest/b/Shopping,_Klarna.json"
start(openplugin_manifest_url)
