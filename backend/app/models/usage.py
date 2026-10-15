"""LLM Usage Record model for tracking API consumption and costs."""
from __future__ import annotations

from sqlalchemy import String, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin


class LLMUsageRecord(Base, TimestampMixin, UUIDMixin):
    """Tracks token counts, execution duration, and estimated cost per agent/run."""
    __tablename__ = "llm_usage_records"

    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    request_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    run_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    agent_name: Mapped[str] = mapped_column(String, index=True)
    provider: Mapped[str] = mapped_column(String, default="groq")
    model: Mapped[str] = mapped_column(String)
    provider_requests: Mapped[int] = mapped_column(Integer, default=1)
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    estimated_cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    duration_ms: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String, default="success")  # success, error, throttled
