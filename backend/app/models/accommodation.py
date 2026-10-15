from datetime import datetime
from sqlalchemy import String, Float, Boolean, JSON, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin

class AccommodationOption(Base, TimestampMixin, UUIDMixin):
    __tablename__ = "accommodation_options"

    run_id: Mapped[str] = mapped_column(ForeignKey("travel_runs.id"), index=True)
    name: Mapped[str] = mapped_column(String)
    location: Mapped[str] = mapped_column(String)
    accommodation_type: Mapped[str] = mapped_column(String)
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    nightly_price: Mapped[float] = mapped_column(Float)
    total_price: Mapped[float] = mapped_column(Float)
    amenities: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    room_type: Mapped[str | None] = mapped_column(String, nullable=True)
    source: Mapped[str] = mapped_column(String)
    source_type: Mapped[str] = mapped_column(String)
    availability: Mapped[str] = mapped_column(String, default="unknown")
    retrieved_at: Mapped[datetime] = mapped_column(DateTime)
    is_selected: Mapped[bool] = mapped_column(Boolean, default=False)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
