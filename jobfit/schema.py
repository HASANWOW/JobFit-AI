"""Structured output the LLM must return, validated with Pydantic."""

from __future__ import annotations

import json
import re

from pydantic import BaseModel, Field, ValidationError, field_validator


class FitReport(BaseModel):
    match_score: int = Field(ge=0, le=100, description="How well the CV fits the job, 0-100")
    summary: str = Field(description="Two or three sentences on the overall fit")
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    improvement_tips: list[str] = Field(default_factory=list)
    interview_questions: list[str] = Field(default_factory=list)

    @field_validator("match_score", mode="before")
    @classmethod
    def clamp_score(cls, value: object) -> int:
        # Models sometimes answer "85" or 85.5; accept both and keep it in range
        score = int(round(float(value)))  # type: ignore[arg-type]
        return max(0, min(100, score))


def extract_json(text: str) -> dict:
    """Pull the first JSON object out of a model reply, even if it is wrapped in prose or ```json fences."""
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fenced:
        return json.loads(fenced.group(1))
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end <= start:
        raise ValueError("No JSON object found in the model reply")
    return json.loads(text[start : end + 1])


def parse_report(text: str) -> FitReport:
    """Parse and validate a model reply. Raises ValueError with a readable message on failure."""
    try:
        return FitReport.model_validate(extract_json(text))
    except (json.JSONDecodeError, ValidationError) as exc:
        raise ValueError(f"Model reply did not match the expected format: {exc}") from exc
