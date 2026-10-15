from typing import Optional

from app.core.config import get_settings, Settings
from app.providers.llm.base import LLMProvider
from app.providers.llm.openai import OpenAIProvider
from app.providers.llm.gemini import GeminiProvider


def get_llm_provider(settings: Optional[Settings] = None) -> LLMProvider:
    """
    Factory function to get the appropriate LLM provider based on settings.
    """
    if settings is None:
        settings = get_settings()

    provider_name = settings.llm_provider.lower()

    if provider_name == "openai":
        kwargs = {
            "api_key": settings.llm_api_key,
            "model_name": settings.llm_model,
        }
        if settings.llm_base_url:
            kwargs["base_url"] = settings.llm_base_url
        return OpenAIProvider(**kwargs)
    elif provider_name == "groq":
        return OpenAIProvider(
            api_key=settings.llm_api_key,
            model_name=settings.llm_model,
            base_url=settings.llm_base_url or "https://api.groq.com/openai/v1",
        )
    else:
        return GeminiProvider(
            api_key=settings.llm_api_key,
            model_name=settings.llm_model if settings.llm_model != "gpt-4o-mini" else "gemini-1.5-pro",
        )
