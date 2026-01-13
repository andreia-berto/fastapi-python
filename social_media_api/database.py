from functools import lru_cache

import databases
import sqlalchemy

from social_media_api.config import get_settings

settings = get_settings()

metadata = sqlalchemy.MetaData()

post_table = sqlalchemy.Table(
    "posts",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("body", sqlalchemy.String),
)


comment_table = sqlalchemy.Table(
    "comments",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("body", sqlalchemy.String),
    sqlalchemy.Column("post_id", sqlalchemy.ForeignKey("posts.id"), nullable=False),
)

user_table = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("email", sqlalchemy.String, unique=True),
    sqlalchemy.Column("password", sqlalchemy.String),
)


@lru_cache()
def get_engine() -> sqlalchemy.Engine:
    return sqlalchemy.create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
    )


@lru_cache()
def get_database() -> databases.Database:
    return databases.Database(
        settings.DATABASE_URL,
        force_rollback=settings.DB_FORCE_ROLL_BACK,
    )
