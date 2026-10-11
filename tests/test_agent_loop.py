from types import SimpleNamespace

from app.agent import run_agent


class FakeResponses:
    def create(self, **kwargs):
        function_call = SimpleNamespace(
            type="function_call",
            name="search_knowledge",
            arguments="{}",
            call_id="fake-call-id",
        )

        return SimpleNamespace(
            output=[function_call],
            output_text="",
        )


class FakeClient:
    def __init__(self):
        self.responses = FakeResponses()


def test_agent_stops_at_max_iterations(monkeypatch):
    fake_client = FakeClient()

    fake_tool_result = {
        "query": "test query",
        "results": [
            {
                "source": "test.md",
                "chunk_index": 0,
                "text": "Fake relevant knowledge.",
                "score": 0.9,
            }
        ],
    }

    monkeypatch.setattr(
        "app.agent.execute_tool",
        lambda name, arguments, original_query: fake_tool_result,
    )

    result = run_agent(
        query="Test support request",
        max_iterations=3,
        model_client=fake_client,
    )

    assert result["status"] == "needs_human_action"
    assert result["iterations"] == 3
    assert "maximum" in result["answer"].lower()
