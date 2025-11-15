#!/usr/bin/env bash
cd ~/legal-ai/backend/app
echo "🔍 Исправляем импорты app.db → app.database..."
grep -rl "app.db" . | while read -r f; do
  echo "   → $f"
  sed -i 's|app\.db|app.database|g' "$f"
done

echo "✅ Замены завершены. Проверим импорт моделей..."
cd ~/legal-ai
export PYTHONPATH=$PWD/backend
source .venv/bin/activate
python3 - <<'PY'
import importlib
m = importlib.import_module("app.models")
print("✅ app.models импортируется успешно:", m)
PY
