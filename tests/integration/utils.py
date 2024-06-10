import typing
from urllib.parse import quote
from fastapi import FastAPI
from httpx import AsyncClient


async def get_test_client(
    app: FastAPI,
) -> typing.AsyncGenerator[AsyncClient, None]:
    test_url = f"http://test-{quote(app.title)}"

    async with AsyncClient(app=app, base_url=test_url) as client:
        yield client
