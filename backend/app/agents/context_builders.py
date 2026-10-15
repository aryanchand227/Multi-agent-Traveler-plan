"""Agent Context Builders — extracts minimal, relevant context per agent.

Adheres strictly to the Memory Rule (Section 9) and Token Rule (Section 55 & 56),
preventing unbounded state propagation and reducing token overhead.
"""
from __future__ import annotations

from typing import Any
from app.graph.state import TravelState


def build_bus_agent_context(state: TravelState) -> dict[str, Any]:
    """Extract relevant context for BusAgent."""
    return {
        "origin": state.get("origin") or "",
        "destination": state.get("destination") or "",
        "departure_date": state.get("departure_date") or state.get("start_date") or "",
        "travelers": state.get("travelers") or 1,
        "budget": state.get("budget"),
        "transport_preferences": state.get("preferred_transport") or [],
    }


def build_train_agent_context(state: TravelState) -> dict[str, Any]:
    """Extract relevant context for TrainAgent."""
    return {
        "origin": state.get("origin") or "",
        "destination": state.get("destination") or "",
        "departure_date": state.get("departure_date") or state.get("start_date") or "",
        "travelers": state.get("travelers") or 1,
        "budget": state.get("budget"),
        "transport_preferences": state.get("preferred_transport") or [],
    }


def build_flight_agent_context(state: TravelState) -> dict[str, Any]:
    """Extract relevant context for FlightAgent."""
    return {
        "origin": state.get("origin") or "",
        "destination": state.get("destination") or "",
        "departure_date": state.get("departure_date") or state.get("start_date") or "",
        "travelers": state.get("travelers") or 1,
        "budget": state.get("budget"),
        "transport_preferences": state.get("preferred_transport") or [],
    }


def build_accommodation_agent_context(state: TravelState) -> dict[str, Any]:
    """Extract relevant context for AccommodationAgent."""
    duration_days = state.get("duration_days") or 1
    nights = max(1, duration_days - 1)

    check_in = state.get("departure_date") or ""
    check_out = state.get("return_date") or ""
    if check_in and check_out:
        try:
            import datetime
            d1 = datetime.date.fromisoformat(str(check_in).strip()[:10])
            d2 = datetime.date.fromisoformat(str(check_out).strip()[:10])
            diff = (d2 - d1).days
            if diff > 0:
                nights = diff
        except Exception:
            pass

    return {
        "destination": state.get("destination") or "",
        "check_in": check_in,
        "check_out": check_out,
        "duration_days": duration_days,
        "nights": nights,
        "travelers": state.get("travelers") or 1,
        "budget": state.get("budget"),
        "travel_style": str(state.get("travel_style") or "standard").lower(),
    }


def build_destination_agent_context(state: TravelState) -> dict[str, Any]:
    """Extract relevant context for DestinationAgent."""
    return {
        "destination": state.get("destination") or "",
        "interests": state.get("interests") or [],
        "travel_style": str(state.get("travel_style") or "standard").lower(),
        "duration_days": state.get("duration_days") or 1,
    }


def build_weather_agent_context(state: TravelState) -> dict[str, Any]:
    """Extract relevant context for WeatherAgent."""
    return {
        "destination": state.get("destination") or "",
        "start_date": state.get("departure_date") or "",
        "end_date": state.get("return_date") or "",
    }


def build_budget_agent_context(state: TravelState) -> dict[str, Any]:
    """Extract relevant context for BudgetAgent."""
    return {
        "travelers": state.get("travelers") or 1,
        "duration_days": state.get("duration_days") or 1,
        "travel_style": str(state.get("travel_style") or "standard").lower(),
        "budget": state.get("budget"),
        "currency": state.get("currency") or "INR",
        "transport_options": state.get("transport_options") or [],
        "selected_transport": state.get("selected_transport"),
        "accommodation_options": state.get("accommodation_options") or [],
        "selected_accommodation": state.get("selected_accommodation"),
    }


def build_itinerary_agent_context(state: TravelState) -> dict[str, Any]:
    """Extract relevant context for ItineraryAgent."""
    return {
        "origin": state.get("origin") or "",
        "destination": state.get("destination") or "",
        "duration_days": state.get("duration_days") or 1,
        "travelers": state.get("travelers") or 1,
        "travel_style": str(state.get("travel_style") or "standard").lower(),
        "interests": state.get("interests") or [],
        "activities": state.get("activities") or [],
        "weather": state.get("weather"),
        "selected_transport": state.get("selected_transport"),
        "selected_accommodation": state.get("selected_accommodation"),
        "budget_analysis": state.get("budget_analysis"),
    }
