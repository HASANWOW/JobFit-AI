import pytest

from jobfit.schema import FitReport, extract_json, parse_report

VALID = """{
  "match_score": 82,
  "summary": "Strong Python and ML background.",
  "matched_skills": ["Python", "Git"],
  "missing_skills": ["LLM"],
  "strengths": ["Real-time CV project"],
  "improvement_tips": ["Add an LLM project"],
  "interview_questions": ["Explain DeepPixBis"]
}"""


def test_parses_plain_json():
    report = parse_report(VALID)
    assert isinstance(report, FitReport)
    assert report.match_score == 82
    assert report.missing_skills == ["LLM"]


def test_parses_json_inside_code_fence_and_prose():
    reply = f"Here is the analysis:\n```json\n{VALID}\n```\nGood luck!"
    assert parse_report(reply).matched_skills == ["Python", "Git"]


def test_score_is_rounded_and_clamped():
    assert parse_report('{"match_score": "85.6", "summary": "ok"}').match_score == 86
    assert parse_report('{"match_score": 140, "summary": "ok"}').match_score == 100


def test_missing_lists_default_to_empty():
    report = parse_report('{"match_score": 50, "summary": "ok"}')
    assert report.strengths == [] and report.interview_questions == []


def test_invalid_reply_raises_readable_error():
    with pytest.raises(ValueError):
        parse_report("Sorry, I can't help with that.")
    with pytest.raises(ValueError):
        parse_report('{"summary": "no score"}')


def test_extract_json_finds_object_in_text():
    assert extract_json('noise {"a": 1} noise') == {"a": 1}
