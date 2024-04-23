import datetime
import os, json
import traceback
from typing import List, Optional, Dict
from fastapi import APIRouter, Body, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKey
from httpx import request
from pydantic import BaseModel
from openplugin.api import auth
from openplugin.core.llms import Config
from openplugin.core.plugin import PluginBuilder, PreferredApproach
from openplugin.core.plugin_execution_pipeline import PluginExecutionPipeline
from openplugin.core.port import MimeType, Port, PortType
from openplugin.utils.helpers import is_url

# Create a FastAPI router instance
router = APIRouter(
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

class PluginExecutionRequest(BaseModel):
    input: Optional[str] = None
    openplugin_manifest_url: Optional[str] = None
    openplugin_manifest_obj: Optional[Dict] = None
    conversation: Optional[List] = []
    preferred_approach: Optional[PreferredApproach] = None
    header: Optional[Dict] = {}
    auth_query_param: Optional[Dict] = None
    config: Optional[Config] = None
    run_all_output_modules: bool = False
    output_module_names: Optional[List[str]] = None

    

# Define a POST endpoint for plugin-pipeline API
@router.post("/plugin-execution-pipeline")
async def plugin_execution_pipeline(
    input_metadata:str=Form(...),
    file: Optional[UploadFile] = None,
    api_key: APIKey = Depends(auth.get_api_key)
) -> JSONResponse:
    try:
        request_obj=PluginExecutionRequest(**json.loads(input_metadata))
        if file:
            print(file.filename)
        start = datetime.datetime.now()
        input = request_obj.input
        if input is None and file is None:
            return JSONResponse(
                status_code=400, content={"message": "Either input or file is required"}
            )
        if input:
            if is_url(input):
                robj = request("GET", input)
                content_type=robj.headers.get("content-type")
                if  content_type.startswith("text") or content_type.startswith("image") or content_type.startswith("video") or content_type.startswith("audio"):
                    mime_type=MimeType(robj.headers.get("content-type"))
                    input_port = Port(data_type=PortType.FILE, mime_types=[mime_type], value=input)
                else:
                    input_port = Port(data_type=PortType.REMOTE_FILE_URL, value=input)
            else:
                input_port = Port(data_type=PortType.TEXT, value=input)
        elif file:
            input_port = Port(data_type=PortType.FILE, mime_types=[MimeType(file.content_type)], value=file.file.read())
        else:
            return JSONResponse(
                status_code=400, content={"message": "Invalid input type"}
            )
        
        if request_obj.openplugin_manifest_url is not None:
            if request_obj.openplugin_manifest_url.startswith("http"):
                plugin_obj = PluginBuilder.build_from_manifest_url(
                    request_obj.openplugin_manifest_url
                )
            else:
                plugin_obj = PluginBuilder.build_from_manifest_file(
                    request_obj.openplugin_manifest_url
                )
        elif request_obj.openplugin_manifest_obj is not None :
            plugin_obj = PluginBuilder.build_from_manifest_obj(request_obj.openplugin_manifest_obj)
        else:
            return JSONResponse(
                status_code=400,
                content={"message": "Either manifest URL or manifest object is required"},
            )
      
        if request_obj.config is None:
            config = Config(openai_api_key=os.environ["OPENAI_API_KEY"])
        else:
            config = request_obj.config
        pipeline = PluginExecutionPipeline(plugin=plugin_obj)
        response_obj = await pipeline.run(
            input_port=input_port,
            config=config,
            preferred_approach=request_obj.preferred_approach,
            header=request_obj.header,
            auth_query_param=request_obj.auth_query_param,
            output_module_names=request_obj.output_module_names,
            run_all_output_modules=request_obj.run_all_output_modules,
        )
        json_data = response_obj.model_dump(
            exclude={"output_ports__type_object", "output_ports__value"}
        )
        end = datetime.datetime.now()
        elapsed_time = end - start
        response = {
            "metadata": {
                "start_time": start.strftime("%Y-%m-%d %H:%M:%S.%f"),
                "end_time": end.strftime("%Y-%m-%d %H:%M:%S.%f"),
                "total_time_taken_seconds": elapsed_time.total_seconds(),
                "total_time_taken_ms": elapsed_time.microseconds,
            },
            "response": json_data,
        }
        return JSONResponse(status_code=200, content=response)
    except Exception as e:
        print(e)
        traceback.print_exc()
        return JSONResponse(
            status_code=500, content={"message": f"Failed to run plugin: {e}"}
        )
