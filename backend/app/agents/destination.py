"""Destination/Activities agent."""
from __future__ import annotations

from typing import Any

from app.agents.base import BaseAgent
from app.providers.llm.base import LLMProvider
from app.providers.destination.base import DestinationProvider
from app.graph.state import TravelState


class DestinationAgent(BaseAgent):
    """Agent for discovering destination activities."""

    def __init__(self, llm_provider: LLMProvider, destination_provider: DestinationProvider):
        super().__init__(llm_provider)
        self.destination_provider = destination_provider

    @property
    def name(self) -> str:
        return "destination_agent"

    async def run(self, state: TravelState) -> dict[str, Any]:
        """Search for activities based on state."""
        destination = state.get("destination")
        interests = state.get("interests", [])
        travel_style = state.get("travel_style", "standard")
        duration_days = state.get("duration_days", 1)
        
        if not destination:
            return {"errors": ["Missing destination for activities search."]}
            
        results = await self.destination_provider.search_activities(
            destination=destination,
            interests=interests,
            travel_style=travel_style,
            days=duration_days
        )
        
        return {
            "activities": [act.model_dump() for act in results]
        }
