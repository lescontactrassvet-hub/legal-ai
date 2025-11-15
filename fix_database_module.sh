#!/usr/bin/env bash
set -e
cd ~/legal-ai/backend/app

# 1. Проверяем наличие database.py, если нет — создаём
if [ ! -f database.py ]; then
  echo "Создаю app/database.py..."
  cat > database.py <<'PY'
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DB_URL = os.getenv("DATABASE_URL", "sqlite:///./legalai.db")

connect_args = {"check_same_thread": False} if DB_URL.startswith("sqlite") else {}
engine = create_engine(DB_URL, connect_args=connect_args, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
PY
else
  echo "✅ database.py уже существует"
fi

# 2. Проверим, что файл читается без ошибок
cd ~/legal-ai
export PYTHONPATH=$PWD/backend
source .venv/bin/activate
python3 - <<'PY'
import importlib
m = importlib.import_module("app.database")
print("✅ app.database импортируется успешно")
PY

# 3. Повторим миграцию
python3 - <<'PY'
from app.database import Base, engine
from app.models import User, EmailToken
try:
    from app.models import SmsToken
except Exception:
    SmsToken = None
Base.metadata.create_all(bind=engine)
print("✅ DB schema synced")
PY
