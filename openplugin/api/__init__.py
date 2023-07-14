import os
from openplugin.api import langchain
from openplugin.api import openai
from openplugin.api import imprompt
from fastapi import FastAPI
from fastapi import APIRouter
from .http_error import http_error_handler
from starlette.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openplugin.api import genric_selector

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
    # router.include_router(langchain.router)
    # router.include_router(imprompt.router)
    # router.include_router(openai.router)
    router.include_router(genric_selector.router)
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
