"""Weather forecast tools."""
from __future__ import annotations

from app.schemas.weather import WeatherForecast
from app.providers.weather.base import WeatherProvider


async def get_weather(
    destination: str,
    start_date: str,
    end_date: str,
    provider: WeatherProvider | None = None,
) -> WeatherForecast:
    """Retrieve weather forecast through provider adapter."""
    if provider is None:
        from app.providers.weather.mock import MockWeatherProvider
        provider = MockWeatherProvider()
    return await provider.get_forecast(
        destination=destination,
        start_date=start_date,
        end_date=end_date,
    )
