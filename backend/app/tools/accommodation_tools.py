"""Accommodation search tools."""
from __future__ import annotations

from typing import List
from app.schemas.accommodation import AccommodationOption
from app.providers.accommodation.base import AccommodationProvider


async def search_hotels(
    destination: str,
    check_in: str,
    check_out: str,
    travelers: int = 1,
    budget_per_night: float | None = None,
    travel_style: str = "standard",
    provider: AccommodationProvider | None = None,
) -> List[AccommodationOption]:
    """Search accommodation options through provider adapter."""
    if provider is None:
        from app.providers.accommodation.mock import MockAccommodationProvider
        provider = MockAccommodationProvider()
    return await provider.search(
        destination=destination,
        check_in=check_in,
        check_out=check_out,
        travelers=travelers,
        budget_per_night=budget_per_night,
        travel_style=travel_style,
    )
