from app.tools import search_knowledge_tool
from app.tools import (
    create_escalation_tool,
    search_knowledge_tool,
)

def test_create_escalation_tool():
    result = create_escalation_tool(
        subject="Test escalation",
        description="Test support request.",
        reason="Human review is required.",
    )

    assert result["id"] is not None
    assert result["subject"] == "Test escalation"
    assert result["status"] == "open"


def test_search_knowledge_tool():
    result = search_knowledge_tool(
        "My VPN connects but internal hostnames do not work."
    )

    assert result["query"]
    assert len(result["results"]) > 0
    assert result["results"][0]["source"] == "vpn-troubleshooting.md"
