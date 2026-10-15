"""Complete LangGraph workflow for the travel planning pipeline."""
from __future__ import annotations

from langgraph.graph import StateGraph, START, END

from app.graph.state import TravelState
from app.agents.intake import IntakeAgent
from app.agents.clarification import ClarificationAgent
from app.agents.manager import TravelManager
from app.agents.transport_supervisor import TransportSupervisor
from app.agents.accommodation import AccommodationAgent
from app.agents.destination import DestinationAgent
from app.agents.weather import WeatherAgent as WeatherAgentCls
from app.agents.budget import BudgetAgent
from app.agents.itinerary import ItineraryAgent
from app.agents.validation import ValidationAgent
from app.agents.final_planner import FinalPlannerAgent

from app.providers.llm.base import LLMProvider
from app.providers.transport.base import BusProvider, TrainProvider, FlightProvider
from app.providers.accommodation.base import AccommodationProvider
from app.providers.destination.base import DestinationProvider
from app.providers.weather.base import WeatherProvider


def route_after_clarification(state: TravelState) -> str:
    """Route based on whether clarification is needed."""
    if state.get("requires_clarification"):
        return END
    return "manager"


def build_graph(
    llm_provider: LLMProvider,
    bus_provider: BusProvider | None = None,
    train_provider: TrainProvider | None = None,
    flight_provider: FlightProvider | None = None,
    accommodation_provider: AccommodationProvider | None = None,
    destination_provider: DestinationProvider | None = None,
    weather_provider: WeatherProvider | None = None,
) -> StateGraph:
    """Build the complete travel planning workflow graph.
    
    If providers are not supplied, mock providers are used.
    """
    # Lazy-import mock providers only when needed
    if bus_provider is None:
        from app.providers.transport.mock_bus import MockBusProvider
        bus_provider = MockBusProvider()
    if train_provider is None:
        from app.providers.transport.mock_train import MockTrainProvider
        train_provider = MockTrainProvider()
    if flight_provider is None:
        from app.providers.transport.mock_flight import MockFlightProvider
        flight_provider = MockFlightProvider()
    if accommodation_provider is None:
        from app.providers.accommodation.mock import MockAccommodationProvider
        accommodation_provider = MockAccommodationProvider()
    if destination_provider is None:
        from app.providers.destination.mock import MockDestinationProvider
        destination_provider = MockDestinationProvider()
    if weather_provider is None:
        from app.providers.weather.mock import MockWeatherProvider
        weather_provider = MockWeatherProvider()

    # Create agent instances
    intake = IntakeAgent(llm_provider)
    clarification = ClarificationAgent(llm_provider)
    manager = TravelManager(llm_provider)
    transport_supervisor = TransportSupervisor(
        llm_provider, bus_provider, train_provider, flight_provider
    )
    accommodation_agent = AccommodationAgent(llm_provider, accommodation_provider)
    destination_agent = DestinationAgent(llm_provider, destination_provider)
    weather_agent = WeatherAgentCls(llm_provider, weather_provider)
    budget_agent = BudgetAgent(llm_provider)
    itinerary_agent = ItineraryAgent(llm_provider)
    validation_agent = ValidationAgent(llm_provider)
    final_planner = FinalPlannerAgent(llm_provider)

    # Build the graph
    workflow = StateGraph(TravelState)

    # Add all nodes
    workflow.add_node("intake", intake.run)
    workflow.add_node("clarification", clarification.run)
    workflow.add_node("manager", manager.run)
    workflow.add_node("transport", transport_supervisor.run)
    workflow.add_node("accommodation", accommodation_agent.run)
    workflow.add_node("destination", destination_agent.run)
    workflow.add_node("weather", weather_agent.run)
    workflow.add_node("budget", budget_agent.run)
    workflow.add_node("itinerary", itinerary_agent.run)
    workflow.add_node("validation", validation_agent.run)
    workflow.add_node("final_planner", final_planner.run)

    # Define edges
    # Phase 1: Intake → Clarification → (conditional) → Manager
    workflow.add_edge(START, "intake")
    workflow.add_edge("intake", "clarification")
    workflow.add_conditional_edges(
        "clarification",
        route_after_clarification,
        {END: END, "manager": "manager"},
    )

    # Phase 2: Manager → Transport + Accommodation + Destination + Weather (parallel-ish via sequential)
    workflow.add_edge("manager", "transport")
    workflow.add_edge("transport", "accommodation")
    workflow.add_edge("accommodation", "destination")
    workflow.add_edge("destination", "weather")

    # Phase 3: Weather → Budget → Itinerary → Validation → Final Planner → END
    workflow.add_edge("weather", "budget")
    workflow.add_edge("budget", "itinerary")
    workflow.add_edge("itinerary", "validation")
    workflow.add_edge("validation", "final_planner")
    workflow.add_edge("final_planner", END)

    return workflow.compile()
