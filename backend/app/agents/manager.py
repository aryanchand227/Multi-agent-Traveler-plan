"""Travel Manager Agent — primary orchestrator and project manager.

The TravelManager does NOT perform tasks itself. It:
1. Inspects the current workflow state
2. Loads user preferences from memory (when available)
3. Sets sensible defaults for missing optional fields
4. Marks the workflow as ready for downstream agents
"""
from __future__ import annotations

import logging
from typing import Any

from app.agents.base import BaseAgent
from app.graph.state import TravelState
from app.memory.service import MemoryService

logger = logging.getLogger(__name__)


class TravelManager(BaseAgent):
    """Orchestrates the travel planning workflow.
    
    Responsibilities:
    - Load user preferences from persistent memory
    - Apply defaults where information is missing
    - Set up execution metadata
    - Route to downstream agents via graph edges
    """

    def __init__(self, llm_provider, memory_service: MemoryService | None = None):
        super().__init__(llm_provider=llm_provider)
        self.memory_service = memory_service

    @property
    def name(self) -> str:
        return "TravelManager"

    async def run(self, state: TravelState) -> dict[str, Any]:
        logger.info("TravelManager: Preparing workflow state for agent dispatch.")

        updates: dict[str, Any] = {}

        # --- Load user preferences from persistent memory ---
        user_id = state.get("user_id")
        if user_id and self.memory_service:
            try:
                prefs = await self.memory_service.get_user_preferences(user_id)
                if prefs:
                    logger.info("TravelManager: Loaded user preferences for %s", user_id)
                    # Apply user preferences only where state is missing
                    if not state.get("preferred_transport") and prefs.get("preferred_transport"):
                        pt = prefs["preferred_transport"]
                        updates["preferred_transport"] = [pt] if isinstance(pt, str) else pt
                    if not state.get("travel_style") and prefs.get("travel_style"):
                        updates["travel_style"] = prefs["travel_style"]
                    if not state.get("currency") and prefs.get("default_currency"):
                        updates["currency"] = prefs["default_currency"]
                    if not state.get("output_detail") and prefs.get("default_output_detail"):
                        updates["output_detail"] = prefs["default_output_detail"]
            except Exception as e:
                logger.warning("TravelManager: Failed to load user preferences: %s", e)

        # --- Apply sensible defaults ---
        if not state.get("currency") and "currency" not in updates:
            updates["currency"] = "INR"

        if not state.get("travel_style") and "travel_style" not in updates:
            updates["travel_style"] = "standard"

        # Ensure duration_days is set if dates are present
        duration_days = state.get("duration_days")
        departure_date = state.get("departure_date")
        return_date = state.get("return_date")
        if not duration_days and departure_date and return_date:
            try:
                from datetime import datetime
                dep = datetime.strptime(departure_date, "%Y-%m-%d")
                ret = datetime.strptime(return_date, "%Y-%m-%d")
                computed = (ret - dep).days
                if computed > 0:
                    updates["duration_days"] = computed
            except ValueError:
                pass

        # Ensure return_date is set if duration_days and departure_date are present
        if departure_date and not return_date and duration_days:
            try:
                from datetime import datetime, timedelta
                dep = datetime.strptime(departure_date, "%Y-%m-%d")
                ret = dep + timedelta(days=duration_days)
                updates["return_date"] = ret.strftime("%Y-%m-%d")
            except ValueError:
                pass

        logger.info("TravelManager: Workflow state prepared. Routing to downstream agents.")
        return updates
