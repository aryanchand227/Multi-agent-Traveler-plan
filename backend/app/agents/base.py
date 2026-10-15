"""Base architecture for all AI agents."""
from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any, TypeVar

from pydantic import BaseModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.providers.llm.base import LLMProvider
from app.graph.state import TravelState

T = TypeVar("T", bound=BaseModel)


class BaseAgent(ABC):
    """Abstract base class for all specialized agents."""

    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
        self.model_name = self.llm_provider.get_model_name()
        
    @property
    @abstractmethod
    def name(self) -> str:
        """The agent's internal name."""
        ...

    @abstractmethod
    async def run(self, state: TravelState) -> dict[str, Any]:
        """Execute the agent's primary logic."""
        ...

    async def get_structured_response(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: type[T],
        temperature: float = 0.0,
    ) -> T:
        """Get a strongly-typed response from the LLM."""
        model = self.llm_provider.get_structured_model(
            schema=response_model, 
            temperature=temperature
        )
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
        
        # Invoke returns a BaseModel instance because of with_structured_output
        response = await model.ainvoke(messages)
        return response

    async def get_text_response(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
    ) -> str:
        """Get a raw text response from the LLM."""
        model = self.llm_provider.get_chat_model(temperature=temperature)
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
        
        response = await model.ainvoke(messages)
        return str(response.content)
