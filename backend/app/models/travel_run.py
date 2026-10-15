from datetime import datetime
from sqlalchemy import String, Integer, Float, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin


class TravelRequest(Base, TimestampMixin):
    __tablename__ = "travel_requests"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    raw_request: Mapped[str] = mapped_column(Text)
    origin: Mapped[str | None] = mapped_column(String, nullable=True)
    destination: Mapped[str | None] = mapped_column(String, nullable=True)
    departure_date: Mapped[str | None] = mapped_column(String, nullable=True)
    return_date: Mapped[str | None] = mapped_column(String, nullable=True)
    travelers: Mapped[int | None] = mapped_column(Integer, nullable=True)
    budget: Mapped[float | None] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String, default="INR")
    travel_style: Mapped[str | None] = mapped_column(String, nullable=True)
    preferred_transport: Mapped[list | None] = mapped_column(JSON, nullable=True)
    interests: Mapped[list | None] = mapped_column(JSON, nullable=True)
    accommodation_preference: Mapped[str | None] = mapped_column(String, nullable=True)
    output_detail: Mapped[str] = mapped_column(String, default="standard")
    additional_requirements: Mapped[str | None] = mapped_column(Text, nullable=True)


class TravelRun(Base, TimestampMixin, UUIDMixin):
    __tablename__ = "travel_runs"

    request_id: Mapped[str] = mapped_column(ForeignKey("travel_requests.id"), index=True)
    status: Mapped[str] = mapped_column(String, default="pending")
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    final_plan: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    agent_states: Mapped[dict | None] = mapped_column(JSON, nullable=True)
