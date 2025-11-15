#!/usr/bin/env bash
set -euo pipefail

ROOT="$HOME/legal-ai"
APP_DIR="$ROOT/backend/app"
DB_FILE="$ROOT/legalai.db"

# 1) Чиним app/database.py — абсолютный путь к БД
cat > "$APP_DIR/database.py" <<PY
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DB_FILE = os.path.expanduser("${DB_FILE}")
DB_URL = f"sqlite:///{DB_FILE}"

connect_args = {"check_same_thread": False}
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

# 2) Активируем venv и PYTHONPATH
cd "$ROOT"
source .venv/bin/activate
export PYTHONPATH="$ROOT/backend"

# 3) Покажем какой файл БД теперь используется и применим схему
python3 - <<'PY'
from app.database import Base, engine
from app.models import User, EmailToken
try:
    from app.models import SmsToken
except Exception:
    pass
print("DB file:", engine.url.database)
Base.metadata.create_all(bind=engine)
# выведем колонки таблицы users
from sqlalchemy import text
with engine.begin() as conn:
    cols = [r[1] for r in conn.exec_driver_sql("PRAGMA table_info(users)").fetchall()]
print("users columns:", cols)
PY

# 4) Перезапускаем uvicorn в фоне
pkill -f uvicorn || true
cd "$ROOT/backend"
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info > "$ROOT/uvicorn.out" 2>&1 &
sleep 2

# 5) Проверяем /health
curl -i http://127.0.0.1:8000/health || true
