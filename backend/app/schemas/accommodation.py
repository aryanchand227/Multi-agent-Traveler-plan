from __future__ import annotations
import datetime
from enum import Enum
from pydantic import BaseModel, Field
from app.schemas.transport import SourceType

class AccommodationType(str, Enum):
    HOSTEL = "hostel"
    BUDGET_HOTEL = "budget_hotel"
    GUESTHOUSE = "guesthouse"
    HOTEL_3STAR = "hotel_3star"
    HOTEL_4STAR = "hotel_4star"
    HOTEL_5STAR = "hotel_5star"
    RESORT = "resort"

class AccommodationOption(BaseModel):
    id: str
    name: str
    location: str
    accommodation_type: AccommodationType
    rating: float | None = None
    nightly_price: float
    total_price: float
    amenities: list[str] = Field(default_factory=list)
    room_type: str | None = None
    source: str
    source_type: SourceType
    availability: str = "unknown"
    retrieved_at: datetime.datetime
    is_selected: bool = False

class AccommodationSearch(BaseModel):
    destination: str
    check_in: str
    check_out: str
    travelers: int
    budget_per_night: float | None = None
    travel_style: str = "standard"
    preferences: list[str] = Field(default_factory=list)
