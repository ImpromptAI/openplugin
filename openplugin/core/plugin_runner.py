import os
import sys
from typing import List, Optional

from dotenv import load_dotenv
from loguru import logger

from .config import Config
from .function_providers import FunctionProvider, FunctionProviders
from .helper import time_taken
from .plugin import PluginBuilder
from .plugin_execution_pipeline import PluginExecutionPipeline
from .port import Port, PortMetadata, PortType

load_dotenv()


@time_taken
async def run_prompt_on_plugin(
    openapi_doc_url: str,
    prompt: str,
    config: Optional[Config] = None,
    output_port_types: Optional[List[PortType]] = None,
    function_provider: Optional[FunctionProvider] = None,
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

    logger.info(f"\n[INPUT_MANIFEST_FILE_LOCATION] {openapi_doc_url}")
    logger.info(f"\n[INPUT_PROMPT] {prompt}")
    logger.log("FLOW", "[PLUGIN-PIPELINE-STARTED]")
    plugin_obj = PluginBuilder.build_from_openapi_doc_url(openapi_doc_url)
    logger.info(f"\n[OPENPLUGIN_OBJ] {plugin_obj}")

    if prompt.startswith("http"):
        input = Port(data_type=PortType.HTTPURL, value=prompt)
    elif os.path.isfile(prompt):
        input = Port(data_type=PortType.FILEPATH, value=prompt)
    else:
        input = Port(data_type=PortType.TEXT, value=prompt)

    if config is None:
        config = Config(openai_api_key=os.environ["OPENAI_API_KEY"])
    if function_provider is None:
        function_provider = FunctionProviders.build().get_default_provider()

    if output_port_types is None:
        output_port_types = plugin_obj.get_output_port_types()
    pipeline = PluginExecutionPipeline(plugin=plugin_obj)
    execution_response = await pipeline.start(
        input=input,
        config=config,
        header={},
        auth_query_param=None,
        function_provider=function_provider,
        output_module_names=[],
    )
    for key, value in execution_response.output_module_map.items():
        if value.get_metadata(PortMetadata.DEFAULT_OUTPUT_MODULE):
            return value
    return None
