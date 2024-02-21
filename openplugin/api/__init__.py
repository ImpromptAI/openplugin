import os

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from openplugin.api import (
    operation_execution,
    operation_signature_builder,
    plugin_pipeline,
    plugin_selector,
)

from .http_error import http_error_handler

API_PREFIX = "/api"
ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")


# Define a function to create the FastAPI application
def create_app() -> FastAPI:
    app = FastAPI(
        title="OpenPlugin",
        openapi_url=f"{API_PREFIX}/openapi.json",
        docs_url=f"{API_PREFIX}/docs",
    )
    if ENVIRONMENT == "production":
        app.root_path = "/openplugin/"

    # Create an APIRouter instance to manage routes
    router = APIRouter()
    router.include_router(plugin_selector.router)
    router.include_router(operation_signature_builder.router)
    router.include_router(operation_execution.router)
    router.include_router(plugin_pipeline.router)

    app.include_router(router, prefix=API_PREFIX)

    # Add an exception handler for HTTPException using the provided custom handler

    app.add_exception_handler(HTTPException, http_error_handler)  # type: ignore

    # Allow Cross-Origin Resource Sharing (CORS)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # type: ignore
        allow_credentials=True,  # type: ignore
        allow_methods=["*"],  # type: ignore
        allow_headers=["*"],  # type: ignore
    )

    return app


# Create the FastAPI application
app = create_app()
