from sqlalchemy import String, Integer, Float, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin

class Itinerary(Base, TimestampMixin, UUIDMixin):
    __tablename__ = "itineraries"

    run_id: Mapped[str] = mapped_column(ForeignKey("travel_runs.id"), unique=True, index=True)
    title: Mapped[str | None] = mapped_column(String, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    total_days: Mapped[int] = mapped_column(Integer)


class ItineraryDay(Base, TimestampMixin, UUIDMixin):
    __tablename__ = "itinerary_days"

    itinerary_id: Mapped[str] = mapped_column(ForeignKey("itineraries.id"), index=True)
    day_number: Mapped[int] = mapped_column(Integer)
    date: Mapped[str | None] = mapped_column(String, nullable=True)
    theme: Mapped[str | None] = mapped_column(String, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class ItineraryItem(Base, TimestampMixin, UUIDMixin):
    __tablename__ = "itinerary_items"

    day_id: Mapped[str] = mapped_column(ForeignKey("itinerary_days.id"), index=True)
    time_start: Mapped[str | None] = mapped_column(String, nullable=True)
    time_end: Mapped[str | None] = mapped_column(String, nullable=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    item_type: Mapped[str] = mapped_column(String)
    estimated_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    location: Mapped[str | None] = mapped_column(String, nullable=True)
    notes: Mapped[str | None] = mapped_column(String, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
