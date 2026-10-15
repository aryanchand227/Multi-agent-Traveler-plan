"""Train Agent — responsible ONLY for train transportation."""
from __future__ import annotations

from typing import Any

from app.agents.base import BaseAgent
from app.agents.context_builders import build_train_agent_context
from app.graph.state import TravelState
from app.providers.transport.base import TrainProvider
from app.tools.transport_tools import search_train_options


class TrainAgent(BaseAgent):
    def __init__(self, llm_provider, train_provider: TrainProvider):
        super().__init__(llm_provider)
        self.train_provider = train_provider

    @property
    def name(self) -> str:
        return "TrainAgent"

    async def run(self, state: TravelState) -> dict[str, Any]:
        ctx = build_train_agent_context(state)
        results = await search_train_options(
            origin=ctx["origin"],
            destination=ctx["destination"],
            date=ctx["departure_date"],
            travelers=ctx["travelers"],
            provider=self.train_provider,
        )
        return {"transport_options": [opt.model_dump() for opt in results]}
