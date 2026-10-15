"""Accommodation Agent — finds and selects accommodation options."""
from __future__ import annotations

from typing import Any

from app.agents.base import BaseAgent
from app.agents.context_builders import build_accommodation_agent_context
from app.providers.llm.base import LLMProvider
from app.providers.accommodation.base import AccommodationProvider
from app.graph.state import TravelState
from app.tools.accommodation_tools import search_hotels


class AccommodationAgent(BaseAgent):
    """Agent for finding and selecting accommodation."""

    def __init__(self, llm_provider: LLMProvider, accommodation_provider: AccommodationProvider):
        super().__init__(llm_provider)
        self.accommodation_provider = accommodation_provider

    @property
    def name(self) -> str:
        return "AccommodationAgent"

    async def run(self, state: TravelState) -> dict[str, Any]:
        """Search for accommodation options based on state."""
        ctx = build_accommodation_agent_context(state)

        if not ctx["destination"] or not ctx["check_in"] or not ctx["check_out"]:
            return {"errors": ["Missing destination or dates for accommodation search."]}

        # Calculate budget per night based on travel style allocation
        budget_per_night = None
        budget = ctx["budget"]
        travelers = ctx["travelers"]
        nights = ctx["nights"]
        if budget and travelers:
            try:
                # Allocate ~30% of total budget to accommodation
                budget_per_night = (float(budget) * 0.3) / nights
            except (ValueError, ZeroDivisionError):
                pass

        results = await search_hotels(
            destination=ctx["destination"],
            check_in=ctx["check_in"],
            check_out=ctx["check_out"],
            travelers=travelers,
            budget_per_night=budget_per_night,
            travel_style=ctx["travel_style"],
            provider=self.accommodation_provider,
        )

        options_data = [opt.model_dump() for opt in results]

        # Select the best matching accommodation based on travel style
        selected = None
        if options_data:
            selected = options_data[0]  # Results are pre-sorted by style match from provider

        return {
            "accommodation_options": options_data,
            "selected_accommodation": selected,
        }
