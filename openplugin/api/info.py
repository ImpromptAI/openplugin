from fastapi import APIRouter
from fastapi.responses import JSONResponse

# Create a FastAPI router instance
router = APIRouter(
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.get("/info")
def info():
    return JSONResponse(
        status_code=200,
        content={"message": "OpenPlugin API"},
    )


@router.get("/")
def version():
    return JSONResponse(
        status_code=200,
        content={"message": "OpenPlugin API"},
    )
