"""Abstract LLM provider interface.

All LLM interactions go through this abstraction.
Agents never directly import OpenAI/Gemini — they use LLMProvider.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Type

from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel


class LLMProvider(ABC):
    """Abstract base for LLM providers."""

    @abstractmethod
    def get_chat_model(self, **kwargs: Any) -> BaseChatModel:
        """Get a chat model instance."""
        ...

    @abstractmethod
    def get_structured_model(
        self,
        schema: Type[BaseModel],
        **kwargs: Any,
    ) -> BaseChatModel:
        """Get a chat model that returns structured output matching the schema."""
        ...

    @abstractmethod
    def get_model_name(self) -> str:
        """Get the model identifier."""
        ...

    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the provider name (openai/gemini)."""
        ...
