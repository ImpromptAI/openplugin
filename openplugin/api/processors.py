import json
import os

# Get the current working directory
from fastapi import APIRouter
from fastapi.responses import JSONResponse

# Create a FastAPI router instance
router = APIRouter(
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.get("/processors")
def processors():
    processors = []
    current_folder = os.getcwd()
    file_name = f"{current_folder}/openplugin/resources/processors.json"
    with open(file_name, "r") as file:
        processors = json.load(file)
    return JSONResponse(status_code=200, content=processors)
