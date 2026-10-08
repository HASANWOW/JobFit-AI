"""Turn provider errors into messages a user can act on."""

from __future__ import annotations

from openai import APIConnectionError, APIStatusError, APITimeoutError

MESSAGES = {
    400: "The provider rejected the request. Check LLM_MODEL and LLM_BASE_URL in your .env.",
    401: "Your API key was rejected. Check LLM_API_KEY in your .env (no spaces or quotes).",
    403: "Your API key isn't allowed to use this model. Check your provider's console.",
    404: "That model isn't available on your account. Change LLM_MODEL in your .env.",
    429: "Rate limit or free quota reached. Wait a minute and try again.",
}


def friendly_error(exc: Exception) -> str:
    if isinstance(exc, APITimeoutError):
        return "The model took too long to answer. Try again, or shorten the CV / job posting."
    if isinstance(exc, APIConnectionError):
        return "Couldn't reach the LLM provider. Check your internet connection and LLM_BASE_URL."
    if isinstance(exc, APIStatusError):
        if exc.status_code >= 500:
            return "The model is overloaded right now (the app already retried a few times). Wait a minute and try again."
        return MESSAGES.get(exc.status_code, f"The provider returned an error ({exc.status_code}).")
    return str(exc)
