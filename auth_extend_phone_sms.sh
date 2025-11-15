#!/usr/bin/env bash
set -euo pipefail
cd ~/legal-ai/backend

mkdir -p app/notifications auth/routes app/models logs

# 0) Зависимости (только если не стоят)
if ! python3 -c "import email_validator" >/dev/null 2>&1; then
  pip install --no-input email-validator >/dev/null
fi

# 1) Простые «отправители» уведомлений (пишем в лог для тестов)
cat > app/notifications/senders.py <<'PY'
import os, time
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "logs")
LOG_DIR = os.path.abspath(LOG_DIR)
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "notifications.log")

def _write(line: str):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {line}\n")

def send_sms(phone: str, text: str):
    _write(f"SMS to {phone}: {text}")

def send_email(email: str, subject: str, text: str):
    _write(f"EMAIL to {email}: {subject} | {text}")
PY

# 2) Модели: SmsToken и журнал уведомлений (при необходимости)
cat > app/models/sms_token.py <<'PY'
from sqlalchemy import Column, Integer, String
from app.database import Base

class SmsToken(Base):
    __tablename__ = "sms_tokens"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(32), index=True)
    code = Column(String(10), index=True)
    created_at = Column(Integer, default=0)
PY

# 2.1) Обновим __init__.py, чтобы экспортировались новые модели
python3 - <<'PY'
import os, re, sys
p = "app/models/__init__.py"
if not os.path.exists(p):
    with open(p, "w", encoding="utf-8") as f:
        f.write("from app.database import Base\n")
# гарантируем импорты
with open(p, "r+", encoding="utf-8") as f:
    s = f.read()
    add = []
    if "from app.models.sms_token import SmsToken" not in s:
        add.append("from app.models.sms_token import SmsToken")
    if "from app.models.email_token import EmailToken" not in s:
        add.append("from app.models.email_token import EmailToken")
    if add:
        s = s + ("\n" if not s.endswith("\n") else "") + "\n".join(add) + "\n"
        f.seek(0), f.truncate(), f.write(s)
PY

# 3) Патч модели User: phone + is_phone_verified
python3 - <<'PY'
import os, re
p = "app/models/user.py"
if not os.path.exists(p):
    raise SystemExit("Ожидалась модель app/models/user.py — проверь структуру проекта.")
with open(p, "r", encoding="utf-8") as f:
    s = f.read()

# Добавим столбцы, если их нет
if "phone" not in s:
    s = s.replace(")", ")\n    phone = Column(String(32), unique=True, index=True, nullable=False)\n    is_phone_verified = Column(Boolean, default=False)\n", 1) \
         .replace("from sqlalchemy import", "from sqlalchemy import") \
         .replace("Boolean", "Boolean")

# Убедимся, что Boolean импортирован
if "Boolean" not in s:
    s = s.replace("from sqlalchemy import Column, Integer, String", "from sqlalchemy import Column, Integer, String, Boolean")

# extend_existing
if '__table_args__' not in s:
    s = s.replace("class User(Base):", "class User(Base):\n    __table_args__ = {\"extend_existing\": True}")

with open(p, "w", encoding="utf-8") as f:
    f.write(s)
PY

# 4) Роуты: регистрация с телефоном, SMS-коды, просмотр последнего кода (dev)
cat > auth/routes/phone_sms.py <<'PY'
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, EmailStr, constr
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, SmsToken
from app.security import get_password_hash
from app.notifications.senders import send_sms, send_email
import secrets, time, re

router = APIRouter(prefix="/auth", tags=["auth"])

class RegisterPhoneReq(BaseModel):
    email: EmailStr
    phone: constr(min_length=5, max_length=32)
    password: constr(min_length=6)

class SmsRequest(BaseModel):
    phone: constr(min_length=5, max_length=32) | None = None
    email: EmailStr | None = None

class SmsVerify(BaseModel):
    phone: constr(min_length=5, max_length=32)
    code: constr(min_length=4, max_length=10)

def _gen_code() -> str:
    return f"{secrets.randbelow(1000000):06d}"

@router.post("/register")
def register_with_phone(data: RegisterPhoneReq, db: Session = Depends(get_db)):
    # уникальность
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(400, "Email уже зарегистрирован")
    if db.query(User).filter(User.phone == data.phone).first():
        raise HTTPException(400, "Телефон уже зарегистрирован")

    user = User(email=data.email, phone=data.phone, hashed_password=get_password_hash(data.password), is_phone_verified=False)
    db.add(user); db.commit(); db.refresh(user)

    code = _gen_code()
    db.add(SmsToken(phone=data.phone, code=code, created_at=int(time.time())))
    db.commit()

    send_sms(data.phone, f"Ваш код подтверждения: {code}")
    return {"status": "ok", "user_id": user.id, "phone_verification_required": True}

