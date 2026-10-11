from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_agent_endpoint_unknown_issue():
    response = client.post(
        "/tickets/agent",
        json={
            "subject": "Printer error 49",
            "description": (
                "My printer displays error 49 and will not print. "
                "What should I do?"
            ),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "insufficient_knowledge"
    assert data["iterations"] == 1
    assert "human review" in data["answer"].lower()


def test_agent_endpoint_known_vpn_issue():
    response = client.post(
        "/tickets/agent",
        json={
            "subject": "VPN hostname problem",
            "description": (
                "My VPN connects, but I cannot access internal "
                "servers by hostname. What should I check?"
            ),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "answered"
    assert data["iterations"] >= 1
    assert data["answer"]
