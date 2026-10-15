"""Tests for Phase 2: LLM and Agent Core."""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, patch

from app.graph.workflow import build_graph
from app.graph.state import TravelState
from app.providers.llm.factory import get_llm_provider
from app.schemas.travel import TravelStyle
from app.agents.intake import IntakeExtraction


@pytest.fixture
def graph():
    # We pass a dummy LLM provider since we will mock the agent methods
    class DummyProvider:
        def get_model_name(self): return "dummy"
        def get_provider_name(self): return "dummy"
        def get_chat_model(self, **kwargs): return None
        def get_structured_model(self, schema, **kwargs): return None
        
    return build_graph(DummyProvider())


def create_initial_state(request: str) -> TravelState:
    return {
        "request_id": "test-req-123",
        "user_id": "test-user",
        "raw_user_request": request,
        "origin": None,
        "destination": None,
        "departure_date": None,
        "return_date": None,
        "duration_days": None,
        "travelers": None,
        "budget": None,
        "currency": "INR",
        "travel_style": TravelStyle.STANDARD,
        "preferred_transport": [],
        "interests": [],
        "clarification_questions": None,
        "clarification_answers": {},
        "is_valid_requirements": False,
        "requires_clarification": False,
        "transport_options": [],
        "accommodation_options": [],
        "activities": [],
        "weather": None,
        "budget_analysis": None,
        "selected_transport": None,
        "selected_accommodation": None,
        "itinerary": None,
        "validation": None,
        "final_plan": None,
        "output_detail": "standard",
        "errors": [],
        "messages": [],
    }


@pytest.mark.asyncio
@patch("app.agents.base.BaseAgent.get_structured_response")
async def test_complete_request(mock_get_structured_response, graph):
    """Test 1: Complete request."""
    request = "Plan a 4-day trip from Hyderabad to Goa for 2 people. Budget is ₹25,000. I prefer trains and like beaches."
    state = create_initial_state(request)
    
    mock_get_structured_response.return_value = IntakeExtraction(
        origin="Hyderabad",
        destination="Goa",
        duration_days=4,
        travelers=2,
        budget=25000.0,
        currency="INR",
        travel_style="budget",
        preferred_transport=["train"],
        interests=["beaches"]
    )
    
    result = await graph.ainvoke(state)
    
    assert result["requires_clarification"] is False
    assert result["origin"].lower() == "hyderabad"
    assert result["destination"].lower() == "goa"
    assert result["duration_days"] == 4
    assert result["travelers"] == 2
    assert result["budget"] == 25000.0
    assert "train" in [t.lower() for t in result["preferred_transport"]]
    assert "beaches" in [i.lower() for i in result["interests"]]


@pytest.mark.asyncio
@patch("app.agents.base.BaseAgent.get_structured_response")
async def test_missing_origin(mock_get_structured_response, graph):
    """Test 2: Missing origin."""
    request = "Plan a 4-day Goa trip for two people."
    state = create_initial_state(request)
    
    mock_get_structured_response.return_value = IntakeExtraction(
        origin=None,
        destination="Goa",
        duration_days=4,
        travelers=2
    )
    
    result = await graph.ainvoke(state)
    
    assert result["requires_clarification"] is True
    assert result["clarification_questions"] is not None
    assert any("origin" in q["field"].lower() for q in result["clarification_questions"])


@pytest.mark.asyncio
@patch("app.agents.base.BaseAgent.get_structured_response")
async def test_missing_travelers(mock_get_structured_response, graph):
    """Test 3: Missing travelers."""
    request = "I want to travel from Hyderabad to Goa from October 10 to October 14."
    state = create_initial_state(request)
    
    mock_get_structured_response.return_value = IntakeExtraction(
        origin="Hyderabad",
        destination="Goa",
        departure_date="2023-10-10",
        return_date="2023-10-14",
        travelers=None
    )
    
    result = await graph.ainvoke(state)
    
    assert result["requires_clarification"] is True
    assert result["clarification_questions"] is not None
    assert any("travelers" in q["field"].lower() or "people" in q["field"].lower() for q in result["clarification_questions"])


@pytest.mark.asyncio
@patch("app.agents.base.BaseAgent.get_structured_response")
async def test_ambiguous_budget(mock_get_structured_response, graph):
    """Test 4: Ambiguous budget."""
    request = "I want a cheap trip from Hyderabad to Goa for 4 days for 2 people."
    state = create_initial_state(request)
    
    mock_get_structured_response.return_value = IntakeExtraction(
        origin="Hyderabad",
        destination="Goa",
        duration_days=4,
        travelers=2,
        travel_style="budget",
        budget=None
    )
    
    result = await graph.ainvoke(state)
    
    assert result["requires_clarification"] is False
    assert result["travel_style"] == TravelStyle.BUDGET
    assert result.get("budget") is None


@pytest.mark.asyncio
@patch("app.agents.base.BaseAgent.get_structured_response")
async def test_luxury_style(mock_get_structured_response, graph):
    """Test 5: Luxury style."""
    request = "Plan a luxury Goa trip from Hyderabad for two people for 5 days."
    state = create_initial_state(request)
    
    mock_get_structured_response.return_value = IntakeExtraction(
        origin="Hyderabad",
        destination="Goa",
        duration_days=5,
        travelers=2,
        travel_style="luxury",
        budget=None
    )
    
    result = await graph.ainvoke(state)
    
    assert result["requires_clarification"] is False
    assert result["travel_style"] == TravelStyle.LUXURY
    assert result.get("budget") is None


@pytest.mark.asyncio
@patch("app.agents.base.BaseAgent.get_structured_response")
async def test_custom_budget(mock_get_structured_response, graph):
    """Test 6: Custom budget."""
    request = "Plan my Goa trip from Hyderabad for 3 days for 2 people with a budget of ₹75,000."
    state = create_initial_state(request)
    
    mock_get_structured_response.return_value = IntakeExtraction(
        origin="Hyderabad",
        destination="Goa",
        duration_days=3,
        travelers=2,
        budget=75000.0,
        currency="INR"
    )
    
    result = await graph.ainvoke(state)
    
    assert result["requires_clarification"] is False
    assert result["budget"] == 75000.0
    assert result["currency"] == "INR"
