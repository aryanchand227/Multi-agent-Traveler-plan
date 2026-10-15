"""Abstract weather provider interface."""
from __future__ import annotations

from abc import ABC, abstractmethod

from app.schemas.weather import WeatherForecast


class WeatherProvider(ABC):
    """Abstract weather provider."""

    @abstractmethod
    async def get_forecast(
        self,
        destination: str,
        start_date: str,
        end_date: str,
    ) -> WeatherForecast:
        """Get weather forecast for a destination and date range."""
        ...

    @abstractmethod
    def get_provider_name(self) -> str:
        ...
