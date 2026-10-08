import httpx2 as httpx
from openai import APIConnectionError, APIStatusError

from jobfit.errors import friendly_error

REQUEST = httpx.Request("POST", "http://localhost/v1/chat/completions")


def status_error(code: int) -> APIStatusError:
    return APIStatusError("boom", response=httpx.Response(code, request=REQUEST), body=None)


def test_overloaded_model_message():
    assert "overloaded" in friendly_error(status_error(503))


def test_bad_key_and_missing_model_messages():
    assert "API key was rejected" in friendly_error(status_error(401))
    assert "Change LLM_MODEL" in friendly_error(status_error(404))
    assert "Rate limit" in friendly_error(status_error(429))


def test_connection_error_message():
    assert "internet connection" in friendly_error(APIConnectionError(request=REQUEST))


def test_other_errors_pass_through():
    assert friendly_error(ValueError("bad JSON")) == "bad JSON"
