#!/usr/bin/env bash
set -euo pipefail
cd ~/legal-ai
source .venv/bin/activate
export PYTHONPATH=$PWD/backend

echo "[1/5] Проверяю ключевые файлы..."
ls -la backend/app | sed 's/^/  /'
ls -la backend/auth/routes | sed 's/^/  /' || true

echo "[2/5] Создаю резервную копию app/main.py (если есть) и пишу стабильную версию..."
mkdir -p backend/app
if [ -f backend/app/main.py ]; then cp backend/app/main.py backend/app/main.py.bak; fi

cat > backend/app/main.py <<'PY'
from fastapi import FastAPI
from typing import Any, Dict

# База данных (создадим таблицы на старте)
try:
    from app.database import Base, engine
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print("DB init skipped:", e)

app = FastAPI(title="LegalAI API")

@app.get("/health")
def health() -> Dict[str, Any]:
    return {"status": "ok"}

# Подключаем наши роуты, если доступны
try:
    from auth.routes import phone_sms
    app.include_router(phone_sms.router)
    print("router phone_sms: OK")
except Exception as e:
    print("router phone_sms skipped:", e)

try:
    from auth.routes import reset_password
    app.include_router(reset_password.router)
    print("router reset_password: OK")
except Exception as e:
    print("router reset_password skipped:", e)
PY

echo "[3/5] Проверка импорта приложения..."
python3 - <<'PY'
import importlib
m = importlib.import_module("app.main")
app = getattr(m, "app", None)
print("✅ app.main импортирован, app:", type(app))
PY

echo "[4/5] Перезапуск Uvicorn..."
pkill -f uvicorn || true
cd backend
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > ~/legal-ai/uvicorn.out 2>&1 &
sleep 3

echo "[5/5] Проверка /health и логов:"
echo "---- CURL ----"
curl -i --max-time 3 http://127.0.0.1:8000/health || true
echo
echo "---- TAIL uvicorn.out ----"
tail -n 80 ~/legal-ai/uvicorn.out || true
