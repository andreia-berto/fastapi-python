from datetime import datetime, timezone,  timedelta
import logging
from http import HTTPStatus

from fastapi import HTTPException, status
from jose import jwt, ExpiredSignatureError, JWTError
from passlib.context import CryptContext
from rich import status

from social_media_api.config import get_settings
from social_media_api.database import get_database, user_table
from social_media_api.model.user import UserIn

logger = logging.getLogger(__name__)

SECRET_KEY = get_settings().SECRET_KEY
ALGORITHM = get_settings().ALGORITHM
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
)

credentials_exception = HTTPException( status_code=HTTPStatus.UNAUTHORIZED, detail="Could not validate credentials",)


def access_token_expire_minutes() -> int:
    return int(get_settings().ACCESS_TOKEN_EXPIRE_MINUTES)

def create_access_token(email: str):
    logger.debug("Creating access token", extra={"email": email})
    expire = datetime.now(timezone.utc) + timedelta(minutes=access_token_expire_minutes())
    jwt_data = {"sub": email, "exp": expire}
    encoded_jwt = jwt.encode(jwt_data, key=SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

async def get_user(email: str) -> UserIn | None:
    logger.debug("Fetching user from the database", extra={"email": email})
    query = user_table.select().where(user_table.c.email == email)
    result = await get_database().fetch_one(query)
    if result:
        return UserIn(email=result["email"], password=result["password"])

async def authenticate_user(email: str, password: str):
    logger.debug("Authenticating user", extra={"email": email, "password": password})
    user = await get_user(email)
    if not user:
        raise credentials_exception

    if not verify_password(password, user.password):
        raise credentials_exception

    return user

async def get_current_user(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except ExpiredSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    except JWTError as e:
        raise credentials_exception from e

    use = await get_user(email=email)
    if not use:
        raise credentials_exception
    return use