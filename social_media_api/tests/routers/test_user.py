import pytest
from httpx import AsyncClient


async def register_user(async_client: AsyncClient, email: str, password: str):
    return await async_client.post("/register", json={"email": email, "password": password})


@pytest.mark.anyio
async def test_register_user_success(async_client: AsyncClient):
    response = await register_user(async_client, email="test_maria@example.net", password="1234")
    assert response.status_code == 201
    assert "User created" in response.json()["detail"]


@pytest.mark.anyio
async def test_register_user_already_exists(async_client: AsyncClient, registered_user_fixture):
    response = await register_user(async_client, registered_user_fixture["email"], registered_user_fixture["password"])
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]

@pytest.mark.anyio
async def test_login_user_not_exists(async_client: AsyncClient):
    response = await async_client.post("/login", json={"email": "test@example.net", "password": "1234"})

    assert response.status_code == 401


@pytest.mark.anyio
async def test_login_user_success(async_client: AsyncClient, registered_user_fixture):
    response = await async_client.post("/login", json={"email": registered_user_fixture["email"], "password": registered_user_fixture["password"]})
    assert response.status_code == 200


