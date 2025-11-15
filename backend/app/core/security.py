# SPDX-FileCopyrightText: © Береску Николае
# SPDX-License-Identifier: Proprietary

from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Хэширует пароль с защитой от ValueError и длины >72 байт"""
    try:
        if len(password.encode("utf-8")) > 72:
            password = password.encode("utf-8")[:72].decode("utf-8", errors="ignore")
        return pwd_context.hash(password)
    except Exception as e:
        raise ValueError(f"Hashing failed: {type(e).__name__} {e}")

def verify_password(plain: str, hashed: str) -> bool:
    """Проверяет пароль (до 72 байт)"""
    try:
        if len(plain.encode("utf-8")) > 72:
            plain = plain.encode("utf-8")[:72].decode("utf-8", errors="ignore")
        return pwd_context.verify(plain, hashed)
    except Exception:
        return False

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(hours=1))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALG)
