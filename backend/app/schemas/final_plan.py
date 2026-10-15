from __future__ import annotations
import datetime
from pydantic import BaseModel, Field
from app.schemas.transport import TransportComparison, TransportOption
from app.schemas.accommodation import AccommodationOption
from app.schemas.activities import ActivityOption
from app.schemas.weather import WeatherForecast
from app.schemas.budget import BudgetBreakdown
from app.schemas.itinerary import Itinerary

class TripSummary(BaseModel):
    request_id: str
    origin: str
    destination: str
    departure_date: str | None = None
    return_date: str | None = None
    travelers: int
    duration_days: int
    budget: float | None = None
    currency: str = "INR"
    travel_style: str
    interests: list[str] = Field(default_factory=list)

class DataSource(BaseModel):
    provider: str
    source_type: str
    retrieved_at: datetime.datetime | None = None

class ValidationResult(BaseModel):
    is_valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    checks_passed: list[str] = Field(default_factory=list)

class FinalTravelPlan(BaseModel):
    """Complete travel plan — the definitive backend→frontend contract."""
    trip_summary: TripSummary
    transportation: TransportComparison | None = None
    accommodation: AccommodationOption | None = None
    accommodation_alternatives: list[AccommodationOption] = Field(default_factory=list)
    activities: list[ActivityOption] = Field(default_factory=list)
    weather: WeatherForecast | None = None
    budget: BudgetBreakdown | None = None
    itinerary: Itinerary | None = None
    decision_factors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    data_sources: list[DataSource] = Field(default_factory=list)
    validation: ValidationResult | None = None
    human_readable_summary: str | None = None
    generated_at: datetime.datetime | None = None
