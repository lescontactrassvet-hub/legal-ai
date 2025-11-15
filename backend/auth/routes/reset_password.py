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
