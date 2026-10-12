from app.escalations import create_escalation


def test_create_escalation_is_idempotent():
    key = "test-printer-error-49"

    first = create_escalation(
        subject="Printer error 49",
        description=(
            "Printer displays error 49 and will not print."
        ),
        reason=(
            "No sufficiently relevant knowledge-base "
            "information was found."
        ),
        idempotency_key=key,
    )

    second = create_escalation(
        subject="Printer error 49",
        description=(
            "Printer displays error 49 and will not print."
        ),
        reason=(
            "No sufficiently relevant knowledge-base "
            "information was found."
        ),
        idempotency_key=key,
    )

    assert first["id"] == second["id"]
    assert first["idempotency_key"] == key
    assert second["idempotency_key"] == key
    assert first["status"] == "open"