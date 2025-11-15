#!/usr/bin/env bash
set -euo pipefail

cd "$HOME/legal-ai/backend"

# 1) Гасим старые uvicorn
pkill -f "uvicorn app.main:app" 2>/dev/null || true

# 2) Покажем хвост предыдущего лога (на всякий случай)
echo "---- tail uvicorn.out (последние 80 строк) ----"
tail -n 80 uvicorn.out 2>/dev/null || echo "(нет файла)"

# 3) Проверка PYTHONPATH и импорта приложения
export PYTHONPATH="$PWD"
echo "PYTHONPATH=$PYTHONPATH"
python - <<'PY' || { echo "❌ import app.main провалился"; exit 1; }
import sys
print("sys.path[0:3] =", sys.path[0:3])
try:
    import app.main as m
    print("✅ import app.main ОК, app =", m.app)
except Exception as e:
    print("❌ Ошибка импорта app.main:", repr(e))
    raise
PY

# 4) Запуск uvicorn в фореграунде с подробным логом
echo "---- RUN UVICORN (foreground, Ctrl+C чтобы остановить) ----"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --log-level debug
