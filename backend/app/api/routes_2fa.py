# SPDX-FileCopyrightText: © Береску Николае
# SPDX-License-Identifier: Proprietary
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from io import BytesIO
import base64, pyotp

try:
    import qrcode
    QR_OK = True
except Exception:
    QR_OK = False

from app.database.session import SessionLocal
from app.models.user import User

router = APIRouter()

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@router.post("/setup")
def setup_2fa(user_id: int = 1, issuer: str = "LegalAI", db: Session = Depends(get_db)):
    """
    Генерирует секрет (TOTP RFC-6238).
    Совместимо с Google Authenticator / Яндекс.Аутентификатор / Authy.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    secret = pyotp.random_base32()  # 16/32 chars, SHA1, 30s, 6 digits по умолчанию
    user.totp_secret = secret
    user.is_2fa_enabled = False
    db.commit()

    # otpauth URI для любых TOTP-приложений
    uri = pyotp.totp.TOTP(secret, digits=6, interval=30).provisioning_uri(
        name=user.email, issuer_name=issuer
    )
    # Пытаемся вернуть QR (base64). Если qrcode нет — вернём только URI.
    payload = {"otpauth_uri": uri, "issuer": issuer, "digits": 6, "period": 30}
    if QR_OK:
        img = qrcode.make(uri)
        buf = BytesIO(); img.save(buf, format="PNG")
        payload["qr_base64"] = base64.b64encode(buf.getvalue()).decode()
    return payload

@router.post("/verify")
def verify_2fa(code: str, user_id: int = 1, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.totp_secret:
        raise HTTPException(status_code=400, detail="2FA not initialized")
    totp = pyotp.TOTP(user.totp_secret, digits=6, interval=30)
    if not totp.verify(code, valid_window=1):  # допускаем ±1 интервал
        raise HTTPException(status_code=400, detail="Invalid code")
    user.is_2fa_enabled = True
    db.commit()
    return {"detail": "2FA enabled"}

@router.post("/disable")
def disable_2fa(user_id: int = 1, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.totp_secret = None
    user.is_2fa_enabled = False
    db.commit()
    return {"detail": "2FA disabled"}
