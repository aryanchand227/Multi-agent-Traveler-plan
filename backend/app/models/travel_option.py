from datetime import datetime
import sqlalchemy as sa
from sqlalchemy import String, Integer, Float, Boolean, JSON, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin

class TransportOption(Base, TimestampMixin, UUIDMixin):
    __tablename__ = "transport_options"

    run_id: Mapped[str] = mapped_column(ForeignKey("travel_runs.id"), index=True)
    mode: Mapped[str] = mapped_column(String)
    provider: Mapped[str] = mapped_column(String)
    provider_type: Mapped[str] = mapped_column(String)
    origin: Mapped[str] = mapped_column(String)
    destination: Mapped[str] = mapped_column(String)
    departure_time: Mapped[str | None] = mapped_column(String, nullable=True)
    arrival_time: Mapped[str | None] = mapped_column(String, nullable=True)
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    price_per_person: Mapped[float] = mapped_column(Float)
    total_price: Mapped[float] = mapped_column(Float)
    stops: Mapped[int] = mapped_column(Integer, default=0)
    comfort_level: Mapped[str | None] = mapped_column(String, nullable=True)
    vehicle_info: Mapped[str | None] = mapped_column(String, nullable=True)
    availability: Mapped[str] = mapped_column(String, default="unknown")
    source: Mapped[str] = mapped_column(String)
    source_type: Mapped[str] = mapped_column(String)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    is_selected: Mapped[bool] = mapped_column(Boolean, default=False, server_default=sa.false())
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    decision_factors: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
