import pytest

from jobfit.llm import JobFitClient, LLMConfig

GOOD = '{"match_score": 70, "summary": "Decent fit."}'


class FakeClient(JobFitClient):
    """JobFitClient with the network call replaced by scripted replies."""

    def __init__(self, replies: list[str]):
        self.config = LLMConfig(api_key="test", base_url="http://localhost", model="fake")
        self.replies = list(replies)
        self.calls: list[str] = []

    def _chat(self, system, user, *, json_mode=False, temperature=0.2):
        self.calls.append(user)
        return self.replies.pop(0)


def test_analyze_returns_report():
    client = FakeClient([GOOD])
    assert client.analyze("cv", "job").match_score == 70
    assert len(client.calls) == 1


def test_analyze_repairs_one_bad_reply():
    client = FakeClient(["not json at all", GOOD])
    report = client.analyze("cv", "job")
    assert report.summary == "Decent fit."
    assert "previous reply was invalid" in client.calls[1]


def test_analyze_gives_up_after_second_bad_reply():
    client = FakeClient(["nope", "still nope"])
    with pytest.raises(ValueError):
        client.analyze("cv", "job")


def test_missing_api_key_is_a_clear_error():
    with pytest.raises(ValueError, match="No API key"):
        JobFitClient(LLMConfig(api_key="", base_url="http://localhost", model="x"))


def test_long_inputs_are_trimmed():
    client = FakeClient([GOOD])
    client.analyze("x" * 50_000, "job")
    assert len(client.calls[0]) < 20_000
