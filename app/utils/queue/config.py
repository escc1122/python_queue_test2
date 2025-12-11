import os
from dataclasses import dataclass
from dotenv import load_dotenv


load_dotenv()


def _get_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


@dataclass(frozen=True)
class Settings:
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = _get_int("REDIS_PORT", 6379)
    redis_db: int = _get_int("REDIS_DB", 0)
    redis_password: str | None = os.getenv("REDIS_PASSWORD") or None
    blpop_timeout: int = _get_int("BLPOP_TIMEOUT", 5)  # seconds
    log_level: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()
