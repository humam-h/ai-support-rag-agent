from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_readiness_when_application_is_ready(monkeypatch):
    def fake_readiness():
        return {
            "database": "ready",
            "knowledge_chunks": 6,
            "knowledge_ready": True,
        }

    monkeypatch.setattr(
        "app.main.check_database_readiness",
        fake_readiness,
    )

    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "database": "ready",
        "knowledge_chunks": 6,
        "knowledge_ready": True,
    }
def test_readiness_when_knowledge_base_is_empty(monkeypatch):
    def fake_readiness():
        return {
            "database": "ready",
            "knowledge_chunks": 0,
            "knowledge_ready": False,
        }

    monkeypatch.setattr(
        "app.main.check_database_readiness",
        fake_readiness,
    )

    response = client.get("/ready")

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Knowledge base is not ready."
    }


def test_readiness_when_database_is_unavailable(monkeypatch):
    def fake_readiness():
        raise RuntimeError("database unavailable")

    monkeypatch.setattr(
        "app.main.check_database_readiness",
        fake_readiness,
    )

    response = client.get("/ready")

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Database is not ready."
    }