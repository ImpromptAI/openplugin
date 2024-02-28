import toml
import datetime
from fastapi import APIRouter
from fastapi.responses import JSONResponse

# Create a FastAPI router instance
router = APIRouter(
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


def get_project_version():
    pyproject_data = toml.load("pyproject.toml")
    return pyproject_data["tool"]["poetry"]["version"]


@router.get("/info")
def info():
    # time taken to run this function
    start = datetime.datetime.now()
    response = JSONResponse(
        status_code=200,
        content={"message": "OpenPlugin API"},
    )
    end = datetime.datetime.now()
    elapsed_time = end - start
    import toml

    return JSONResponse(
        status_code=200,
        content={
            "version": get_project_version(),
            "message": "OpenPlugin API",
            "start_time": start.strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": end.strftime("%Y-%m-%d %H:%M:%S"),
            "time_taken_seconds": elapsed_time.seconds,
            "time_taken_ms": elapsed_time.microseconds,
        },
    )


@router.get("/")
def version():
    return JSONResponse(
        status_code=200,
        content={"message": "OpenPlugin API"},
    )
