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
