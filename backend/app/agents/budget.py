"""Budget Agent — deterministic budget calculations, no LLM fabrication."""
from __future__ import annotations

from typing import Any

from app.agents.base import BaseAgent
from app.graph.state import TravelState
from app.schemas.budget import BudgetBreakdown, BudgetStatus, BudgetCategory
from app.core.config import BUDGET_THRESHOLDS


# Default daily cost estimates by travel style (INR per person per day)
DAILY_COST_ESTIMATES: dict[str, dict[str, float]] = {
    "budget": {
        "food": 500,
        "local_transport": 200,
        "activities": 300,
        "miscellaneous": 200,
    },
    "standard": {
        "food": 1000,
        "local_transport": 500,
        "activities": 800,
        "miscellaneous": 400,
    },
    "premium": {
        "food": 2000,
        "local_transport": 1000,
        "activities": 1500,
        "miscellaneous": 700,
    },
    "luxury": {
        "food": 4000,
        "local_transport": 2000,
        "activities": 3000,
        "miscellaneous": 1500,
    },
}


class BudgetAgent(BaseAgent):
    """Calculates budget breakdown using deterministic Python arithmetic."""

    @property
    def name(self) -> str:
        return "BudgetAgent"

    async def run(self, state: TravelState) -> dict[str, Any]:
        travelers = state.get("travelers") or 1
        duration_days = state.get("duration_days") or 1
        travel_style = str(state.get("travel_style", "standard")).lower()
        budget = state.get("budget")
        currency = state.get("currency", "INR")

        if travel_style not in DAILY_COST_ESTIMATES:
            travel_style = "standard"

        daily_rates = DAILY_COST_ESTIMATES[travel_style]

        # --- Transport cost ---
        transport_options = state.get("transport_options", [])
        selected_transport = state.get("selected_transport")
        if selected_transport:
            transport_cost = float(selected_transport.get("total_price", 0))
        elif transport_options:
            # Use cheapest option as estimate
            transport_cost = min(float(o.get("total_price", 0)) for o in transport_options)
        else:
            transport_cost = 0.0

        # --- Accommodation cost ---
        accommodation_options = state.get("accommodation_options", [])
        selected_accommodation = state.get("selected_accommodation")
        if selected_accommodation:
            accommodation_cost = float(selected_accommodation.get("total_price", 0))
        elif accommodation_options:
            # Use cheapest matching style
            accommodation_cost = min(float(o.get("total_price", 0)) for o in accommodation_options)
        else:
            accommodation_cost = daily_rates.get("food", 0) * duration_days * travelers * 0.5  # rough estimate

        # --- Daily costs ---
        food_cost = daily_rates["food"] * duration_days * travelers
        local_transport_cost = daily_rates["local_transport"] * duration_days * travelers
        activities_cost = daily_rates["activities"] * duration_days * travelers
        misc_cost = daily_rates["miscellaneous"] * duration_days * travelers

        total = transport_cost + accommodation_cost + food_cost + local_transport_cost + activities_cost + misc_cost
        per_person = total / travelers if travelers > 0 else total

        # --- Budget status ---
        remaining = None
        status = BudgetStatus.WITHIN_BUDGET
        warnings = []
        suggestions = []

        if budget and budget > 0:
            remaining = budget - total
            ratio = total / budget
            if ratio <= BUDGET_THRESHOLDS["within_budget"]:
                status = BudgetStatus.WITHIN_BUDGET
            elif ratio <= BUDGET_THRESHOLDS["over_budget"]:
                status = BudgetStatus.NEAR_BUDGET
                warnings.append(f"You are using {ratio:.0%} of your budget.")
            else:
                status = BudgetStatus.OVER_BUDGET
                overage = total - budget
                warnings.append(f"Over budget by {currency} {overage:,.0f}.")
                suggestions.append("Consider switching to a lower accommodation tier.")
                suggestions.append("Consider bus/train instead of flight to save on transport.")
                suggestions.append("Reduce activity spending or duration.")

        categories = [
            BudgetCategory(category="Transportation", estimated_cost=transport_cost),
            BudgetCategory(category="Accommodation", estimated_cost=accommodation_cost),
            BudgetCategory(category="Food & Dining", estimated_cost=food_cost),
            BudgetCategory(category="Local Transport", estimated_cost=local_transport_cost),
            BudgetCategory(category="Activities", estimated_cost=activities_cost),
            BudgetCategory(category="Miscellaneous", estimated_cost=misc_cost),
        ]

        breakdown = BudgetBreakdown(
            transportation=transport_cost,
            accommodation=accommodation_cost,
            food=food_cost,
            local_transport=local_transport_cost,
            activities=activities_cost,
            miscellaneous=misc_cost,
            total=total,
            budget=budget,
            remaining=remaining,
            currency=currency,
            status=status,
            per_person_total=per_person,
            categories=categories,
            optimization_suggestions=suggestions,
            warnings=warnings,
        )

        return {"budget_analysis": breakdown.model_dump()}
