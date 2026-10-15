"""Abstract transport provider interfaces.

Each transport mode (bus/train/flight) has its own provider interface.
Providers return data in their own format; agents normalize to TransportOption.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from app.schemas.transport import TransportOption


class BusProvider(ABC):
    """Abstract bus transport provider."""

    @abstractmethod
    async def search(
        self,
        origin: str,
        destination: str,
        date: str,
        travelers: int = 1,
    ) -> list[TransportOption]:
        """Search for bus options."""
        ...

    @abstractmethod
    def get_provider_name(self) -> str:
        ...


class TrainProvider(ABC):
    """Abstract train transport provider."""

    @abstractmethod
    async def search(
        self,
        origin: str,
        destination: str,
        date: str,
        travelers: int = 1,
    ) -> list[TransportOption]:
        """Search for train options."""
        ...

    @abstractmethod
    def get_provider_name(self) -> str:
        ...


class FlightProvider(ABC):
    """Abstract flight transport provider."""

    @abstractmethod
    async def search(
        self,
        origin: str,
        destination: str,
        date: str,
        travelers: int = 1,
    ) -> list[TransportOption]:
        """Search for flight options."""
        ...

    @abstractmethod
    def get_provider_name(self) -> str:
        ...
