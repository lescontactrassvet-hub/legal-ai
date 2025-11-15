#!/usr/bin/env bash
set -e
APP="$HOME/legal-ai/backend/app"

echo "[1/3] Обновляю секцию JWT для единых настроек..."

cat > "$APP/security.py" <<'PY'
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def hash_password(p: str) -> str:
    return pwd_context.hash(p)

def create_access_token(subject: str) -> str:
    to_encode = {
        "sub": subject,
        "exp": datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    }
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return int(payload.get("sub"))
    except JWTError:
        return None
PY

echo "[2/3] Обновляю router profile для использования decode_access_token..."
cat > "$APP/routers/auth.py" <<'PY'
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.db import get_session
from app.models.user import User
from app.schemas.auth import UserCreate, UserLogin, UserOut
from app.security import hash_password, verify_password, create_access_token, decode_access_token

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.post("/register", response_model=UserOut)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_session)):
    exists = await db.execute(select(User).where(User.email == payload.email))
    if exists.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=payload.email, hashed_password=hash_password(payload.password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_session)):
    res = await db.execute(select(User).where(User.email == form_data.username))
    user = res.scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(subject=str(user.id))
    return {"access_token": token, "token_type": "bearer"}

@router.get("/profile", response_model=UserOut)
async def profile(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_session)):
    uid = decode_access_token(token)
    if not uid:
        raise HTTPException(status_code=401, detail="Invalid token")
    res = await db.execute(select(User).where(User.id == uid))
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/reset-password")
async def reset_password():
    return {"status": "todo", "detail": "Password reset flow will be implemented"}

@router.post("/2fa/enable")
async def enable_2fa():
    return {"status": "todo", "detail": "2FA enable flow will be implemented"}
PY

echo "[3/3] Перезапуск сервера..."
cd ~/legal-ai/backend
pkill -f "uvicorn app.main:app" 2>/dev/null || true
sleep 1
source ~/legal-ai/.venv/bin/activate
export PYTHONPATH="$PWD"
nohup python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --log-level info > uvicorn_live.log 2>&1 &
disown
sleep 3
curl -i http://127.0.0.1:8000/health
