from app.tools import search_knowledge_tool


def test_search_knowledge_tool():
    result = search_knowledge_tool(
        "My VPN connects but internal hostnames do not work."
    )

    assert result["query"]
    assert len(result["results"]) > 0
    assert result["results"][0]["source"] == "vpn-troubleshooting.md"
