#!/usr/bin/env bash
set -euo pipefail

ROOT="$HOME/legal-ai"
BACK="$ROOT/backend"
APP="$BACK/app"

echo "[1/5] Останавливаю uvicorn..."
pkill -f "uvicorn app.main:app" 2>/dev/null || true
sleep 1

echo "[2/5] Обновляю security.py на pbkdf2_sha256..."
cat > "$APP/security.py" <<'PY'
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

# Чисто-Python схема (без bcrypt/cryptography)
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def hash_password(p: str) -> str:
    return pwd_context.hash(p)

def create_access_token(subject: str) -> str:
    to_encode = {"sub": subject, "exp": datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)}
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
PY

echo "[3/5] Перезапускаю uvicorn (фон)..."
cd "$BACK"
source "$ROOT/.venv/bin/activate"
export PYTHONPATH="$PWD"
nohup python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --log-level info > "$BACK/uvicorn_live.log" 2>&1 &
disown
sleep 3

echo "[Проверка /health]"
curl -s -i http://127.0.0.1:8000/health || true
echo

echo "[4/5] Тест: регистрация пользователя..."
# пробуем зарегистрировать (повторная регистрация допустима — вернёт 400)
curl -s -i -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "123456"}'
echo

echo "[5/5] Тест: логин и профиль..."
LOGIN_JSON="$(curl -s -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=123456")"

echo "LOGIN RESPONSE: $LOGIN_JSON"
TOKEN="$(python - <<'PY'
import json,os
s=os.environ.get("LOGIN_JSON","")
try:
    print(json.loads(s).get("access_token",""))
except Exception:
    print("")
PY
)"
if [ -z "$TOKEN" ]; then
  echo "❌ Не удалось получить токен. Смотрите лог: $BACK/uvicorn_live.log"
  exit 1
fi

echo "[PROFILE RESPONSE]"
curl -s -i -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8000/auth/profile
echo
echo "Готово."
