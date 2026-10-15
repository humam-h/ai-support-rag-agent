from app.audit import (
    create_audit_event,
    record_audit_event,
)


def test_create_audit_event():
    event = create_audit_event(
        request_id="test-audit-001",
        event_type="escalation_creation",
        outcome="success",
        details={
            "escalation_id": 123,
        },
    )

    assert event["id"] is not None
    assert event["request_id"] == "test-audit-001"
    assert event["event_type"] == "escalation_creation"
    assert event["outcome"] == "success"
    assert event["details"] == {
        "escalation_id": 123,
    }
    assert event["created_at"] is not None
def test_record_audit_event_handles_failure(
    monkeypatch,
):
    def failing_create_audit_event(**kwargs):
        raise RuntimeError("Audit database unavailable")

    monkeypatch.setattr(
        "app.audit.create_audit_event",
        failing_create_audit_event,
    )

    recorded = record_audit_event(
        request_id="test-audit-failure-001",
        event_type="escalation_creation",
        outcome="success",
        details={
            "escalation_id": 123,
        },
    )

    assert recorded is False