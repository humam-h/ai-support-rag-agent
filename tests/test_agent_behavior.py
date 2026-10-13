from app.agent import run_agent


def test_known_vpn_issue_is_answered():
    result = run_agent(
    request_id="test-vpn-001",
    subject="VPN DNS problem",
    description=(
        "My VPN connects but internal hostnames "
        "do not resolve."
    ),
)
    

    assert result["status"] == "answered"
    assert result["iterations"] >= 1
    assert result["answer"]


def test_unknown_printer_issue_is_escalated():
    result = run_agent(
        request_id="test-agent-printer-001",
        subject="Printer error 49",
        description=(
            "My printer displays error 49 and will not print. "
            "What should I do?"
        ),
    )

    assert result["status"] == "needs_human_action"
    assert result["iterations"] == 1
    assert "Escalation #" in result["answer"]
    assert "human review" in result["answer"]

def test_unknown_printer_escalation_is_idempotent():
    request_id = "test-agent-printer-idempotent-001"

    first = run_agent(
        request_id=request_id,
        subject="Printer error 49",
        description=(
            "My printer displays error 49 and will not print."
        ),
    )

    second = run_agent(
        request_id=request_id,
        subject="Printer error 49",
        description=(
            "My printer displays error 49 and will not print."
        ),
    )

    assert first["status"] == "needs_human_action"
    assert second["status"] == "needs_human_action"
    assert first["answer"] == second["answer"]