from app.agent import run_agent, _complete_agent_request


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
    assert result["escalation"] is not None
    assert result["escalation"]["id"] is not None
    assert result["escalation"]["status"] == "open"
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

    assert first["escalation"] is not None
    assert second["escalation"] is not None

    assert (
        first["escalation"]["id"]
        == second["escalation"]["id"]
    )

    assert first["escalation"]["status"] == "open"
    assert second["escalation"]["status"] == "open"

def test_escalation_failure_does_not_claim_success(
    monkeypatch,
):
    def failing_create_escalation_tool(**kwargs):
        raise RuntimeError("Database unavailable")

    monkeypatch.setattr(
        "app.agent.create_escalation_tool",
        failing_create_escalation_tool,
    )

    result = run_agent(
        request_id="test-escalation-failure-001",
        subject="Printer error 49",
        description=(
            "My printer displays error 49 and will not print."
        ),
    )

    assert result["status"] == "needs_human_action"
    assert result["escalation"] is None

    assert "human review" in result["answer"].lower()
    assert (
    "an escalation was created"
    not in result["answer"].lower()
)
    assert (
    "could not be created"
    in result["answer"].lower()
)
def test_successful_escalation_records_audit_event(
    monkeypatch,
):
    audit_calls = []

    def fake_record_audit_event(**kwargs):
        audit_calls.append(kwargs)
        return True

    monkeypatch.setattr(
        "app.agent.record_audit_event",
        fake_record_audit_event,
    )

    result = run_agent(
        request_id="test-audit-success-001",
        subject="Printer error 49",
        description=(
            "My printer displays error 49 and will not print."
        ),
    )

    assert result["action_status"] == "escalation_created"

    assert len(audit_calls) == 1

    event = audit_calls[0]

    assert event["request_id"] == "test-audit-success-001"
    assert event["event_type"] == "escalation_creation"
    assert event["outcome"] == "success"

    assert (
        event["details"]["escalation_id"]
        == result["escalation"]["id"]
    ) 
def test_audit_failure_does_not_change_escalation_success(
    monkeypatch,
):
    def failing_record_audit_event(**kwargs):
        return False

    monkeypatch.setattr(
        "app.agent.record_audit_event",
        failing_record_audit_event,
    )

    result = run_agent(
        request_id="test-agent-audit-failure-001",
        subject="Printer error 49",
        description=(
            "My printer displays error 49 and will not print."
        ),
    )

    assert result["status"] == "needs_human_action"
    assert result["action_status"] == "escalation_created"

    assert result["escalation"] is not None
    assert result["escalation"]["id"] is not None
    assert result["escalation"]["status"] == "open"

    assert (
        "an escalation was created"
        in result["answer"].lower()
    )
def test_agent_logs_request_completion(caplog):
    result = {
        "status": "answered",
        "answer": "Test answer",
        "iterations": 2,
    }

    with caplog.at_level("INFO", logger="app.agent"):
        returned = _complete_agent_request(
            "logging-test-123",
            result,
        )

    assert returned == result

    assert (
        "Agent request completed "
        "request_id=logging-test-123 "
        "status=answered "
        "action_status=none "
        "iterations=2"
    ) in caplog.text
    