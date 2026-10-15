"""Itinerary Agent — builds a day-by-day schedule using LLM synthesis."""
from __future__ import annotations

from typing import Any, Optional, List

from pydantic import BaseModel, Field

from app.agents.base import BaseAgent
from app.graph.state import TravelState


class ItineraryItemOutput(BaseModel):
    time_start: Optional[str] = Field(default=None, description="Start time HH:MM")
    time_end: Optional[str] = Field(default=None, description="End time HH:MM")
    title: str = Field(description="Activity/event title")
    description: Optional[str] = Field(default=None, description="Brief description")
    item_type: str = Field(description="transport|accommodation|activity|meal|rest|free_time")
    estimated_cost: Optional[float] = Field(default=None, description="Cost in local currency")
    location: Optional[str] = Field(default=None, description="Location name")


class ItineraryDayOutput(BaseModel):
    day_number: int = Field(description="Day number starting from 1")
    date: Optional[str] = Field(default=None, description="Date YYYY-MM-DD")
    theme: Optional[str] = Field(default=None, description="Theme for the day")
    items: List[ItineraryItemOutput] = Field(default_factory=list, description="Schedule items")


class ItineraryOutput(BaseModel):
    title: Optional[str] = Field(default=None, description="Trip title")
    summary: Optional[str] = Field(default=None, description="Brief trip summary")
    total_days: int = Field(description="Total number of days")
    days: List[ItineraryDayOutput] = Field(default_factory=list, description="Day-by-day itinerary")


class ItineraryAgent(BaseAgent):
    """Builds a realistic day-by-day itinerary using available data + LLM."""

    @property
    def name(self) -> str:
        return "ItineraryAgent"

    async def run(self, state: TravelState) -> dict[str, Any]:
        origin = state.get("origin", "Origin")
        destination = state.get("destination", "Destination")
        duration_days = state.get("duration_days") or 3
        travelers = state.get("travelers") or 1
        travel_style = str(state.get("travel_style", "standard"))
        interests = state.get("interests", [])
        activities = state.get("activities", [])
        weather = state.get("weather")
        selected_transport = state.get("selected_transport")
        selected_accommodation = state.get("selected_accommodation")
        budget_analysis = state.get("budget_analysis")

        # Build context for LLM
        context_parts = [
            f"Trip: {origin} to {destination}, {duration_days} days, {travelers} travelers",
            f"Style: {travel_style}",
        ]
        if interests:
            context_parts.append(f"Interests: {', '.join(interests)}")
        if selected_transport:
            context_parts.append(f"Transport: {selected_transport.get('provider', 'N/A')} ({selected_transport.get('mode', 'N/A')}), "
                                 f"departs {selected_transport.get('departure_time', 'TBD')}")
        if selected_accommodation:
            context_parts.append(f"Accommodation: {selected_accommodation.get('name', 'N/A')}")
        if activities:
            act_names = [a.get("name", "") for a in activities[:10]]
            context_parts.append(f"Available activities: {', '.join(act_names)}")
        if weather:
            days_weather = weather.get("days", [])
            weather_summary = "; ".join(
                f"Day {i+1}: {d.get('condition', 'clear')}" for i, d in enumerate(days_weather[:duration_days])
            )
            context_parts.append(f"Weather: {weather_summary}")
        if budget_analysis:
            context_parts.append(f"Daily activity budget per person: ~₹{budget_analysis.get('activities', 0) / max(duration_days * travelers, 1):.0f}")

        context = "\n".join(context_parts)

        system_prompt = (
            "You are an expert travel itinerary planner for Indian travel. "
            "Create a realistic, detailed day-by-day itinerary. "
            "Include travel time on Day 1, check-in, meals, activities, and return travel on the last day. "
            "Use realistic timing. Include free time and rest. "
            "Do NOT fabricate costs — use the activity costs from the provided data. "
            "Do NOT fabricate transport/hotel names — use what was provided."
        )

        user_prompt = f"Create a {duration_days}-day itinerary based on this context:\n\n{context}"

        try:
            result = await self.get_structured_response(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_model=ItineraryOutput,
                temperature=0.5,
            )
            return {"itinerary": result.model_dump()}
        except Exception as e:
            return {
                "itinerary": {
                    "title": f"{origin} to {destination} Trip",
                    "summary": f"A {duration_days}-day {travel_style} trip",
                    "total_days": duration_days,
                    "days": [],
                },
                "errors": [f"ItineraryAgent error: {str(e)}"],
            }
