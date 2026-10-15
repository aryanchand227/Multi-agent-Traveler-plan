"""Destination and activity search tools."""
from __future__ import annotations

from typing import List
from app.schemas.activities import ActivityOption
from app.providers.destination.base import DestinationProvider


async def search_attractions(
    destination: str,
    interests: list[str] | None = None,
    travel_style: str = "standard",
    days: int = 1,
    provider: DestinationProvider | None = None,
) -> List[ActivityOption]:
    """Search activities and attractions through provider adapter."""
    if provider is None:
        from app.providers.destination.mock import MockDestinationProvider
        provider = MockDestinationProvider()
    return await provider.search_activities(
        destination=destination,
        interests=interests or [],
        travel_style=travel_style,
        days=days,
    )
