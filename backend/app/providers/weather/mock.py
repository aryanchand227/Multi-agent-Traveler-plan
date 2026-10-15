"""Mock weather provider."""
from __future__ import annotations

import datetime

from app.providers.weather.base import WeatherProvider
from app.schemas.weather import WeatherForecast, WeatherDay
from app.schemas.transport import SourceType


class MockWeatherProvider(WeatherProvider):
    """Mock implementation of WeatherProvider."""

    async def get_forecast(
        self,
        destination: str,
        start_date: str,
        end_date: str,
    ) -> WeatherForecast:
        """Get weather forecast for a destination and date range."""
        try:
            start = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
            end = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
            days_count = max(1, (end - start).days + 1)
        except ValueError:
            start = datetime.date.today()
            days_count = 3
            
        dest_lower = destination.lower()
        
        # Determine weather based on some basic logic (e.g., month + destination)
        month = start.month
        
        # Default summer/monsoon/winter logic for India
        if 3 <= month <= 5:
            # Summer
            temp_high = 35.0
            temp_low = 25.0
            condition = "Sunny"
            precip = 0.05
            humidity = 40.0
            rec = "Wear light cotton clothes, carry sunscreen and stay hydrated."
        elif 6 <= month <= 9:
            # Monsoon
            temp_high = 30.0
            temp_low = 24.0
            condition = "Rainy"
            precip = 0.80
            humidity = 85.0
            rec = "Carry an umbrella or raincoat. Expect heavy showers."
        else:
            # Winter
            if "delhi" in dest_lower or "shimla" in dest_lower or "manali" in dest_lower:
                temp_high = 20.0
                temp_low = 8.0
                condition = "Clear"
                precip = 0.0
                humidity = 50.0
                rec = "Wear warm layers as evenings can be chilly."
            else:
                temp_high = 28.0
                temp_low = 18.0
                condition = "Pleasant"
                precip = 0.05
                humidity = 60.0
                rec = "Perfect weather for sightseeing. Carry a light jacket for evenings."
                
        weather_days = []
        for i in range(days_count):
            current_date = start + datetime.timedelta(days=i)
            # Add some minor daily variation
            var = (i % 3) - 1
            weather_days.append(
                WeatherDay(
                    date=current_date.strftime("%Y-%m-%d"),
                    temperature_high=temp_high + var,
                    temperature_low=temp_low + var,
                    condition=condition if i % 4 != 0 else ("Cloudy" if condition == "Sunny" else condition),
                    precipitation_probability=precip,
                    humidity=humidity + (var * 2),
                    recommendation=rec
                )
            )
            
        overall = f"Overall {condition.lower()} weather expected in {destination}. {rec}"
        
        return WeatherForecast(
            destination=destination,
            days=weather_days,
            source="MockWeatherAPI",
            source_type=SourceType.MOCK,
            overall_recommendation=overall,
            schedule_adjustments=[]
        )

    def get_provider_name(self) -> str:
        return "Mock Weather Provider"
