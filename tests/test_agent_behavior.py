from app.agent import run_agent


def test_known_vpn_issue_is_answered():
    result = run_agent(
        "My VPN connects, but I cannot access "
        "internal servers by hostname. What should I check?"
    )

    assert result["status"] == "answered"
    assert result["iterations"] >= 1
    assert result["answer"]


def test_unknown_printer_issue_is_insufficient_knowledge():
    result = run_agent(
        "My printer displays error 49 and will not print. "
        "What should I do?"
    )

    assert result["status"] == "insufficient_knowledge"
    assert result["iterations"] == 1
    assert "human review" in result["answer"].lower()
