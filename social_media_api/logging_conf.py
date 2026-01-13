import logging
from logging.config import dictConfig

from social_media_api.config import DevConfig, get_settings

settings = get_settings()


def obfuscated(email: str, obfuscated_lenght: int) -> str:
    characters = email[:obfuscated_lenght]
    first, last = email.split("@")
    return characters + ("*" * (len(first) - obfuscated_lenght)) + "@" + last


class EmailObfuscationFilter(logging.Filter):
    def __init__(self, name: str = "", obfuscated_lenght: int = 2) -> None:
        super().__init__(name)
        self.obfuscated_lenght = obfuscated_lenght

    def filter(self, record: logging.LogRecord) -> bool:
        if "email" in record.__dict__:
            record.email = obfuscated(record.email, self.obfuscated_lenght)


def configure_logging() -> None:
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {
                "correlation_id": {
                    "()": "asgi_correlation_id.CorrelationIdFilter",
                    "uuid_length": 8 if isinstance(settings, DevConfig) else 32,
                    "default_value": "-",
                }
            },
            "formatters": {
                "console": {
                    "class": "logging.Formatter",
                    "datefmt": "%Y-%m-%dT%H:%M:%S",
                    "format": "(%(correlation_id)s) %(name)s:%(lineno)d - %(message)s",
                },
                "file": {
                    "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
                    "datefmt": "%Y-%m-%dT%H:%M:%S",
                    "format": "%(asctime)s %(msecs)03d %(levelname)-8s %(correlation_id)s %(name)s %(lineno)d %(message)s",
                },
            },
            "handlers": {
                "default": {
                    "class": "rich.logging.RichHandler",
                    "level": "DEBUG",
                    "formatter": "console",
                    "filters": ["correlation_id"],
                },
                "rotating_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "DEBUG",
                    "formatter": "file",
                    "filename": "socialmedia.log",
                    "maxBytes": 1024 * 1024,
                    "backupCount": 2,
                    "encoding": "utf8",
                    "filters": ["correlation_id"],
                },
            },
            "loggers": {
                "uvicorn": {"handlers": ["default", "rotating_file"], "level": "INFO"},
                "social_media_api": {
                    "handlers": ["default", "rotating_file"],
                    "level": "DEBUG" if isinstance(settings, DevConfig) else "INFO",
                    "propagate": False,
                },
                "databases": {"handlers": ["default"], "level": "WARNING"},
                "aiosqlite": {"handlers": ["default"], "level": "WARNING"},
            },
            "root": {
                "handlers": ["default"],
                "level": "WARNING",
            },
        }
    )
