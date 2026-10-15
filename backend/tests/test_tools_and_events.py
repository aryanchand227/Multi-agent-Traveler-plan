"""Unit tests for tools, context builders, and event service."""
import pytest
from app.tools.transport_tools import (
    search_bus_options,
    search_train_options,
    search_flight_options,
)
from app.tools.accommodation_tools import search_hotels
from app.tools.destination_tools import search_attractions
from app.tools.weather_tools import get_weather
from app.tools.budget_tools import calculate_per_person_cost, calculate_budget_utilization
from app.agents.context_builders import (
    build_bus_agent_context,
    build_train_agent_context,
    build_flight_agent_context,
    build_accommodation_agent_context,
)
from app.services.event_service import EventService, AgentEvent
from app.schemas.transport import TransportMode


@pytest.mark.asyncio
async def test_transport_tools():
    """Verify transport search tools return valid options."""
    buses = await search_bus_options("Hyderabad", "Goa", date="2026-10-01", travelers=2)
    assert len(buses) > 0
    assert all(b.mode == TransportMode.BUS for b in buses)

    trains = await search_train_options("Hyderabad", "Goa", date="2026-10-01", travelers=2)
    assert len(trains) > 0
    assert all(t.mode == TransportMode.TRAIN for t in trains)

    flights = await search_flight_options("Hyderabad", "Goa", date="2026-10-01", travelers=2)
    assert len(flights) > 0
    assert all(f.mode == TransportMode.FLIGHT for f in flights)


@pytest.mark.asyncio
async def test_accommodation_tools():
    """Verify accommodation search returns options."""
    hotels = await search_hotels(
        destination="Goa",
        check_in="2026-10-01",
        check_out="2026-10-04",
        travelers=2,
    )
    assert len(hotels) > 0
    assert hotels[0].total_price > 0


@pytest.mark.asyncio
async def test_destination_and_weather_tools():
    """Verify destination attractions and weather tools."""
    activities = await search_attractions(
        destination="Goa",
        interests=["beach", "culture"],
        travel_style="standard",
        days=3,
    )
    assert len(activities) > 0

    weather = await get_weather("Goa", start_date="2026-10-01", end_date="2026-10-04")
    assert weather.destination.lower() == "goa"
    assert len(weather.days) > 0


def test_budget_tools():
    """Verify budget calculations."""
    per_person = calculate_per_person_cost(12000.0, 3)
    assert per_person == 4000.0

    utilization = calculate_budget_utilization(18000.0, 20000.0)
    assert utilization["status"] == "within_budget"
    assert utilization["remaining"] == 2000.0

    over = calculate_budget_utilization(25000.0, 20000.0)
    assert over["status"] == "over_budget"


def test_context_builders():
    """Verify context builders isolate state."""
    state = {
        "origin": "Hyderabad",
        "destination": "Goa",
        "departure_date": "2026-10-01",
        "return_date": "2026-10-05",
        "duration_days": 4,
        "travelers": 2,
        "travel_style": "standard",
        "budget": 25000.0,
        "interests": ["beaches"],
    }
    bus_ctx = build_bus_agent_context(state)
    assert bus_ctx["origin"] == "Hyderabad"
    assert bus_ctx["departure_date"] == "2026-10-01"

    hotel_ctx = build_accommodation_agent_context(state)
    assert hotel_ctx["destination"] == "Goa"
    assert hotel_ctx["nights"] == 4


@pytest.mark.asyncio
async def test_event_service():
    """Verify event service pub-sub."""
    service = EventService()
    req_id = "test-req-event"

    service.emit_started(req_id, "test_agent", "Working")
    service.emit_completed(req_id, "test_agent", "Done")
    service.mark_complete(req_id)

    events = service.get_events(req_id)
    assert len(events) == 3
    assert events[0].agent_name == "test_agent"
    assert events[0].event_type == "running"
    assert events[1].event_type == "completed"
    assert events[2].event_type == "complete"
