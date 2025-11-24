from functools import lru_cache
from typing import Optional
import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from .env or environment variables."""

    # Конфиг pydantic v2
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",
    )

    # Определяем, запущены ли мы в CI (GitHub Actions)
    CI: bool = os.getenv("CI", "").lower() == "true"

    if CI:
        # В GitHub Actions используем локальную тестовую SQLite
        DATABASE_URL: str = "sqlite:///./test.db"
    else:
        # В проде используем размещение БД в безопасной директории
        DATABASE_URL: str = "sqlite:////srv/legal-ai/data/legalai.db"

    # Секрет для JWT / сессий (обязательно переопределим в .env)
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
    """Возвращает кэшированный экземпляр настроек."""
    return Settings()
