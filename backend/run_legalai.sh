#!/usr/bin/env bash
set -euo pipefail

cd /srv/legal-ai/backend

# Определяем uvicorn
if [ -x "/srv/legal-ai/backend/.venv/bin/uvicorn" ]; then
  UVICORN="/srv/legal-ai/backend/.venv/bin/uvicorn"
elif command -v uvicorn >/dev/null 2>&1; then
  UVICORN="$(command -v uvicorn)"
else
  echo "ERROR: uvicorn not found ( ни в .venv, ни в системе )" >&2
  exit 1
fi

export PYTHONPATH="/srv/legal-ai/backend"

# Запускаем FastAPI
exec "$UVICORN" app.main:app --host 127.0.0.1 --port 8000
