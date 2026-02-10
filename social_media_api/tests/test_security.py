import pytest
from jose import jwt

from social_media_api import security

@pytest.mark.anyio
async def test_access_token_expire_minutest():
    assert security.access_token_expire_minutes() == 30

@pytest.mark.anyio
async def test_create_access_token():
    token = security.create_access_token("123")
    assert {"sub": "123"}.items() <= jwt.decode(
        token, key=security.SECRET_KEY, algorithms=[security.ALGORITHM]
    ).items()


@pytest.mark.anyio
async def test_password_hashes():
    password = "password"
    assert security.verify_password(password, security.get_password_hash(password))

@pytest.mark.anyio
async def get_user(registered_user_fixture):
    user = await security.get_user(registered_user_fixture)

    assert user.email == registered_user_fixture["email"]

@pytest.mark.anyio
async def test_get_user_not_found():
    user = await security.get_user("test@example.com")
    assert user is None

@pytest.mark.anyio
async def test_authenticate_user(registered_user_fixture: dict):
    user = await security.authenticate_user(registered_user_fixture["email"], registered_user_fixture["password"])
    assert user.email == registered_user_fixture["email"]

@pytest.mark.anyio
async def test_authenticate_user_wrong_password(registered_user_fixture: dict):
    with pytest.raises(security.HTTPException):
        await security.authenticate_user(registered_user_fixture["email"],"test")


@pytest.mark.anyio
async def test_authenticate_user_not_found():
    with pytest.raises(security.HTTPException):
        await security.authenticate_user("test@example.net","1234")

@pytest.mark.anyio
async def test_get_current_user(registered_user_fixture: dict):
    token = security.create_access_token(registered_user_fixture["email"])
    user = await security.get_current_user(token)
    assert user.email == registered_user_fixture["email"]

@pytest.mark.anyio
async def test_get_current_user_invalid_token():
    with pytest.raises(security.HTTPException):
        await security.get_current_user("invalid token")