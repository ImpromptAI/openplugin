from typing import Optional

from fastapi import APIRouter, FastAPI,  Request, status
from loguru import logger
from starlette.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from openplugin.api import (
    info,
    operation_execution,
    operation_signature_builder,
    plugin_execution_pipeline,
    plugin_selector,
    processors
)
from fastapi.responses import JSONResponse
from loguru import logger

# Define a function to create the FastAPI application
def create_app(root_path: Optional[str] = None) -> FastAPI:
    logger.remove()
    try:
        logger.level("FLOW", no=38, color="<yellow>", icon="🚀")
    except Exception as e:
        print(e)
    API_PREFIX = "/api"
    if root_path:
        API_PREFIX = f"/{root_path}{API_PREFIX}"
    app = FastAPI(
        title="OpenPlugin",
        openapi_url=f"{API_PREFIX}/openapi.json",
        docs_url=f"{API_PREFIX}/docs",
    )

    @app.middleware("http")
    async def add_cors_headers(request, call_next):
        response = await call_next(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = (
            "GET, POST, PUT, DELETE, OPTIONS"
        )
        response.headers["Access-Control-Allow-Headers"] = (
            "Content-Type, Authorization"
        )
        return response

    # Allow Cross-Origin Resource Sharing (CORS)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # type: ignore
        allow_credentials=True,  # type: ignore
        allow_methods=["*"],  # type: ignore
        allow_headers=["*"],  # type: ignore
    )

    # Create an APIRouter instance to manage routes
    router = APIRouter()
    router.include_router(plugin_selector.router)
    router.include_router(operation_signature_builder.router)
    router.include_router(operation_execution.router)
    router.include_router(info.router)
    router.include_router(plugin_execution_pipeline.router)
    router.include_router(processors.router)

    app.include_router(router, prefix=API_PREFIX)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        print(request.form())
        exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
        logger.error(f"{request}: {exc_str}")
        print(f"{request}: {exc_str}")
        content = {'status_code': 10422, 'message': exc_str, 'data': None}
        return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
    return app
