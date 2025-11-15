from fastapi.testclient import TestClient
from backend.main import app  # важно: backend.main, не app.main

client = TestClient(app)


def test_health_status_code():
    resp = client.get("/health")
    assert resp.status_code == 200


def test_health_payload():
    resp = client.get("/health")
    data = resp.json()
    assert isinstance(data, dict)

    # допускаем варианты ("ok", "OK", "healthy")
    status = str(data.get("status", "")).lower()
    assert status in {"ok", "healthy"}
