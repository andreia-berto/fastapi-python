import logging

from fastapi import APIRouter, HTTPException, status

from social_media_api.database import user_table
from social_media_api.model.user import UserIn
from social_media_api.routers.post import database
from social_media_api.security import (
    get_user,
    get_password_hash,
    authenticate_user,
    create_access_token,
)

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: UserIn):
    if await get_user(user.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")

    hashed_password = get_password_hash(user.password)
    query = user_table.insert().values(email=user.email, password=hashed_password)

    logger.debug(query)

    await database.execute(query)
    return {"detail": "User created successfully"}


@router.post("/login", status_code=status.HTTP_200_OK)
async def login_user(user: UserIn):
    user = await authenticate_user(user.email, user.password)
    access_token = create_access_token(user.email)
    return {"access_token": access_token, "token_type": "bearer"}