@router.post("/sms/request")
def sms_request(data: SmsRequest, db: Session = Depends(get_db)):
    # можно искать по email или по телефону
    user = None
    if data.phone:
        user = db.query(User).filter(User.phone == data.phone).first()
    elif data.email:
        user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(404, "Пользователь не найден")
    code = _gen_code()
    db.add(SmsToken(phone=user.phone, code=code, created_at=int(time.time())))
    db.commit()
    send_sms(user.phone, f"Ваш код подтверждения: {code}")
    return {"status": "ok"}

@router.post("/sms/verify")
def sms_verify(data: SmsVerify, db: Session = Depends(get_db)):
    token = db.query(SmsToken).filter(SmsToken.phone == data.phone, SmsToken.code == data.code).order_by(SmsToken.id.desc()).first()
    if not token:
        raise HTTPException(400, "Неверный код")
    user = db.query(User).filter(User.phone == data.phone).first()
    if not user:
        raise HTTPException(404, "Пользователь не найден")
    user.is_phone_verified = True
    db.commit()
    return {"status": "verified"}

# Dev-вспомогательный эндпоинт (удалить в prod): получить последний SMS-код
@router.get("/sms/debug/last-code")
def sms_last_code(phone: str = Query(...), db: Session = Depends(get_db)):
    token = db.query(SmsToken).filter(SmsToken.phone == phone).order_by(SmsToken.id.desc()).first()
    if not token:
        raise HTTPException(404, "Код не найден")
    return {"phone": phone, "code": token.code}
PY

# 5) Reset-password с «крестовыми» уведомлениями
cat > auth/routes/reset_password.py <<'PY'
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr, constr
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, EmailToken
from app.notifications.senders import send_sms, send_email
from app.security import get_password_hash
import secrets, time

router = APIRouter(prefix="/auth/reset-password", tags=["auth"])

class ResetRequest(BaseModel):
    email: EmailStr | None = None
    phone: constr(min_length=5, max_length=32) | None = None

class ResetConfirm(BaseModel):
    token: str
    new_password: constr(min_length=6)

@router.post("/request")
def request_reset(data: ResetRequest, db: Session = Depends(get_db)):
    if not data.email and not data.phone:
        raise HTTPException(400, "Нужно указать email или телефон")

    user = None
    if data.email:
        user = db.query(User).filter(User.email == data.email).first()
    elif data.phone:
        user = db.query(User).filter(User.phone == data.phone).first()

    if not user:
        raise HTTPException(404, "Пользователь не найден")

    token_value = secrets.token_urlsafe(24)
    entry = EmailToken(email=user.email, token=token_value, created_at=int(time.time()))
    db.add(entry); db.commit()

    # Крестовые уведомления:
    if data.phone:
        # запрос по телефону → уведомление на email
        send_email(user.email, "Сброс пароля", f"Инициирован сброс пароля по телефону {user.phone}. Токен: {token_value}")
    if data.email:
        # запрос по email → уведомление на SMS
        if not user.phone:
            raise HTTPException(400, "У пользователя не указан телефон")
        send_sms(user.phone, "Инициирован сброс пароля по email. Проверьте почту.")
    return {"status": "ok", "reset_token": token_value}

@router.post("/confirm")
def confirm_reset(data: ResetConfirm, db: Session = Depends(get_db)):
    token = db.query(EmailToken).filter(EmailToken.token == data.token).first()
    if not token:
        raise HTTPException(400, "Неверный или просроченный токен")
    user = db.query(User).filter(User.email == token.email).first()
    if not user:
        raise HTTPException(404, "Пользователь не найден")
    user.hashed_password = get_password_hash(data.new_password)
    db.delete(token)
    db.commit()
    return {"status": "Пароль обновлён"}
PY

# 6) Подключаем роуты в app/main.py
if ! grep -q "from auth.routes import phone_sms" app/main.py 2>/dev/null; then
  sed -i '1i from auth.routes import phone_sms' app/main.py
  sed -i '/app = .*FastAPI.*/a app.include_router(phone_sms.router)' app/main.py
fi
if ! grep -q "from auth.routes import reset_password" app/main.py 2>/dev/null; then
  sed -i '1i from auth.routes import reset_password' app/main.py
  sed -i '/app = .*FastAPI.*/a app.include_router(reset_password.router)' app/main.py
fi

# 7) Миграция схемы (create_all)
python3 - <<'PY'
from app.database import Base, engine
from app.models import User, EmailToken, SmsToken  # noqa: F401
Base.metadata.create_all(bind=engine)
print("DB schema synced")
PY

# 8) Перезапуск Uvicorn
pkill -f uvicorn || true
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > uvicorn.out 2>&1 &
sleep 1
echo "=== Телефон/SMS + reset-password с крестовыми уведомлениями установлены. ==="
echo "Логи уведомлений: ~/legal-ai/logs/notifications.log"
