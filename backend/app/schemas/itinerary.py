from __future__ import annotations
from enum import Enum
from pydantic import BaseModel, Field

class ItineraryItemType(str, Enum):
    TRANSPORT = "transport"
    ACCOMMODATION = "accommodation"
    ACTIVITY = "activity"
    MEAL = "meal"
    REST = "rest"
    FREE_TIME = "free_time"

class ItineraryItem(BaseModel):
    time_start: str | None = None
    time_end: str | None = None
    title: str
    description: str | None = None
    item_type: ItineraryItemType
    estimated_cost: float | None = None
    location: str | None = None
    notes: str | None = None

class ItineraryDay(BaseModel):
    day_number: int
    date: str | None = None
    theme: str | None = None
    items: list[ItineraryItem] = Field(default_factory=list)
    notes: str | None = None

class Itinerary(BaseModel):
    title: str | None = None
    summary: str | None = None
    total_days: int
    days: list[ItineraryDay] = Field(default_factory=list)
