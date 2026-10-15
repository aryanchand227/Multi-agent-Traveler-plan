from __future__ import annotations
from pydantic import BaseModel, Field
from app.schemas.transport import SourceType

class WeatherDay(BaseModel):
    date: str
    temperature_high: float | None = None
    temperature_low: float | None = None
    condition: str | None = None
    precipitation_probability: float | None = None
    humidity: float | None = None
    recommendation: str | None = None

class WeatherScheduleAdjustment(BaseModel):
    """Weather-based suggestion to adjust the itinerary."""
    original_day: int
    suggested_day: int | None = None
    activity: str
    reason: str
    severity: str = "suggestion"

class WeatherForecast(BaseModel):
    destination: str
    days: list[WeatherDay] = Field(default_factory=list)
    source: str = "unknown"
    source_type: SourceType = SourceType.MOCK
    overall_recommendation: str | None = None
    schedule_adjustments: list[WeatherScheduleAdjustment] = Field(default_factory=list)
