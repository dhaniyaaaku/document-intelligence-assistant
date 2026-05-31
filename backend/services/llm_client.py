"""Gemini chat client with automatic model fallback on quota errors."""

from functools import lru_cache
from typing import Any

from langchain_core.messages import BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from backend.utils.config import get_settings
from backend.utils.logging import get_logger

log = get_logger(__name__)

# Tried in order. When the primary hits a per-day quota, we fall back.
_FALLBACK_MODELS = ["gemini-1.5-flash", "gemini-1.5-flash-8b"]


class LLMNotConfiguredError(RuntimeError):
    pass


class LLMQuotaExceededError(RuntimeError):
    """Raised when every configured model has hit its quota."""


def _is_quota_error(exc: BaseException) -> bool:
    msg = str(exc).lower()
    return (
        "429" in msg
        or "resource_exhausted" in msg
        or "resourceexhausted" in msg
        or "quota" in msg
    )


def _build(model_name: str) -> ChatGoogleGenerativeAI:
    settings = get_settings()
    return ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=settings.gemini_api_key,
        temperature=0.2,
        convert_system_message_to_human=False,
    )


@lru_cache(maxsize=1)
def _models() -> list[ChatGoogleGenerativeAI]:
    settings = get_settings()
    if not settings.gemini_api_key:
        raise LLMNotConfiguredError(
            "GEMINI_API_KEY is not set. Add it to your .env file."
        )
    chain = [settings.gemini_model] + [
        m for m in _FALLBACK_MODELS if m != settings.gemini_model
    ]
    log.info("LLM fallback chain: %s", chain)
    return [_build(name) for name in chain]


class _FallbackLLM:
    """Drop-in replacement for ChatGoogleGenerativeAI that walks a fallback chain."""

    def invoke(self, messages: list[BaseMessage], **kwargs: Any):
        last_exc: BaseException | None = None
        for llm in _models():
            try:
                return llm.invoke(messages, **kwargs)
            except Exception as e:  # noqa: BLE001
                if not _is_quota_error(e):
                    raise
                log.warning("Quota hit on %s, falling back: %s", llm.model, e)
                last_exc = e
        raise LLMQuotaExceededError(
            "All Gemini models have hit their daily free-tier quota. "
            "Please try again later (quota resets at midnight Pacific Time)."
        ) from last_exc

    def bind_tools(self, tools, **kwargs):  # passthrough for LangGraph
        return _models()[0].bind_tools(tools, **kwargs)


def get_llm() -> _FallbackLLM:
    _models()  # validate config eagerly
    return _FallbackLLM()
