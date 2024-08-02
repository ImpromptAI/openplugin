import asyncio
import os
import traceback
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi.responses import JSONResponse

from openplugin.core.config import Config
from openplugin.core.function_providers import FunctionProviders
from openplugin.core.plugin import PluginBuilder
from openplugin.core.plugin_execution_pipeline import (
    PluginExecutionPipeline,
    PluginExecutionPipelineError,
)
from openplugin.core.port import Port, PortType

function_providers = FunctionProviders.build()


def run_pipeline(
    openapi_doc_url: Optional[str],
    openapi_doc_obj: Optional[dict],
    prompt: str,
    header: dict,
    function_provider_name: str,
    conversation: list,
    auth_query_param: Optional[dict],
    config: Optional[Config],
    run_all_output_modules: bool,
    output_module_names: Optional[List[str]],
    selected_operations: Optional[List[str]],
    enable_ui_form_controls: bool,
    session_variables: Optional[str],
):
    start = datetime.now()
    try:
        pipeline = None
        input = Port(data_type=PortType.TEXT, value=prompt)
        if openapi_doc_obj is not None:
            plugin_obj = PluginBuilder.build_from_openapi_doc_obj(openapi_doc_obj)
        elif openapi_doc_url is not None:
            if openapi_doc_url.startswith("http"):
                plugin_obj = PluginBuilder.build_from_openapi_doc_url(
                    openapi_doc_url
                )
            else:
                plugin_obj = PluginBuilder.build_from_openapi_doc_file(
                    openapi_doc_url
                )
        else:
            return JSONResponse(
                status_code=400,
                content={
                    "message": "Either openapi_doc_url URL or openapi_doc_obj is required"
                },
            )

        if config is None:
            if "OPENAI_API_KEY" in os.environ:
                config = Config(openai_api_key=os.environ["OPENAI_API_KEY"])
            else:
                config = Config()

        pipeline = PluginExecutionPipeline(plugin=plugin_obj)

        json_data = {}
        error = None
        trace: Dict[Any, Any] = {"steps": []}
        response_obj = asyncio.run(
            pipeline.start(
                input=input,
                config=config,
                function_provider=function_providers.get_by_name(
                    function_provider_name
                ),
                header=header,
                auth_query_param=auth_query_param,
                output_module_names=output_module_names,
                run_all_output_modules=run_all_output_modules,
                conversation=conversation,
                selected_operations=selected_operations,
                enable_ui_form_controls=enable_ui_form_controls,
                session_variables=session_variables,
            )
        )
        json_data = response_obj.model_dump(
            exclude={"output_ports__type_object", "output_ports__value"}
        )
        trace = {"steps": pipeline.tracing_steps}
        end = datetime.now()
        elapsed_time = end - start
        response = {
            "metadata": {
                "start_time": start.strftime("%Y-%m-%d %H:%M:%S.%f"),
                "end_time": end.strftime("%Y-%m-%d %H:%M:%S.%f"),
                "total_time_taken_seconds": elapsed_time.total_seconds(),
                "total_time_taken_ms": elapsed_time.microseconds,
                "function_provider_name": function_provider_name,
                "output_module_names": output_module_names,
                "total_tokens_used": pipeline.total_tokens_used,
                "cost": pipeline.total_cost,
            },
            "response": json_data,
            "error": error,
            "trace": trace,
        }
        return response
    except PluginExecutionPipelineError as e:
        traceback.print_exc()
        error = {"message": e.message}
    except Exception as e:
        traceback.print_exc()
        error = {"message": f"Failed to run plugin. {e}"}

    trace = {}
    try:
        if pipeline:
            trace = {"steps": pipeline.tracing_steps}
    except Exception as e:
        print(e)

    end = datetime.now()
    elapsed_time = end - start
    response = {
        "metadata": {
            "start_time": start.strftime("%Y-%m-%d %H:%M:%S.%f"),
            "end_time": end.strftime("%Y-%m-%d %H:%M:%S.%f"),
            "total_time_taken_seconds": elapsed_time.total_seconds(),
            "total_time_taken_ms": elapsed_time.microseconds,
            "function_provider_name": function_provider_name,
            "output_module_names": output_module_names,
            "total_tokens_used": None,
            "cost": None,
        },
        "response": {},
        "error": error,
        "trace": trace,
    }
    return response
