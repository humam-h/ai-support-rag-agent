from app.agent import can_create_escalation


def test_escalation_allowed_after_empty_search():
    allowed = can_create_escalation(
        knowledge_searched=True,
        knowledge_found=False,
    )

    assert allowed is True


def test_escalation_rejected_when_knowledge_exists():
    allowed = can_create_escalation(
        knowledge_searched=True,
        knowledge_found=True,
    )

    assert allowed is False


def test_escalation_rejected_before_search():
    allowed = can_create_escalation(
        knowledge_searched=False,
        knowledge_found=False,
    )

    assert allowed is False
