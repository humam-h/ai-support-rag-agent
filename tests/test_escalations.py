from app.escalations import create_escalation


def test_create_escalation():
    escalation = create_escalation(
        subject="Printer error 49",
        description=(
            "Printer displays error 49 and will not print."
        ),
        reason=(
            "No sufficiently relevant knowledge-base "
            "information was found."
        ),
    )

    assert escalation["id"] is not None
    assert escalation["subject"] == "Printer error 49"
    assert escalation["status"] == "open"
    assert escalation["created_at"] is not None
