#!/usr/bin/env bash
set -euo pipefail

ROOT="$HOME/legal-ai"
APP="$ROOT/backend/app"
LOG="$ROOT/uvicorn.out"

# 1) Патчим app/security.py: безопасная обрезка до 72 байт
cat > "$APP/security.py" <<'PY'
from passlib.context import CryptContext

# bcrypt имеет лимит 72 байта на пароль.
_MAX_BCRYPT_BYTES = 72
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _truncate_for_bcrypt(secret: str) -> str:
    data = secret.encode("utf-8")
    if len(data) > _MAX_BCRYPT_BYTES:
        data = data[:_MAX_BCRYPT_BYTES]
        # игнорируем «хвост» по границе символов
        return data.decode("utf-8", errors="ignore")
    return secret

def get_password_hash(password: str) -> str:
    """Хэширует пароль, учитывая лимит bcrypt в 72 байта."""
    safe = _truncate_for_bcrypt(password)
    return pwd_context.hash(safe)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет пароль с учётом лимита bcrypt."""
    safe = _truncate_for_bcrypt(plain_password)
    return pwd_context.verify(safe, hashed_password)
PY

# 2) Активируем окружение и PYTHONPATH
cd "$ROOT"
source .venv/bin/activate
export PYTHONPATH="$ROOT/backend"

# 3) Перезапускаем uvicorn в фоне
pkill -f uvicorn || true
cd "$ROOT/backend"
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info > "$LOG" 2>&1 &
sleep 2

# 4) Быстрая проверка /health
echo "---- /health ----"
curl -i http://127.0.0.1:8000/health || true

# 5) Повтор регистрации (новые уникальные email/phone)
echo
echo "---- /auth/register ----"
curl -i -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test8@example.com","phone":"+79991112288","password":"MySecurePass123"}' || true

echo
echo "---- tail uvicorn.out ----"
tail -n 60 "$LOG" || true
