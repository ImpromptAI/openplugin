import os
from fastapi import FastAPI
from fastapi import APIRouter
from openplugin.api import plugin_selector
from .http_error import http_error_handler
from starlette.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openplugin.api import api_signature_selector, plugin_selector

API_PREFIX = "/api"
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development')


def create_app() -> FastAPI:
    app = FastAPI(
        title="OpenPlugin",
        openapi_url=f"{API_PREFIX}/openapi.json",
        docs_url=f"{API_PREFIX}/docs"
    )
    if ENVIRONMENT == 'production':
        app.root_path = "/openplugin/"

    # add routes
    router = APIRouter()
    router.include_router(plugin_selector.router)
    router.include_router(api_signature_selector.router)
    app.include_router(router, prefix=API_PREFIX)

    app.add_exception_handler(HTTPException, http_error_handler)
    # Allow CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app


app = create_app()
