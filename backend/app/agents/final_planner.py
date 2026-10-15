"""Final Planner Agent — synthesizes the complete travel plan."""
from __future__ import annotations

import datetime
from typing import Any

from app.agents.base import BaseAgent
from app.graph.state import TravelState
from app.core.config import get_settings
from app.core.serialization import to_json_safe


class FinalPlannerAgent(BaseAgent):
    """Assembles all agent outputs into the final travel plan."""

    @property
    def name(self) -> str:
        return "FinalPlannerAgent"

    async def run(self, state: TravelState) -> dict[str, Any]:
        settings = get_settings()
        output_detail = str(state.get("output_detail", "standard")).lower()
        token_limits = settings.output_token_limits
        max_tokens = token_limits.get(output_detail, 1200)

        origin = state.get("origin", "")
        destination = state.get("destination", "")
        travelers = state.get("travelers") or 1
        duration_days = state.get("duration_days") or 1
        travel_style = str(state.get("travel_style", "standard"))
        budget = state.get("budget")
        currency = state.get("currency", "INR")
        interests = state.get("interests", [])

        # Build trip summary
        trip_summary = {
            "request_id": state.get("request_id", ""),
            "origin": origin,
            "destination": destination,
            "departure_date": state.get("departure_date"),
            "return_date": state.get("return_date"),
            "travelers": travelers,
            "duration_days": duration_days,
            "budget": budget,
            "currency": currency,
            "travel_style": travel_style,
            "interests": interests,
        }

        # Selected transport
        selected_transport = state.get("selected_transport")
        transport_options = state.get("transport_options", [])
        transportation = None
        if selected_transport or transport_options:
            sel = selected_transport or (transport_options[0] if transport_options else None)
            alternatives = [o for o in transport_options if o.get("id") != (sel or {}).get("id")]
            cheapest = min(transport_options, key=lambda x: x.get("total_price", float("inf")), default=None) if transport_options else None
            fastest = min(transport_options, key=lambda x: x.get("duration_minutes", float("inf")), default=None) if transport_options else None
            transportation = {
                "selected": sel,
                "alternatives": alternatives[:5],
                "cheapest": cheapest,
                "fastest": fastest,
                "recommended": sel,
                "recommendation_reason": f"Best match for {travel_style} travel style",
            }

        # Selected accommodation
        accommodation_options = state.get("accommodation_options", [])
        selected_accommodation = state.get("selected_accommodation")
        accommodation = selected_accommodation or (accommodation_options[0] if accommodation_options else None)
        accommodation_alternatives = [o for o in accommodation_options if o.get("id") != (accommodation or {}).get("id")]

        # Activities
        activities = state.get("activities", [])

        # Weather
        weather = state.get("weather")

        # Budget
        budget_analysis = state.get("budget_analysis")

        # Itinerary
        itinerary = state.get("itinerary")

        # Validation
        validation = state.get("validation")

        # Data sources
        data_sources = [{"provider": "MockTransport", "source_type": "mock", "retrieved_at": datetime.datetime.now(datetime.timezone.utc).isoformat()}]
        if accommodation:
            data_sources.append({"provider": "MockAccommodation", "source_type": "mock", "retrieved_at": datetime.datetime.now(datetime.timezone.utc).isoformat()})
        if weather:
            data_sources.append({"provider": "MockWeather", "source_type": "mock", "retrieved_at": datetime.datetime.now(datetime.timezone.utc).isoformat()})

        # Warnings
        plan_warnings = []
        if validation:
            plan_warnings.extend(validation.get("warnings", []))
        if budget_analysis and budget_analysis.get("status") == "over_budget":
            plan_warnings.append("Trip is over budget. Consider adjustments.")

        # Generate human-readable summary using LLM
        human_summary = await self._generate_summary(
            state, output_detail, max_tokens
        )

        final_plan = {
            "trip_summary": trip_summary,
            "transportation": transportation,
            "accommodation": accommodation,
            "accommodation_alternatives": accommodation_alternatives[:3],
            "activities": activities,
            "weather": weather,
            "budget": budget_analysis,
            "itinerary": itinerary,
            "decision_factors": self._get_decision_factors(state),
            "warnings": plan_warnings,
            "data_sources": data_sources,
            "validation": validation,
            "human_readable_summary": human_summary,
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }

        return {"final_plan": to_json_safe(final_plan)}

    async def _generate_summary(self, state: TravelState, detail_level: str, max_tokens: int) -> str:
        """Generate a human-readable summary using the LLM."""
        origin = state.get("origin", "")
        destination = state.get("destination", "")
        duration = state.get("duration_days", 0)
        travelers = state.get("travelers", 1)
        style = state.get("travel_style", "standard")
        budget_analysis = state.get("budget_analysis")
        selected_transport = state.get("selected_transport")
        itinerary = state.get("itinerary")

        context = f"Trip: {origin} → {destination}, {duration} days, {travelers} people, {style} style.\n"
        if selected_transport:
            context += f"Transport: {selected_transport.get('provider', 'N/A')} ({selected_transport.get('mode', 'N/A')})\n"
        if budget_analysis:
            context += f"Total estimated cost: ₹{budget_analysis.get('total', 0):,.0f}\n"

        detail_instructions = {
            "brief": "Write a concise 2-3 sentence summary.",
            "standard": "Write a clear 1-2 paragraph summary covering transport, accommodation, key activities, and budget.",
            "detailed": "Write a comprehensive summary covering all aspects: transport, accommodation, daily itinerary highlights, budget breakdown, and practical tips.",
        }
        instruction = detail_instructions.get(detail_level, detail_instructions["standard"])

        system_prompt = (
            "You are a travel assistant summarizing a complete travel plan. "
            "Use Indian Rupees (₹). Be factual — only mention data that was provided. "
            f"{instruction}"
        )

        try:
            return await self.get_text_response(
                system_prompt=system_prompt,
                user_prompt=context,
                temperature=0.5,
            )
        except Exception:
            return f"Your {duration}-day {style} trip from {origin} to {destination} for {travelers} traveler(s) has been planned."

    def _get_decision_factors(self, state: TravelState) -> list[str]:
        """Build a list of key decision factors."""
        factors = []
        style = str(state.get("travel_style", "standard"))
        factors.append(f"Travel style: {style}")

        preferred = state.get("preferred_transport", [])
        if preferred:
            factors.append(f"Preferred transport: {', '.join(preferred)}")

        budget = state.get("budget")
        if budget:
            factors.append(f"Budget constraint: ₹{budget:,.0f}")

        interests = state.get("interests", [])
        if interests:
            factors.append(f"Interests: {', '.join(interests)}")

        return factors
