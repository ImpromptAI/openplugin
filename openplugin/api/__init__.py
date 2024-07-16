import sys
from typing import Optional

from fastapi import APIRouter, FastAPI
from loguru import logger
from starlette.middleware.cors import CORSMiddleware

from openplugin.api import (
    function_providers,
    helpers,
    info,
    plugin_execution_pipeline,
    processors,
)


# Define a function to create the FastAPI application
def create_app(root_path: Optional[str] = None) -> FastAPI:
    logger.remove()
    try:
        logger.add(sys.stdout, level="DEBUG")
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
    # router.include_router(plugin_selector.router)
    # router.include_router(operation_signature_builder.router)
    # router.include_router(operation_execution.router)
    router.include_router(info.router)
    router.include_router(plugin_execution_pipeline.router)
    router.include_router(processors.router)
    router.include_router(function_providers.router)
    router.include_router(helpers.router)
    app.include_router(router, prefix=API_PREFIX)

    return app
