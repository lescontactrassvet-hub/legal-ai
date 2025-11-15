# SPDX-FileCopyrightText: © Береску Николае
# SPDX-License-Identifier: Proprietary
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy import exc as sa_exc
from datetime import datetime, timezone
import pyotp

from app.database.session import SessionLocal
from app.models.user import User
from app.models.device import Device
from app.schemas.auth import UserRegister, UserLogin, TokenPair
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter()

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@router.post("/register", response_model=TokenPair)
def register(data: UserRegister, db: Session = Depends(get_db)):
    # Явно проверим дубликат
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    try:
        user = User(email=data.email, password_hash=hash_password(data.password))
        db.add(user)
        db.commit()
        db.refresh(user)
    except sa_exc.IntegrityError:
        db.rollback()
        # На случай гонок/уникальных ограничений
        raise HTTPException(status_code=400, detail="Email already registered")
    except Exception as e:
        db.rollback()
        # Отдадим понятное сообщение вместо 500
        raise HTTPException(status_code=400, detail=f"Register failed: {type(e).__name__}")
    token = create_access_token({"sub": str(user.id)})
    return TokenPair(access_token=token)

@router.post("/login", response_model=TokenPair)
def login(
    data: UserLogin,
    db: Session = Depends(get_db),
    x_device_id: str = Header(None, alias="X-Device-Id"),
    user_agent: str = Header("", alias="User-Agent"),
    totp_code: str | None = None,
):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Если включена 2FA — требуем корректный TOTP
    if getattr(user, "is_2fa_enabled", False):
        if not totp_code or not user.totp_secret:
            raise HTTPException(status_code=401, detail="TOTP required")
        totp = pyotp.TOTP(user.totp_secret, digits=6, interval=30)
        if not totp.verify(totp_code, valid_window=1):
            raise HTTPException(status_code=401, detail="Invalid TOTP code")

    if not x_device_id:
        raise HTTPException(status_code=400, detail="Missing X-Device-Id")
    devices = db.query(Device).filter(Device.user_id == user.id).all()
    existing = next((d for d in devices if d.device_id == x_device_id), None)
    if not existing:
        if len(devices) >= 2:
            raise HTTPException(status_code=403, detail="DEVICE_LIMIT_REACHED: only 2 devices allowed")
        new_dev = Device(user_id=user.id, device_id=x_device_id, ua=user_agent)
        db.add(new_dev); db.commit(); db.refresh(new_dev)
    else:
        existing.last_seen_at = datetime.now(timezone.utc)
        db.commit()

    token = create_access_token({"sub": str(user.id), "device": x_device_id})
    return TokenPair(access_token=token)
