from __future__ import annotations
from typing import Any
import datetime
from enum import Enum
from pydantic import BaseModel, Field

class TransportMode(str, Enum):
    BUS = "bus"
    TRAIN = "train"
    FLIGHT = "flight"

class ProviderType(str, Enum):
    GOVERNMENT = "government"
    PRIVATE = "private"
    AIRLINE = "airline"

class ComfortLevel(str, Enum):
    ECONOMY = "economy"
    STANDARD = "standard"
    PREMIUM = "premium"
    LUXURY = "luxury"

class SourceType(str, Enum):
    MOCK = "mock"
    LIVE = "live"
    CACHED = "cached"

class TransportOption(BaseModel):
    """Normalized transport option — common schema for bus/train/flight."""
    id: str
    mode: TransportMode
    provider: str
    provider_type: ProviderType
    origin: str
    destination: str
    departure_time: str | None = None
    arrival_time: str | None = None
    duration_minutes: int | None = None
    price_per_person: float
    total_price: float
    stops: int = 0
    comfort_level: ComfortLevel = ComfortLevel.STANDARD
    vehicle_info: str | None = None
    availability: str = "unknown"
    source: str
    source_type: SourceType
    retrieved_at: datetime.datetime
    score: float | None = None
    decision_factors: dict[str, Any] | list[str] | None = None

class BusOption(TransportOption):
    """Bus-specific transport option."""
    bus_type: str | None = None
    operator_type: str | None = None

class TrainOption(TransportOption):
    """Train-specific transport option."""
    train_number: str | None = None
    train_name: str | None = None
    train_class: str | None = None

class FlightOption(TransportOption):
    """Flight-specific transport option."""
    airline: str | None = None
    flight_number: str | None = None
    departure_airport: str | None = None
    arrival_airport: str | None = None
    baggage_info: str | None = None

class TransportComparison(BaseModel):
    """Comparison of transport options across modes."""
    selected: TransportOption
    alternatives: list[TransportOption] = Field(default_factory=list)
    cheapest: TransportOption | None = None
    fastest: TransportOption | None = None
    recommended: TransportOption | None = None
    recommendation_reason: str | None = None
