"""Flight Agent — responsible ONLY for flight transportation."""
from __future__ import annotations

from typing import Any

from app.agents.base import BaseAgent
from app.agents.context_builders import build_flight_agent_context
from app.graph.state import TravelState
from app.providers.transport.base import FlightProvider
from app.tools.transport_tools import search_flight_options


class FlightAgent(BaseAgent):
    def __init__(self, llm_provider, flight_provider: FlightProvider):
        super().__init__(llm_provider)
        self.flight_provider = flight_provider

    @property
    def name(self) -> str:
        return "FlightAgent"

    async def run(self, state: TravelState) -> dict[str, Any]:
        ctx = build_flight_agent_context(state)
        results = await search_flight_options(
            origin=ctx["origin"],
            destination=ctx["destination"],
            date=ctx["departure_date"],
            travelers=ctx["travelers"],
            provider=self.flight_provider,
        )
        return {"transport_options": [opt.model_dump() for opt in results]}
