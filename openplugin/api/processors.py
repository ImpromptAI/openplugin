import json
import os
from typing import List, Optional

# Get the current working directory
from fastapi import APIRouter
from pydantic import BaseModel

# Create a FastAPI router instance
router = APIRouter(
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


class MetadataResponse(BaseModel):
    key: str
    required: bool
    default_value: Optional[str] = None
    type: str
    long_form: bool
    is_user_provided: Optional[bool] = None


class ImplementationsResponse(BaseModel):
    processor_implementation_type: str
    name: str
    metadata: List[MetadataResponse]


class ProcessorResponse(BaseModel):
    processor_type: str
    processor_name: str
    description: str
    input_port: str
    output_port: str
    implementations: List[ImplementationsResponse]


@router.get(
    "/processors",
    tags=["processors"],
    description="Enpoint to retrieve list of available processors",
    response_model=List[ProcessorResponse],
)
def processors():
    plist = []
    current_folder = os.getcwd()
    file_name = f"{current_folder}/openplugin/resources/processors.json"
    with open(file_name, "r") as file:
        processors = json.load(file)
        for processor in processors:
            plist.append(ProcessorResponse(**processor))
    return plist
