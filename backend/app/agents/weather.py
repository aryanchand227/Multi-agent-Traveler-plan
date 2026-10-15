"""Weather agent."""
from __future__ import annotations

from typing import Any

from app.agents.base import BaseAgent
from app.providers.llm.base import LLMProvider
from app.providers.weather.base import WeatherProvider
from app.graph.state import TravelState


class WeatherAgent(BaseAgent):
    """Agent for fetching weather forecasts."""

    def __init__(self, llm_provider: LLMProvider, weather_provider: WeatherProvider):
        super().__init__(llm_provider)
        self.weather_provider = weather_provider

    @property
    def name(self) -> str:
        return "weather_agent"

    async def run(self, state: TravelState) -> dict[str, Any]:
        """Get weather forecast based on state."""
        destination = state.get("destination")
        start_date = state.get("departure_date")
        end_date = state.get("return_date")
        
        if not destination or not start_date or not end_date:
            return {"errors": ["Missing destination or dates for weather forecast."]}
            
        forecast = await self.weather_provider.get_forecast(
            destination=destination,
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            "weather": forecast.model_dump()
        }
