import json
import os

import pytest
from loguru import logger

from openplugin.core.config import Config
from openplugin.core.function_providers import FunctionProviders
from openplugin.core.functions import Functions

test_file_path = "tests/resources/test_plugins_beta.json"


def load_json_params():
    with open(test_file_path, "r") as f:
        data = json.load(f)
    values = []
    for item in data:
        for example in item["examples"]:
            values.append(
                (
                    item["openplugin_manifest_url"],
                    example["example"],
                    example["method"],
                    example["path"],
                )
            )
    return values


@pytest.fixture(scope="module")
def json_params():
    return load_json_params()


@pytest.mark.parametrize(
    "openplugin_manifest_url, request_prompt, method, path",
    load_json_params(),
)
def test_function_calling_gpt4(
    openplugin_manifest_url, request_prompt, method, path
):
    """This method tests the function calling for GPT-4 plugin."""
    functions = Functions()
    functions.add_from_manifest(manifest_url=openplugin_manifest_url, plugin=None)
    function_json = functions.get_json()
    function_providers = FunctionProviders.build()
    function_provider = function_providers.get_by_name(name="OpenAI [gpt-4]")
    if path.startswith("/"):
        path = path[1:]
    expected_function_name = f"{method}_{path.replace('/', '_')}"
    config = Config(openai_api_key=os.environ["OPENAI_API_KEY"])
    func_response = function_provider.run(
        request_prompt, function_json, config, conversation=[]
    )

    logger.info(f"\nopenplugin_manifest_url: {openplugin_manifest_url}")
    logger.info(f"\nrequest_prompt: {request_prompt}")
    logger.info(f"\nmethod: {method}")
    logger.info(f"\npath: {path}")
    logger.info(f"\nexpected_function_name: {expected_function_name}")
    logger.info(f"\nextracted_function_name: {func_response}")

    assert func_response.is_function_call
    assert func_response.detected_function_name == expected_function_name
