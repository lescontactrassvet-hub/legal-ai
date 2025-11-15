#!/usr/bin/env bash
set -e
FILE="$HOME/legal-ai/backend/app/models/__init__.py"
if [ -f "$FILE" ]; then
  echo "# fixed init for models" > "$FILE"
  echo "from app.db import Base" >> "$FILE"
  echo "✅ Исправлено: $FILE"
else
  echo "⚠️ Файл $FILE не найден (возможно, не создавался — не критично)"
fi

# Перезапуск uvicorn
cd ~/legal-ai/backend
pkill -f "uvicorn app.main:app" 2>/dev/null || true
sleep 1
PYTHONPATH="$PWD" nohup python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 > uvicorn.out 2>&1 &
sleep 3
curl -i http://127.0.0.1:8000/health || tail -n 100 uvicorn.out
