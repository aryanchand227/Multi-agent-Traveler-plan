"""Abstract accommodation provider interface."""
from __future__ import annotations

from abc import ABC, abstractmethod

from app.schemas.accommodation import AccommodationOption


class AccommodationProvider(ABC):
    """Abstract accommodation provider."""

    @abstractmethod
    async def search(
        self,
        destination: str,
        check_in: str,
        check_out: str,
        travelers: int = 1,
        budget_per_night: float | None = None,
        travel_style: str = "standard",
    ) -> list[AccommodationOption]:
        """Search for accommodation options."""
        ...

    @abstractmethod
    def get_provider_name(self) -> str:
        ...
