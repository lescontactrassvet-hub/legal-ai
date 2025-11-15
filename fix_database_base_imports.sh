#!/usr/bin/env bash
cd ~/legal-ai/backend/app
echo "🔧 Исправляем 'from app.database.base import Base' → 'from app.database import Base'..."
grep -rl "from app.database.base import Base" models | while read -r f; do
  echo "   → $f"
  sed -i 's|from app\.database\.base import Base|from app.database import Base|g' "$f"
done

echo "✅ Проверяем импорт моделей..."
cd ~/legal-ai
export PYTHONPATH=$PWD/backend
source .venv/bin/activate
python3 - <<'PY'
import importlib
m = importlib.import_module("app.models")
print("✅ app.models импортируется успешно:", m)
PY
