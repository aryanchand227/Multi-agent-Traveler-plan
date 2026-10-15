from datetime import datetime
from sqlalchemy import String, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin


class MemoryEntry(Base, TimestampMixin, UUIDMixin):
    __tablename__ = "memory_entries"

    user_id: Mapped[str] = mapped_column(String, index=True)
    run_id: Mapped[str | None] = mapped_column(String, index=True, nullable=True)
    memory_type: Mapped[str] = mapped_column(String)
    key: Mapped[str] = mapped_column(String, index=True)
    value: Mapped[dict] = mapped_column(JSON)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
