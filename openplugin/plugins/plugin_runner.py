import os
import sys
from typing import List, Optional

from dotenv import load_dotenv
from loguru import logger

from . import time_taken
from .models import Config, PreferredApproach
from .plugin import Plugin
from .plugin_pipeline import PluginPipeline
from .port import Port, PortType

load_dotenv()


@time_taken
async def run_prompt_on_plugin(
    openplugin_manifest: str,
    prompt: str,
    config: Optional[Config] = None,
    output_port_types: Optional[List[PortType]] = None,
    preferred_approach: Optional[PreferredApproach] = None,
    log_level: Optional[str] = "INFO",
) -> List[Port]:
    """
    Execute a plugin with custom prompt
    """

    logger.remove()
    logger.level("FLOW", no=38, color="<yellow>", icon="🚀")
    if log_level:
        logger.add(sys.stderr, level=log_level.upper())

    logger.info(f"\n[INPUT_MANIFEST_FILE_LOCATION] {openplugin_manifest}")
    logger.info(f"\n[INPUT_PROMPT] {prompt}")
    logger.log("FLOW", "[PLUGIN-PIPELINE-STARTED]")
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

    if config is None:
        config = Config(openai_api_key=os.environ["OPENAI_API_KEY"])
    if preferred_approach is None:
        preferred_approach = plugin_obj.preferred_approaches[0]

    if output_port_types is None:
        output_port_types = plugin_obj.get_output_port_types()

    pipeline = PluginPipeline(plugin=plugin_obj)
    output_ports = await pipeline.start(
        input=input,
        outputs=output_port_types,
        config=config,
        preferred_approach=preferred_approach,
    )
    return output_ports
