from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from app.config import get_settings

# Глобальные настройки
settings = get_settings()

# Пробуем вытащить URL БД из настроек
DATABASE_URL: Optional[str] = getattr(settings, "DATABASE_URL", None) or getattr(
    settings, "database_url", None
)

if not DATABASE_URL:
    # На всякий случай дефолт — локальная SQLite
    DATABASE_URL = "sqlite:///./dev.db"

# Для SQLite нужен спец-параметр
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# Движок SQLAlchemy
engine = create_engine(DATABASE_URL, connect_args=connect_args)

# Фабрика сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс моделей
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Зависимость FastAPI для получения сессии БД."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

