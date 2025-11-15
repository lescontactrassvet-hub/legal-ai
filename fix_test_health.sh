#!/bin/bash
set -e

echo "=== Fix test_health.py for GitHub Actions ==="

# Переходим в корень репозитория
cd "$(dirname "$0")"

# Перезаписываем backend/tests/test_health.py
cat > backend/tests/test_health.py << 'PYCODE'
import pathlib
import sys

# Добавляем корень репозитория в sys.path,
# чтобы импорт "backend.main" работал и локально, и в GitHub Actions.
ROOT_DIR = pathlib.Path(__file__).resolve().parents[2]
ROOT_STR = str(ROOT_DIR)
if ROOT_STR not in sys.path:
    sys.path.insert(0, ROOT_STR)

from fastapi.testclient import TestClient
from backend.main import app  # импорт FastAPI-приложения

client = TestClient(app)


def test_health_status_code():
    resp = client.get("/health")
    assert resp.status_code == 200


def test_health_payload():
    resp = client.get("/health")
    data = resp.json()
    assert isinstance(data, dict)
    status = str(data.get("status", "")).lower()
    assert status in {"ok", "healthy"}
PYCODE

echo "[+] backend/tests/test_health.py rewritten."

# Добавляем в git
git add backend/tests/test_health.py

echo "[+] Commit changes..."
git commit -m "Fix test_health imports for CI" || echo "[i] Nothing to commit."

echo "[+] Push to GitHub..."
git push

echo "=== DONE ==="
echo "Теперь открой GitHub → Actions → Backend tests и посмотри последний запуск."
