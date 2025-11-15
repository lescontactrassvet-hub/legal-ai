#!/usr/bin/env bash
set -e
cd ~/legal-ai/backend/app

# 1) Проверим файл user.py
if [ ! -f models/user.py ]; then
  echo "❌ models/user.py отсутствует — создаю..."
  mkdir -p models
  cat > models/user.py <<'PY'
from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base

class User(Base):
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_phone_verified = Column(Boolean, default=False)
PY
fi

# 2) Гарантируем, что user импортируется в __init__.py
if ! grep -q "from app.models.user import User" models/__init__.py 2>/dev/null; then
  echo "Добавляю импорт User в models/__init__.py"
  echo "from app.models.user import User" >> models/__init__.py
fi

# 3) Проверим импорт пакета моделей
cd ~/legal-ai
export PYTHONPATH=$PWD/backend
source .venv/bin/activate
python3 - <<'PY'
import importlib
m = importlib.import_module("app.models")
print("✅ app.models импортируется успешно:", m)
PY
