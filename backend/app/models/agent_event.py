from datetime import datetime
from sqlalchemy import String, Integer, JSON, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin


class AgentEvent(Base, TimestampMixin, UUIDMixin):
    __tablename__ = "agent_events"

    run_id: Mapped[str] = mapped_column(ForeignKey("travel_runs.id"), index=True)
    agent_name: Mapped[str] = mapped_column(String, index=True)
    event_type: Mapped[str] = mapped_column(String)
    message: Mapped[str | None] = mapped_column(String, nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
