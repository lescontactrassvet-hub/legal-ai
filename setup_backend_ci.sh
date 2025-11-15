#!/usr/bin/env bash
set -euo pipefail

cd /srv/legal-ai

echo "[1/3] Обновляю backend/requirements.txt..."
cat > backend/requirements.txt << 'REQEOF'
fastapi==0.119.1
uvicorn==0.38.0

sqlalchemy>=2.0.0
aiosqlite>=0.19.0
python-dotenv>=1.0.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
pyotp>=2.9.0
httpx>=0.27.0

pydantic>=2.0.0
pydantic-settings>=2.0.0
email-validator>=2.0.0

python-docx>=1.1.0
reportlab>=4.0.0
REQEOF


echo "[2/3] Создаю минимальные тесты backend..."
mkdir -p backend/tests

cat > backend/tests/test_health.py << 'PYEOF'
import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_health_ok():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
PYEOF


echo "[3/3] Создаю GitHub Actions workflow для тестов backend..."
mkdir -p .github/workflows

cat > .github/workflows/backend-tests.yml << 'YAMLEOF'
name: Backend tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: backend

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run tests
        run: |
          pytest -q
YAMLEOF

echo
echo "✅ Файлы для backend CI созданы:"
echo "  - backend/requirements.txt"
echo "  - backend/tests/test_health.py"
echo "  - .github/workflows/backend-tests.yml"
echo
echo "Теперь можно сделать:"
echo "  cd /srv/legal-ai"
echo "  git status"
echo "  git add backend/requirements.txt backend/tests/test_health.py .github/workflows/backend-tests.yml"
echo "  git commit -m 'Add backend tests and CI workflow; sync working backend'"
echo "  git push"
