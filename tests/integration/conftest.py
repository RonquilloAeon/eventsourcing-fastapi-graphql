import os
import typing

import psycopg2
import pytest
from contextlib import contextmanager
from httpx import AsyncClient
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from .utils import get_test_client
from src.entrypoints.api.app import create_app as create_api_app

DB_NAME = os.getenv("POSTGRES_DBNAME")
DB_CONFIG = {
    "database": "postgres",
    "host": os.getenv("POSTGRES_HOST"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "port": os.getenv("POSTGRES_PORT"),
    "user": os.getenv("POSTGRES_USER"),
}


@contextmanager
def db_conn():
    conn = psycopg2.connect(**DB_CONFIG)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    try:
        yield conn
    finally:
        conn.close()


def run_db_statement(statement: str) -> None:
    with db_conn() as conn:
        with conn.cursor() as cursor:
            cursor.execute(statement)


def pytest_configure(config) -> None:
    try:
        run_db_statement(f"CREATE DATABASE {DB_NAME}")
    except psycopg2.errors.lookup("42P04"):
        run_db_statement(f"DROP DATABASE {DB_NAME}")
        run_db_statement(f"CREATE DATABASE {DB_NAME}")


def pytest_unconfigure(config) -> None:
    run_db_statement(f"DROP DATABASE {DB_NAME}")


@pytest.fixture
async def api_client() -> AsyncClient:
    api_app = create_api_app()

    async for client in get_test_client(api_app):
        yield client


@pytest.fixture
def graphql_test_client(api_client):
    async def _wrapped_test_client(
        query: str,
        headers: dict[str, str] | None = None,
        variables: dict[str, typing.Any] | None = None,
    ):
        return await api_client.post(
            "/graphql",
            headers=headers,
            json={"query": query, "variables": variables or {}},
        )

    return _wrapped_test_client
