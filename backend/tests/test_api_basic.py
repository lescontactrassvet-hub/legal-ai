from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    """Проверяем, что /health работает."""
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_auth_login_empty():
    """Проверяем, что /auth/login возвращает 422 при пустом теле."""
    r = client.post("/auth/login", json={})
    assert r.status_code in (400, 422)


def test_ai_ask_empty():
    """Проверяем, что /ai/ask отвечает 400 при пустом запросе."""
    r = client.post("/ai/ask", json={"query": ""})
    # В зависимости от логики может быть 400 или 422
    assert r.status_code in (400, 422)


def test_docs_templates_unauthorized():
    """Проверяем, что /docs/templates защищён и требует авторизации."""
    r = client.get("/docs/templates")
    assert r.status_code in (401, 403)
