"""Memory service — provides short-term (state) and long-term (DB) memory."""
from __future__ import annotations

from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.preferences import PreferencesRepository
from app.db.repositories.memory import MemoryRepository


class MemoryService:
    """Unified memory interface for agents."""

    def __init__(self, db_session: Optional[AsyncSession] = None):
        self.db_session = db_session
        self._preferences_repo = PreferencesRepository(db_session) if db_session else None
        self._memory_repo = MemoryRepository(db_session) if db_session else None

    async def get_user_preferences(self, user_id: str) -> dict[str, Any]:
        """Load stored user preferences from the database."""
        if not self._preferences_repo:
            return {}
        try:
            pref = await self._preferences_repo.get_by_user_id(user_id)
            if pref:
                return {
                    "preferred_transport": pref.preferred_transport,
                    "travel_style": pref.travel_style,
                    "budget_preference": pref.budget_preference,
                    "hotel_preference": pref.hotel_preference,
                    "activity_preferences": pref.activity_preferences or [],
                    "food_preferences": pref.food_preferences or [],
                    "default_currency": pref.default_currency,
                    "default_output_detail": pref.default_output_detail,
                }
        except Exception:
            pass
        return {}

    async def save_user_preferences(self, user_id: str, preferences: dict[str, Any]) -> None:
        """Persist user preferences."""
        if not self._preferences_repo:
            return
        try:
            await self._preferences_repo.create_or_update(user_id, preferences)
        except Exception:
            pass

    async def store_memory(self, user_id: str, key: str, value: Any) -> None:
        """Store a memory entry."""
        if not self._memory_repo:
            return
        try:
            await self._memory_repo.store(user_id, key, value)
        except Exception:
            pass

    async def recall_memory(self, user_id: str, key: str) -> Any:
        """Retrieve a memory entry."""
        if not self._memory_repo:
            return None
        try:
            return await self._memory_repo.retrieve(user_id, key)
        except Exception:
            return None
