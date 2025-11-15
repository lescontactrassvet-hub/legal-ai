#!/usr/bin/env bash
set -euo pipefail

cd ~/legal-ai
source .venv/bin/activate

# 1) Гарантируем, что каталоги - это Python-пакеты
touch backend/app/__init__.py
touch backend/app/models/__init__.py
touch backend/app/notifications/__init__.py
touch backend/auth/__init__.py
mkdir -p backend/auth/routes
touch backend/auth/routes/__init__.py

# 2) PYTHONPATH на каталог backend
export PYTHONPATH="$PWD/backend"

# 3) Быстрая проверка, что app импортируется
python3 - <<'PY'
import importlib
import sys
print("sys.path[0]:", sys.path[0])
m = importlib.import_module("app")
print("✅ import app OK; package:", m.__package__)
PY

# 4) Миграция БД
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

# 5) Перезапуск uvicorn
pkill -f uvicorn || true
cd backend
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > ~/legal-ai/uvicorn.out 2>&1 &
sleep 2

# 6) Быстрые проверки
echo "---- ps uvicorn ----"
pgrep -fa uvicorn || true
echo "---- curl /health ----"
curl -i --max-time 3 http://127.0.0.1:8000/health || true
echo
echo "---- tail uvicorn.out (last 60) ----"
tail -n 60 ~/legal-ai/uvicorn.out || true
