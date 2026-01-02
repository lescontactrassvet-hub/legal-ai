from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import hashlib

from app.config import get_settings
from app.db import get_db
from app.auth.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

settings = get_settings()

# JWT настройки
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


# ---------------- Пароли ---------------- #
def hash_password(password: str) -> str:
    """SHA-256 → bcrypt. Защита от лимита 72 байта bcrypt."""
    sha256 = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return pwd_context.hash(sha256)

def check_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля: SHA-256(plain) → verify(bcrypt-hash)."""
    sha256 = hashlib.sha256(plain_password.encode("utf-8")).hexdigest()
    return pwd_context.verify(sha256, hashed_password)



def get_password_policy() -> dict:
    """Политика паролей для фронтенда / клиентов API."""
    return {
        "min_length": 6,
        "max_length": 72,  # ограничение bcrypt
        "require_upper": True,
        "require_lower": True,
        "require_digit": True,
        "require_symbol": True,
        "note": "желательно избегать похожих символов вроде '0' и 'o'",
    }


# ---------------- JWT токены ---------------- #

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Создать JWT access-token."""
    to_encode = data.copy()
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=ALGORITHM,
    )
    return encoded_jwt


# ---------------- Текущий пользователь ---------------- #

def _decode_token(token: str) -> dict:
    """Внутренняя функция: декодировать JWT и вернуть payload."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Зависимость FastAPI: вернуть текущего пользователя по JWT.

    Используется в защищённых маршрутах (в т.ч. в legal_doc).
    """
    payload = _decode_token(token)
    username = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user: Optional[User] = (
        db.query(User).filter(User.username == username).first()
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


# ------------------- Login helpers (restored) -------------------
def authenticate_user(db: Session, username_or_email: str, password: str) -> Optional[User]:
    """Find user by username OR email OR phone, then verify password."""
    ident = (username_or_email or "").strip()
    if not ident:
        return None
    user = db.query(User).filter((User.username == ident) | (User.email == ident) | (User.phone == ident)).first()

    if user is None:
        return None
    if getattr(user, "is_active", True) is False:
        return None
    if not check_password(password, user.hashed_password):
        return None
    return user


def decode_access_token(token: str) -> dict:
    """Compatibility wrapper for routes.py (expects decode_access_token)."""
    return _decode_token(token)


 
