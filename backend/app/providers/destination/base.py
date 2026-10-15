"""Abstract destination/activity provider interface."""
from __future__ import annotations

from abc import ABC, abstractmethod

from app.schemas.activities import ActivityOption


class DestinationProvider(ABC):
    """Abstract destination/activity provider."""

    @abstractmethod
    async def search_activities(
        self,
        destination: str,
        interests: list[str] | None = None,
        travel_style: str = "standard",
        days: int = 1,
    ) -> list[ActivityOption]:
        """Search for activities at a destination."""
        ...

    @abstractmethod
    def get_provider_name(self) -> str:
        ...
