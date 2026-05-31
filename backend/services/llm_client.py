"""Lazily-initialized Gemini chat client via LangChain."""

from functools import lru_cache

from langchain_google_genai import ChatGoogleGenerativeAI

from backend.utils.config import get_settings


class LLMNotConfiguredError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def get_llm() -> ChatGoogleGenerativeAI:
    settings = get_settings()
    if not settings.gemini_api_key:
        raise LLMNotConfiguredError(
            "GEMINI_API_KEY is not set. Add it to your .env file."
        )
    return ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.gemini_api_key,
        temperature=0.2,
        convert_system_message_to_human=False,
    )
