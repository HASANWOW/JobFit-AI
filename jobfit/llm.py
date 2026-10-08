"""Thin wrapper around any OpenAI-compatible chat API (Groq, OpenRouter, OpenAI, 9router, a local server...)."""

from __future__ import annotations

import os
from dataclasses import dataclass

from openai import OpenAI

from . import prompts
from .schema import FitReport, parse_report

# CV and job text are trimmed so a long PDF can't blow past the model's context window
MAX_CHARS = 12_000


@dataclass
class LLMConfig:
    api_key: str
    base_url: str
    model: str

    @classmethod
    def from_env(cls) -> "LLMConfig":
        return cls(
            api_key=os.getenv("LLM_API_KEY", ""),
            base_url=os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1"),
            model=os.getenv("LLM_MODEL", "llama-3.1-8b-instant"),
        )


class JobFitClient:
    def __init__(self, config: LLMConfig):
        if not config.api_key:
            raise ValueError("No API key set. Add LLM_API_KEY to your .env file.")
        self.config = config
        self.client = OpenAI(api_key=config.api_key, base_url=config.base_url)

    def _chat(self, system: str, user: str, *, json_mode: bool = False, temperature: float = 0.2) -> str:
        kwargs = {"response_format": {"type": "json_object"}} if json_mode else {}
        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=temperature,
            **kwargs,
        )
        return response.choices[0].message.content or ""

    def analyze(self, cv: str, job: str, language: str = "English") -> FitReport:
        user = prompts.ANALYSIS_USER.format(cv=cv[:MAX_CHARS], job=job[:MAX_CHARS], language=language)
        reply = self._chat(prompts.ANALYSIS_SYSTEM, user, json_mode=True)
        try:
            return parse_report(reply)
        except ValueError as first_error:
            # One repair attempt: show the model its own output and the validation error
            repair = (
                f"{user}\n\nYour previous reply was invalid:\n{reply}\n\n"
                f"Error: {first_error}\nReturn only the corrected JSON object."
            )
            return parse_report(self._chat(prompts.ANALYSIS_SYSTEM, repair, json_mode=True))

    def cover_letter(self, cv: str, job: str, language: str = "English") -> str:
        user = prompts.COVER_LETTER_USER.format(cv=cv[:MAX_CHARS], job=job[:MAX_CHARS], language=language)
        return self._chat(prompts.COVER_LETTER_SYSTEM, user, temperature=0.6).strip()
