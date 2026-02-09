from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

class EnvConfig(BaseSettings):
    ENV_STATE: str

    model_config = SettingsConfigDict(env_file=".env")


class GlobalConfig(BaseSettings):
    SECRET_KEY: str
    ALGORITHM:str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    DATABASE_URL: str

class DevConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_file=".env.dev")


class ProdConfig(GlobalConfig):
    model_config = SettingsConfigDict()


class TestConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_file=".env.test")


@lru_cache()
def get_config(env_state: str):
    configs = {
        "dev": DevConfig,
        "prod": ProdConfig,
        "test": TestConfig,
    }
    try:
        return configs[env_state]()
    except KeyError:
        raise ValueError(f"Invalid ENV_STATE: {env_state}")


def get_settings():
    env_state = EnvConfig().ENV_STATE
    return get_config(env_state)
