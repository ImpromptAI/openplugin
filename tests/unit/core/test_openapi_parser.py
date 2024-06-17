import json

import pytest
from loguru import logger

from openplugin.core.functions import Functions

test_file_path = "tests/resources/test_plugins_beta.json"


def load_json_params():
    with open(test_file_path, "r") as f:
        data = json.load(f)
    values = []
    for item in data:
        values.append((item["openapi_doc_url"], item["openapi_function_count"]))
    return values


@pytest.fixture(scope="module")
def json_params():
    return load_json_params()


@pytest.mark.parametrize(
    "openapi_doc_url,openapi_function_count",
    load_json_params(),
)
def test_openapi_parsing(openapi_doc_url, openapi_function_count):
    """This method tests the openapi parsing."""
    functions = Functions()
    functions.add_from_openapi_spec(open_api_spec_url=openapi_doc_url)
    function_json = functions.get_json()

    logger.info(f"\nopenapi_doc_url: {openapi_doc_url}")

    assert function_json is not None
    assert len(function_json) > 0
    assert len(function_json) == openapi_function_count
