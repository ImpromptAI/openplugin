import os

from dotenv import load_dotenv
from loguru import logger

from openplugin.plugins.models import Config
from openplugin.plugins.plugin import Plugin
from openplugin.plugins.plugin_runner import run_plugin_pipeline
from openplugin.plugins.port import Port, PortType

load_dotenv()


def run_prompt_on_plugin(openplugin_manifest: str, prompt: str):
    """
    Execute a plugin with custom prompt
    """
    logger.info(f"\n[INPUT_MANIFEST_FILE_LOCATION] {openplugin_manifest}")
    logger.info(f"\n[INPUT_PROMPT] {prompt}")
    if openplugin_manifest.startswith("http"):
        plugin_obj = Plugin.build_from_manifest_url(openplugin_manifest)
    else:
        plugin_obj = Plugin.build_from_manifest_file(openplugin_manifest)

    logger.info(f"\n[OPENPLUGIN_OBJ] {plugin_obj}")

    if prompt.startswith("http"):
        input = Port(data_type=PortType.HTTPURL, value=prompt)
    elif os.path.isfile(prompt):
        input = Port(data_type=PortType.FILEPATH, value=prompt)
    else:
        input = Port(data_type=PortType.TEXT, value=prompt)
    config = Config(
        provider="openai",
        openai_api_key=os.environ["OPENAI_API_KEY"],
        cohere_api_key="",
        google_palm_key="",
        aws_access_key_id="",
        aws_secret_access_key="",
        aws_region_name="",
    )
    preferred_approach = plugin_obj.preferred_approaches[0]
    run_plugin_pipeline(
        plugin=plugin_obj,
        input=input,
        outputs=plugin_obj.get_output_port_types(),
        config=config,
        preferred_approach=preferred_approach,
    )
