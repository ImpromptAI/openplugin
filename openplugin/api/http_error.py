from fastapi import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse


# Define an asynchronous function to handle HTTP exceptions
async def http_error_handler(_: Request, exc: HTTPException) -> JSONResponse:
    # Create a JSONResponse with a single key "errors" containing the exception detail
    # and set the status code to the HTTP exception's status code
    return JSONResponse({"errors": [exc.detail]}, status_code=exc.status_code)
