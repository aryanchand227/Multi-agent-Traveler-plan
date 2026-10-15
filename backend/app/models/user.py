from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin


class User(Base, TimestampMixin, UUIDMixin):
    __tablename__ = "users"

    email: Mapped[str | None] = mapped_column(String, unique=True, index=True, nullable=True)
    hashed_password: Mapped[str | None] = mapped_column(String, nullable=True)
    display_name: Mapped[str | None] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

