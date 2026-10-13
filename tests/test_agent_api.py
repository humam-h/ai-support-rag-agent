from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_agent_endpoint_unknown_issue():
    response = client.post(
        "/tickets/agent",
        json={
            "request_id": "test-api-printer-001",
            "subject": "Printer error 49",
            "description": (
                "My printer displays error 49 and will not print. "
                "What should I do?"
            ),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "needs_human_action"
    assert data["iterations"] == 1
    assert "Escalation #" in data["answer"]
    assert "human review" in data["answer"]


def test_agent_endpoint_known_vpn_issue():
    response = client.post(
        "/tickets/agent",
        json={
            "request_id": "test-vpn-001",
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
