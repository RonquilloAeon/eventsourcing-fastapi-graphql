import os

import psycopg2
from contextlib import contextmanager
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

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
    run_db_statement(f"CREATE DATABASE {DB_NAME}")


def pytest_unconfigure(config) -> None:
    run_db_statement(f"DROP DATABASE {DB_NAME}")
