"""User database operations."""
from __future__ import annotations

from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    """Repository for user entity operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        email: str,
        hashed_password: str,
        display_name: str | None = None,
        user_id: str | None = None,
    ) -> User:
        """Create a new user."""
        kwargs: dict[str, Any] = {
            "email": email.lower().strip(),
            "hashed_password": hashed_password,
            "display_name": display_name or email.split("@")[0],
            "is_active": True,
        }
        if user_id:
            kwargs["id"] = user_id

        user = User(**kwargs)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_by_id(self, user_id: str) -> User | None:
        """Retrieve user by UUID."""
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """Retrieve user by unique email."""
        result = await self.session.execute(
            select(User).where(User.email == email.lower().strip())
        )
        return result.scalar_one_or_none()
