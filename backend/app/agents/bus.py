"""Bus Agent — responsible ONLY for bus transportation."""
from __future__ import annotations

from typing import Any

from app.agents.base import BaseAgent
from app.agents.context_builders import build_bus_agent_context
from app.graph.state import TravelState
from app.providers.transport.base import BusProvider
from app.tools.transport_tools import search_bus_options


class BusAgent(BaseAgent):
    def __init__(self, llm_provider, bus_provider: BusProvider):
        super().__init__(llm_provider)
        self.bus_provider = bus_provider

    @property
    def name(self) -> str:
        return "BusAgent"

    async def run(self, state: TravelState) -> dict[str, Any]:
        ctx = build_bus_agent_context(state)
        results = await search_bus_options(
            origin=ctx["origin"],
            destination=ctx["destination"],
            date=ctx["departure_date"],
            travelers=ctx["travelers"],
            provider=self.bus_provider,
        )
        return {"transport_options": [opt.model_dump() for opt in results]}
