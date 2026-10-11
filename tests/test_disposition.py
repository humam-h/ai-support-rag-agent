from app.classifier import determine_disposition


def test_guidance_request_is_answered():
    result = determine_disposition(
        "How do I troubleshoot repeated account lockouts?"
    )

    assert result["required_capability"] == "provide_guidance"
    assert result["status"] == "answered"


def test_password_reset_requires_human_action():
    result = determine_disposition(
        "Please reset my password."
    )

    assert result["required_capability"] == "reset_password"
    assert result["status"] == "needs_human_action"


def test_unlock_requires_human_action():
    result = determine_disposition(
        "My account is locked. Please unlock it."
    )

    assert result["required_capability"] == "unlock_account"
    assert result["status"] == "needs_human_action"
