"""User preferences database operations."""
from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.preference import UserPreference


class PreferenceRepository:
    """Repository for user preferences."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_user(self, user_id: str) -> UserPreference | None:
        result = await self.session.execute(
            select(UserPreference).where(UserPreference.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: str) -> UserPreference | None:
        return await self.get_by_user(user_id)

    async def create_or_update(
        self, user_id: str, *args: Any, **kwargs: Any
    ) -> UserPreference:
        if args and isinstance(args[0], dict):
            kwargs.update(args[0])
        existing = await self.get_by_user(user_id)
        if existing:
            for key, value in kwargs.items():
                if value is not None and hasattr(existing, key):
                    setattr(existing, key, value)
            await self.session.commit()
            await self.session.refresh(existing)
            return existing
        else:
            # Filter kwargs to valid model attributes
            valid_keys = {
                "preferred_transport", "travel_style", "budget_preference",
                "hotel_preference", "activity_preferences", "food_preferences",
                "default_currency", "default_output_detail"
            }
            data = {k: v for k, v in kwargs.items() if k in valid_keys and v is not None}
            pref = UserPreference(user_id=user_id, **data)
            self.session.add(pref)
            await self.session.commit()
            await self.session.refresh(pref)
            return pref


PreferencesRepository = PreferenceRepository
