"""User preferences API endpoints — backed by persistent database."""
from __future__ import annotations

from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user_id, get_database
from app.db.repositories.preferences import PreferenceRepository

router = APIRouter(tags=["preferences"])


@router.get("")
async def get_preferences(
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_database),
) -> dict[str, Any]:
    """Get preferences for the authenticated user from database."""
    repo = PreferenceRepository(session)
    pref = await repo.get_by_user(user_id)

    if pref:
        return {
            "preferred_transport": pref.preferred_transport,
            "travel_style": pref.travel_style or "standard",
            "budget_preference": pref.budget_preference,
            "hotel_preference": pref.hotel_preference,
            "activity_preferences": pref.activity_preferences or [],
            "food_preferences": pref.food_preferences or [],
            "default_currency": pref.default_currency or "INR",
            "default_output_detail": pref.default_output_detail or "standard",
        }

    return {
        "preferred_transport": None,
        "travel_style": "standard",
        "budget_preference": None,
        "hotel_preference": None,
        "activity_preferences": [],
        "food_preferences": [],
        "default_currency": "INR",
        "default_output_detail": "standard",
    }


@router.put("")
async def update_preferences(
    preferences: dict[str, Any],
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_database),
) -> dict[str, Any]:
    """Update preferences for the authenticated user in database."""
    repo = PreferenceRepository(session)
    pref = await repo.create_or_update(user_id, preferences)

    return {
        "preferred_transport": pref.preferred_transport,
        "travel_style": pref.travel_style or "standard",
        "budget_preference": pref.budget_preference,
        "hotel_preference": pref.hotel_preference,
        "activity_preferences": pref.activity_preferences or [],
        "food_preferences": pref.food_preferences or [],
        "default_currency": pref.default_currency or "INR",
        "default_output_detail": pref.default_output_detail or "standard",
    }
