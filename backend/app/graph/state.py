"""LangGraph state definition."""
from __future__ import annotations

import operator
from typing import Annotated, Any, TypedDict

from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field

from app.schemas.travel import TravelStyle, OutputDetail


def merge_dicts(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    """Merge two dictionaries."""
    a = a or {}
    b = b or {}
    return {**a, **b}


class TravelState(TypedDict):
    """The central state for the travel planning workflow."""
    
    # Core identifiers
    request_id: str
    user_id: str
    raw_user_request: str
    
    # Extracted requirements (from Intake)
    origin: str | None
    destination: str | None
    departure_date: str | None
    return_date: str | None
    duration_days: int | None
    travelers: int | None
    budget: float | None
    currency: str
    travel_style: TravelStyle
    preferred_transport: list[str]
    interests: list[str]
    
    # Clarification
    clarification_questions: list[dict[str, Any]] | None
    clarification_answers: Annotated[dict[str, str], merge_dicts]
    
    # Workflow flags
    is_valid_requirements: bool
    requires_clarification: bool
    
    # Results (populated in later phases)
    transport_options: list[dict[str, Any]]
    accommodation_options: list[dict[str, Any]]
    activities: list[dict[str, Any]]
    weather: dict[str, Any] | None
    
    budget_analysis: dict[str, Any] | None
    selected_transport: dict[str, Any] | None
    selected_accommodation: dict[str, Any] | None
    
    itinerary: dict[str, Any] | None
    validation: dict[str, Any] | None
    
    final_plan: dict[str, Any] | None
    output_detail: OutputDetail
    
    # Error handling
    errors: Annotated[list[str], operator.add]
    
    # LangGraph messaging
    messages: Annotated[list[BaseMessage], operator.add]
