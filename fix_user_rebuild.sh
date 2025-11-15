#!/usr/bin/env bash
set -e
cd ~/legal-ai/backend/app/models

echo "🧩 Пересоздаю models/user.py..."
cat > user.py <<'PY'
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

# Проверим, что импорт проходит без ошибок
cd ~/legal-ai
export PYTHONPATH=$PWD/backend
source .venv/bin/activate
python3 - <<'PY'
import importlib
m = importlib.import_module("app.models.user")
print("✅ app.models.user импортируется успешно:", m)
PY
