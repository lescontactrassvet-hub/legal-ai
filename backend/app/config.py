from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Конфиг pydantic v2
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",
    )

    # База данных (по умолчанию SQLite + aiosqlite в корне backend)
    DATABASE_URL: str = "sqlite:///./legalai.db"

    # Секрет для JWT / сессий (обязательно переопредели в .env)
    SECRET_KEY: str = "CHANGE_ME_PLEASE"

    # Алгоритм для JWT
    ALGORITHM: str = "HS256"

    # Время жизни access/refresh токенов
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Sentry (может быть пустым)
    SENTRY_DSN: Optional[str] = None


@lru_cache
def get_settings() -> "Settings":
    return Settings()
