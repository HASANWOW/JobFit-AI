"""Headless UI tests with Streamlit's AppTest (no browser, no API calls)."""

from streamlit.testing.v1 import AppTest


def run_app(monkeypatch, cv: str = "", job: str = "", button: int | None = None) -> AppTest:
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    # Keep a developer's real .env from leaking into the test run
    monkeypatch.setattr("dotenv.load_dotenv", lambda *a, **k: False)
    at = AppTest.from_file("../app.py", default_timeout=30).run()
    at.text_area[0].set_value(cv)
    at.text_area[1].set_value(job)
    if button is not None:
        at.button[button].click()
    return at.run()


def test_page_renders(monkeypatch):
    at = run_app(monkeypatch)
    assert not at.exception
    assert at.title[0].value.endswith("JobFit AI")


def test_asks_for_both_inputs(monkeypatch):
    at = run_app(monkeypatch, cv="Python", job="", button=0)
    assert "Add both your CV and the job posting" in at.warning[0].value


def test_missing_api_key_shows_clear_error(monkeypatch):
    at = run_app(monkeypatch, cv="Python, PyTorch", job="AI Engineer intern", button=0)
    assert not at.exception
    assert "No API key" in at.error[0].value
