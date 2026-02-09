import os
from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from social_media_api.database import get_database, get_engine, metadata, user_table
from social_media_api.main import app

os.environ["ENV_STATE"] = "test"


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="session")
def setup_test_db():
    engine = get_engine()

    metadata.create_all(engine)

    yield

    metadata.drop_all(engine)


@pytest.fixture()
def client() -> Generator:
    yield TestClient(app)


@pytest.fixture(autouse=True)
async def db(setup_test_db) -> AsyncGenerator:
    await get_database().connect()

    transaction = await get_database().transaction()
    try:
        yield
    finally:
        await transaction.rollback()


@pytest.fixture()
async def async_client(client) -> AsyncGenerator:
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url=client.base_url) as ac:
        yield ac

@pytest.fixture()
async def registered_user_fixture(async_client) -> dict:
    user_details = {"email": "test@example.net", "password": "1234"}
    await async_client.post("/register", json=user_details)
    query = user_table.select().where(user_table.c.email == user_details["email"])
    user = await get_database().fetch_one(query)
    user_details["id"] = user.id
    return user_details