from sqlalchemy import String, Integer, Float, Boolean, Text, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin

class Activity(Base, TimestampMixin, UUIDMixin):
    __tablename__ = "activities"

    run_id: Mapped[str] = mapped_column(ForeignKey("travel_runs.id"), index=True)
    name: Mapped[str] = mapped_column(String)
    category: Mapped[str] = mapped_column(String)
    location: Mapped[str | None] = mapped_column(String, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    estimated_duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    estimated_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    best_time: Mapped[str | None] = mapped_column(String, nullable=True)
    weather_dependency: Mapped[bool] = mapped_column(Boolean, default=False)
    source: Mapped[str] = mapped_column(String)
    source_type: Mapped[str] = mapped_column(String)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
