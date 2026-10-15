from sqlalchemy import String, Float, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin

class UserPreference(Base, TimestampMixin, UUIDMixin):
    __tablename__ = "user_preferences"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    preferred_transport: Mapped[str | None] = mapped_column(String, nullable=True)
    travel_style: Mapped[str | None] = mapped_column(String, nullable=True)
    budget_preference: Mapped[float | None] = mapped_column(Float, nullable=True)
    hotel_preference: Mapped[str | None] = mapped_column(String, nullable=True)
    activity_preferences: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    food_preferences: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    default_currency: Mapped[str] = mapped_column(String, default="INR")
    default_output_detail: Mapped[str] = mapped_column(String, default="standard")

    __table_args__ = (
        UniqueConstraint("user_id", name="uq_user_preference_user_id"),
    )
