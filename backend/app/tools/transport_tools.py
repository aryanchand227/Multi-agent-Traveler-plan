"""Transport search and processing tools."""
from __future__ import annotations

from typing import List
from app.schemas.transport import TransportOption
from app.providers.transport.base import BusProvider, TrainProvider, FlightProvider


async def search_bus_options(
    origin: str,
    destination: str,
    date: str,
    travelers: int = 1,
    provider: BusProvider | None = None,
) -> List[TransportOption]:
    """Search bus options through provider adapter."""
    if provider is None:
        from app.providers.transport.mock_bus import MockBusProvider
        provider = MockBusProvider()
    return await provider.search(origin=origin, destination=destination, date=date, travelers=travelers)


async def search_train_options(
    origin: str,
    destination: str,
    date: str,
    travelers: int = 1,
    provider: TrainProvider | None = None,
) -> List[TransportOption]:
    """Search train options through provider adapter."""
    if provider is None:
        from app.providers.transport.mock_train import MockTrainProvider
        provider = MockTrainProvider()
    return await provider.search(origin=origin, destination=destination, date=date, travelers=travelers)


async def search_flight_options(
    origin: str,
    destination: str,
    date: str,
    travelers: int = 1,
    provider: FlightProvider | None = None,
) -> List[TransportOption]:
    """Search flight options through provider adapter."""
    if provider is None:
        from app.providers.transport.mock_flight import MockFlightProvider
        provider = MockFlightProvider()
    return await provider.search(origin=origin, destination=destination, date=date, travelers=travelers)
