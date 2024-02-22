from typing import Optional

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from openplugin.api import (
    operation_execution,
    operation_signature_builder,
    plugin_pipeline,
    plugin_selector,
    info,
)
from openplugin.plugins.functions import API


# Define a function to create the FastAPI application
def create_app(root_path: Optional[str] = None) -> FastAPI:
    logger.remove()
    logger.level("FLOW", no=38, color="<yellow>", icon="🚀")

    API_PREFIX = "/api"
    if root_path:
        API_PREFIX = f"/{root_path}{API_PREFIX}"
    print("+++")
    print(API_PREFIX)
    app = FastAPI(
        title="OpenPlugin",
        openapi_url=f"{API_PREFIX}/openapi.json",
        docs_url=f"{API_PREFIX}/docs",
    )
    # Create an APIRouter instance to manage routes
    router = APIRouter()
    router.include_router(plugin_selector.router)
    router.include_router(operation_signature_builder.router)
    router.include_router(operation_execution.router)
    router.include_router(plugin_pipeline.router)
    router.include_router(info.router)

    app.include_router(router, prefix=API_PREFIX)

    # Allow Cross-Origin Resource Sharing (CORS)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # type: ignore
        allow_credentials=True,  # type: ignore
        allow_methods=["*"],  # type: ignore
        allow_headers=["*"],  # type: ignore
    )

    return app
