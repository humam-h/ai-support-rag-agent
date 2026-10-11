from app.classifier import disposition_for_capability


def test_available_capability_is_answered():
    status = disposition_for_capability(
        "provide_guidance"
    )

    assert status == "answered"


def test_password_reset_requires_human():
    status = disposition_for_capability(
        "reset_password"
    )

    assert status == "needs_human_action"


def test_unlock_account_requires_human():
    status = disposition_for_capability(
        "unlock_account"
    )

    assert status == "needs_human_action"


def test_modify_mfa_requires_human():
    status = disposition_for_capability(
        "modify_mfa"
    )

    assert status == "needs_human_action"
