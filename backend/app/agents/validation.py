"""Validation Agent — validates the complete travel plan for consistency."""
from __future__ import annotations

from typing import Any

from app.agents.base import BaseAgent
from app.graph.state import TravelState


class ValidationAgent(BaseAgent):
    """Deterministic validation of the entire travel plan."""

    @property
    def name(self) -> str:
        return "ValidationAgent"

    async def run(self, state: TravelState) -> dict[str, Any]:
        errors: list[str] = []
        warnings: list[str] = []
        checks_passed: list[str] = []

        # --- 1. Required fields ---
        origin = state.get("origin")
        destination = state.get("destination")
        travelers = state.get("travelers")
        duration_days = state.get("duration_days")

        if not origin:
            errors.append("Origin is missing.")
        else:
            checks_passed.append("Origin is set.")

        if not destination:
            errors.append("Destination is missing.")
        else:
            checks_passed.append("Destination is set.")

        if not travelers or travelers < 1:
            errors.append("Number of travelers is missing or invalid.")
        else:
            checks_passed.append(f"Travelers: {travelers}")

        if not duration_days or duration_days < 1:
            errors.append("Duration is missing or invalid.")
        else:
            checks_passed.append(f"Duration: {duration_days} days")

        # --- 2. Transport validation ---
        transport_options = state.get("transport_options", [])
        selected_transport = state.get("selected_transport")

        if not transport_options:
            warnings.append("No transport options were found.")
        else:
            checks_passed.append(f"Transport: {len(transport_options)} options available.")

        if selected_transport:
            tp = selected_transport.get("total_price", 0)
            if tp <= 0:
                warnings.append("Selected transport has zero/negative price.")
            checks_passed.append(f"Selected transport: {selected_transport.get('provider', 'N/A')}")

        # --- 3. Accommodation validation ---
        accommodation_options = state.get("accommodation_options", [])
        selected_accommodation = state.get("selected_accommodation")

        if not accommodation_options:
            warnings.append("No accommodation options were found.")
        else:
            checks_passed.append(f"Accommodation: {len(accommodation_options)} options available.")

        if selected_accommodation:
            checks_passed.append(f"Selected accommodation: {selected_accommodation.get('name', 'N/A')}")

        # --- 4. Budget validation ---
        budget = state.get("budget")
        budget_analysis = state.get("budget_analysis")

        if budget_analysis:
            total_cost = budget_analysis.get("total", 0)
            if budget and total_cost > budget:
                overage = total_cost - budget
                currency = state.get("currency", "INR")
                warnings.append(f"Total estimated cost ({currency} {total_cost:,.0f}) exceeds budget ({currency} {budget:,.0f}) by {currency} {overage:,.0f}.")
            else:
                checks_passed.append("Budget is within limits.")
        else:
            warnings.append("Budget analysis is not available.")

        # --- 5. Itinerary validation ---
        itinerary = state.get("itinerary")
        if itinerary:
            itinerary_days = itinerary.get("days", [])
            if len(itinerary_days) != (duration_days or 0):
                warnings.append(f"Itinerary has {len(itinerary_days)} days but trip is {duration_days} days.")
            else:
                checks_passed.append(f"Itinerary covers all {duration_days} days.")
        else:
            warnings.append("No itinerary generated.")

        # --- 6. Date consistency ---
        departure_date = state.get("departure_date")
        return_date = state.get("return_date")
        if departure_date and return_date:
            try:
                from datetime import datetime
                dep = datetime.strptime(departure_date, "%Y-%m-%d")
                ret = datetime.strptime(return_date, "%Y-%m-%d")
                if ret <= dep:
                    errors.append("Return date must be after departure date.")
                else:
                    computed_days = (ret - dep).days
                    if duration_days and abs(computed_days - duration_days) > 1:
                        warnings.append(f"Date range ({computed_days} days) doesn't match duration_days ({duration_days}).")
                    checks_passed.append("Date range is valid.")
            except ValueError:
                warnings.append("Could not parse departure/return dates.")

        is_valid = len(errors) == 0

        validation_result = {
            "is_valid": is_valid,
            "errors": errors,
            "warnings": warnings,
            "checks_passed": checks_passed,
        }

        return {"validation": validation_result}
