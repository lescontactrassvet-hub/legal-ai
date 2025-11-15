#!/usr/bin/env bash
cd ~/legal-ai/backend/app/models

# 1️⃣ Проверяем и исправляем синтаксис класса User
if grep -q "class User(Base)" user.py; then
  echo "🔧 Исправляю строку объявления класса User..."
  sed -i 's|class User(Base)|class User(Base):|' user.py
fi

# 2️⃣ Проверяем, что файл читается без ошибок
cd ~/legal-ai
export PYTHONPATH=$PWD/backend
source .venv/bin/activate
python3 - <<'PY'
import importlib
m = importlib.import_module("app.models.user")
print("✅ app.models.user импортируется успешно:", m)
PY
