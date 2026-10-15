from __future__ import annotations
import datetime
from enum import Enum
from pydantic import BaseModel, Field
from app.schemas.transport import SourceType

class ActivityCategory(str, Enum):
    ADVENTURE = "adventure"
    CULTURAL = "cultural"
    FOOD = "food"
    NIGHTLIFE = "nightlife"
    NATURE = "nature"
    HISTORICAL = "historical"
    SHOPPING = "shopping"
    RELAXATION = "relaxation"
    FAMILY = "family"
    INDOOR = "indoor"
    OUTDOOR = "outdoor"

class ActivityOption(BaseModel):
    id: str
    name: str
    category: ActivityCategory
    location: str | None = None
    description: str | None = None
    estimated_duration_minutes: int | None = None
    estimated_cost: float | None = None
    best_time: str | None = None
    weather_dependency: bool = False
    source: str
    source_type: SourceType
    retrieved_at: datetime.datetime | None = None

class ActivitySearch(BaseModel):
    destination: str
    interests: list[str] = Field(default_factory=list)
    travel_style: str = "standard"
    budget_for_activities: float | None = None
    days: int = 1
