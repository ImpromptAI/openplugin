from . import langchain
from fastapi import FastAPI
from fastapi import APIRouter
from .http_error import http_error_handler
from starlette.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware

API_PREFIX = "/api"


def create_app() -> FastAPI:
    app = FastAPI()
    # add routes
    router = APIRouter()
    router.include_router(langchain.router)
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
