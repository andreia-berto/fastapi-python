import os
from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from social_media_api.database import get_database, get_engine, metadata
from social_media_api.main import app

os.environ["ENV_STATE"] = "test"


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture()
def client() -> Generator:
    yield TestClient(app)


@pytest.fixture(autouse=True)
async def db() -> AsyncGenerator:
    metadata.create_all(get_engine())
    await get_database().connect()
    yield
    await get_database().disconnect()


@pytest.fixture()
async def async_client(client) -> AsyncGenerator:
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url=client.base_url) as ac:
        yield ac
