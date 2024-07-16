import datetime

import toml
from fastapi import APIRouter
from pydantic import BaseModel

# Create a FastAPI router instance
router = APIRouter(
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


def get_project_version():
    pyproject_data = toml.load("pyproject.toml")
    return pyproject_data["tool"]["poetry"]["version"]


class InfoResponse(BaseModel):
    """Response schema for Info endpoint"""

    version: str
    message: str
    start_time: str
    end_time: str
    time_taken_seconds: int
    time_taken_ms: int


@router.get(
    "/info",
    tags=["info"],
    description="Enpoint to retrieve openplugin server information",
    response_model=InfoResponse,
)
def info():
    # time taken to run this function
    start = datetime.datetime.now()
    end = datetime.datetime.now()
    elapsed_time = end - start

    return InfoResponse(
        version=get_project_version(),
        message="OpenPlugin API",
        start_time=start.strftime("%Y-%m-%d %H:%M:%S"),
        end_time=end.strftime("%Y-%m-%d %H:%M:%S"),
        time_taken_seconds=elapsed_time.seconds,
        time_taken_ms=elapsed_time.microseconds,
    )
