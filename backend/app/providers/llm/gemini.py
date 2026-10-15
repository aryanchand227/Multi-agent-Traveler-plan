from typing import Any, Type
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models import BaseChatModel

from app.providers.llm.base import LLMProvider


class GeminiProvider(LLMProvider):
    """Google Gemini implementation of the LLMProvider."""

    def __init__(self, api_key: str, model_name: str = "gemini-1.5-pro", **kwargs):
        self.api_key = api_key
        self.model_name = model_name
        self.kwargs = kwargs

    def get_chat_model(self, **kwargs: Any) -> BaseChatModel:
        """Get a chat model instance."""
        merged_kwargs = {**self.kwargs, **kwargs}
        return ChatGoogleGenerativeAI(
            api_key=self.api_key,
            model=self.model_name,
            **merged_kwargs
        )

    def get_structured_model(self, schema: Type[BaseModel], **kwargs: Any) -> BaseChatModel:
        """Get a model that outputs structured data according to a schema."""
        model = self.get_chat_model(**kwargs)
        return model.with_structured_output(schema)

    def get_model_name(self) -> str:
        return self.model_name

    def get_provider_name(self) -> str:
        return "gemini"
