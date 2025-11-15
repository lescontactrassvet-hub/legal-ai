#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-$HOME/legal-ai}"
BACKEND_DIR="$PROJECT_ROOT/backend"
APP_DIR="$BACKEND_DIR/app"
REPORT_FILE="$BACKEND_DIR/auth_install_report.txt"

log() { echo "[$(date '+%F %T')] $*"; }
req() { command -v "$1" >/dev/null 2>&1 || { echo "ERROR: требуется $1"; exit 1; }; }

log "Старт установки модуля аутентификации (v2)"

# 0) Предусловия
req python
req pip
req curl

# 1) venv
if [ -d "$PROJECT_ROOT/.venv" ]; then
  . "$PROJECT_ROOT/.venv/bin/activate"
  log "Активирован venv: $PROJECT_ROOT/.venv"
else
  log "Создаю venv..."
  python -m venv "$PROJECT_ROOT/.venv"
  . "$PROJECT_ROOT/.venv/bin/activate"
fi

python -V
pip -V

# 2) Обновим базовые инструменты
pip install --upgrade pip setuptools wheel

# 3) Устанавливаем все зависимости одной командой (быстро и без проверок)
log "Устанавливаю зависимости..."
pip install --upgrade \
  fastapi==0.119.1 \
  uvicorn==0.38.0 \
  "pydantic>=2" \
  email-validator \
  sqlalchemy \
  aiosqlite \
  python-dotenv \
  "passlib[bcrypt]==1.7.4" \
  "bcrypt==5.0.0" \
  "python-jose[cryptography]" \
  pyotp \
  httpx

# 4) Структура проекта
mkdir -p "$APP_DIR/core" "$APP_DIR/models" "$APP_DIR/routers" "$APP_DIR/schemas"

# 5) Конфиг
cat > "$APP_DIR/core/config.py" <<'PY'
from pydantic import BaseModel
import os

class Settings(BaseModel):
    app_name: str = "LegalAI"
    secret_key: str = os.getenv("SECRET_KEY", "CHANGE_ME_SUPER_SECRET")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MIN", "60"))
    algorithm: str = "HS256"
    sqlite_url: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./legalai.db")

settings = Settings()
PY

# 6) DB / ORM
cat > "$APP_DIR/db.py" <<'PY'
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

engine = create_async_engine(settings.sqlite_url, echo=False, future=True)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()

async def get_session():
    async with AsyncSessionLocal() as session:
        yield session
PY

# 7) Модель
cat > "$APP_DIR/models/user.py" <<'PY'
from sqlalchemy import String, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(256), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(256), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
PY

# 8) Схемы
cat > "$APP_DIR/schemas/auth.py" <<'PY'
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    class Config:
        from_attributes = True
PY

# 9) Безопасность / JWT
cat > "$APP_DIR/security.py" <<'PY'
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def hash_password(p: str) -> str:
    return pwd_context.hash(p)

def create_access_token(subject: str) -> str:
    to_encode = {"sub": subject, "exp": datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)}
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
PY

# 10) Роуты
cat > "$APP_DIR/routers/auth.py" <<'PY'
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.db import get_session
from app.models.user import User
from app.schemas.auth import UserCreate, UserLogin, UserOut
from app.security import hash_password, verify_password, create_access_token

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
    from jose import jwt, JWTError
    from app.core.config import settings
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        uid = int(payload.get("sub"))
    except JWTError:
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

# 11) main.py
cat > "$APP_DIR/main.py" <<'PY'
from fastapi import FastAPI
from app.db import Base, engine
from app.routers import auth
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="LegalAI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"]
)

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/health")
async def health():
    return {"status": "ok"}

app.include_router(auth.router)
PY

# 12) __init__
echo "# app package" > "$APP_DIR/__init__.py"
echo "# routers package" > "$APP_DIR/routers/__init__.py"

# 13) Запуск uvicorn в фоне + health-check
pkill -f "uvicorn app.main:app" 2>/dev/null || true
sleep 1

cd "$BACKEND_DIR"
# Важно: PYTHONPATH, чтобы модуль app корректно импортировался
PYTHONPATH="$BACKEND_DIR" nohup python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 > uvicorn.out 2>&1 &
sleep 3

STATUS="$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/health || true)"
echo "Health HTTP: $STATUS"
if [ "$STATUS" != "200" ]; then
  echo "---- uvicorn.out (последние строки) ----"
  tail -n 200 uvicorn.out || true
  echo "Сервер не прошёл health-check" | tee "$REPORT_FILE"
  exit 1
fi

# 14) Отчёт
{
  echo "=== LegalAI Auth Installer Report ==="
  date '+%F %T'
  echo "Server: http://127.0.0.1:8000"
  echo "Health: $STATUS"
  echo "Endpoints:"
  echo "  GET  /health"
  echo "  POST /auth/register"
  echo "  POST /auth/login (OAuth2PasswordRequestForm: username=email, password=...)"
  echo "  GET  /auth/profile (Authorization: Bearer <token>)"
  echo "  POST /auth/reset-password (todo)"
  echo "  POST /auth/2fa/enable (todo)"
} > "$REPORT_FILE"

log "Готово. Отчёт: $REPORT_FILE"
