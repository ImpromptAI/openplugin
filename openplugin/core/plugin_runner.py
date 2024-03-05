import os
import sys
from typing import List, Optional

from dotenv import load_dotenv
from loguru import logger

from .helper import time_taken
from .llms import Config
from .plugin import PluginBuilder, PreferredApproach
from .plugin_execution_pipeline import PluginExecutionPipeline
from .port import Port, PortType, PortMetadata

load_dotenv()


@time_taken
async def run_prompt_on_plugin(
    openplugin_manifest: str,
    prompt: str,
    config: Optional[Config] = None,
    output_port_types: Optional[List[PortType]] = None,
    preferred_approach: Optional[PreferredApproach] = None,
    log_level: Optional[str] = "INFO",
) -> Optional[Port]:
    """
    Execute a plugin with custom prompt
    """

    logger.remove()
    try:
        logger.level("FLOW", no=38, color="<yellow>", icon="🚀")
    except Exception as e:
        print(e)
    if log_level:
        logger.add(sys.stderr, level=log_level.upper())

    logger.info(f"\n[INPUT_MANIFEST_FILE_LOCATION] {openplugin_manifest}")
    logger.info(f"\n[INPUT_PROMPT] {prompt}")
    logger.log("FLOW", "[PLUGIN-PIPELINE-STARTED]")
    if openplugin_manifest.startswith("http"):
        plugin_obj = PluginBuilder.build_from_manifest_url(openplugin_manifest)
    else:
        plugin_obj = PluginBuilder.build_from_manifest_file(openplugin_manifest)

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
    pipeline = PluginExecutionPipeline(plugin=plugin_obj)
    execution_response = await pipeline.start(
        input=input,
        config=config,
        header={},
        auth_query_param=None,
        preferred_approach=preferred_approach,
        output_module_names=[],
    )
    for key, value in execution_response.output_module_map.items():
        if value.get_metadata(PortMetadata.DEFAULT_OUTPUT_MODULE):
            return value
    return None
