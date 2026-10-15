from __future__ import annotations
import datetime
from enum import Enum
from pydantic import BaseModel, Field
from app.schemas.final_plan import FinalTravelPlan

class TravelStyle(str, Enum):
    BUDGET = "budget"
    STANDARD = "standard"
    PREMIUM = "premium"
    LUXURY = "luxury"
    CUSTOM = "custom"

class OutputDetail(str, Enum):
    BRIEF = "brief"
    STANDARD = "standard"
    DETAILED = "detailed"

class TravelRunStatus(str, Enum):
    PENDING = "pending"
    CLARIFYING = "clarifying"
    PLANNING = "planning"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TravelPlanRequest(BaseModel):
    """Request to create a new travel plan."""
    raw_request: str | None = Field(None, description="Natural language travel request")
    origin: str | None = None
    destination: str | None = None
    departure_date: str | None = None
    return_date: str | None = None
    travelers: int | None = Field(None, ge=1, le=20)
    budget: float | None = Field(None, ge=0)
    currency: str = "INR"
    travel_style: TravelStyle = TravelStyle.STANDARD
    preferred_transport: list[str] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)
    accommodation_preference: str | None = None
    output_detail: OutputDetail = OutputDetail.STANDARD
    additional_requirements: str | None = None

class ClarificationResponse(BaseModel):
    """User's response to clarification questions."""
    request_id: str
    responses: dict[str, str]

class ClarificationQuestion(BaseModel):
    field: str
    question: str
    required: bool = True
    options: list[str] | None = None

class TravelRunResponse(BaseModel):
    """Status of a travel planning run."""
    request_id: str
    run_id: str
    status: TravelRunStatus
    started_at: datetime.datetime | None = None
    completed_at: datetime.datetime | None = None
    error: str | None = None
    clarification_questions: list[ClarificationQuestion] | None = None
    final_plan: FinalTravelPlan | None = None

class ReplanRequest(BaseModel):
    """Request to modify an existing plan."""
    message: str
    changes: dict[str, object] | None = None
