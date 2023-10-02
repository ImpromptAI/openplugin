import os

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException

from openplugin.api import (
    operation_execution,
    operation_signature_builder,
    plugin_selector,
)
from openplugin.api.http_error import http_error_handler

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
    app.include_router(router, prefix=API_PREFIX)

    # Add an exception handler for HTTPException using the provided custom handler
    app.add_exception_handler(HTTPException, http_error_handler)

    # Allow Cross-Origin Resource Sharing (CORS)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


# Create the FastAPI application
app = create_app()
