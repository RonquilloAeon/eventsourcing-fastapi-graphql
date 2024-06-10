import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from .config import settings
from .graphql import router as graphql_router

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    # Logging
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logging.basicConfig(level=log_level)
    logger.setLevel(log_level)

    # App
    _app = FastAPI(
        title="Eventsourcing Demo API",
    )
    _app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_headers=["*"],
        allow_methods=["*"],
        allow_origins=["*"],
    )
    _app.add_middleware(GZipMiddleware, minimum_size=1000)

    # Routes
    _app.include_router(graphql_router, prefix="/graphql")

    return _app
