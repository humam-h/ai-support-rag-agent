import pytest

from app.agent import execute_tool


def test_execute_search_knowledge_tool():
    result = execute_tool(
        "search_knowledge",
        {},
        original_query=(
            "My VPN connects but internal "
            "hostnames do not work."
        ),
    )

    assert len(result["results"]) > 0
    assert (
        result["results"][0]["source"]
        == "vpn-troubleshooting.md"
    )


def test_unknown_tool_is_rejected():
    with pytest.raises(
        ValueError,
        match="Unknown tool",
    ):
        execute_tool(
            "reset_password",
            {},
            original_query="Please reset my password.",
        )