from __future__ import annotations
from enum import Enum
from pydantic import BaseModel, Field

class BudgetStatus(str, Enum):
    WITHIN_BUDGET = "within_budget"
    NEAR_BUDGET = "near_budget"
    OVER_BUDGET = "over_budget"

class BudgetCategory(BaseModel):
    category: str
    estimated_cost: float
    notes: str | None = None

class BudgetBreakdown(BaseModel):
    transportation: float = 0
    accommodation: float = 0
    food: float = 0
    activities: float = 0
    local_transport: float = 0
    miscellaneous: float = 0
    total: float = 0
    budget: float | None = None
    remaining: float | None = None
    currency: str = "INR"
    status: BudgetStatus = BudgetStatus.WITHIN_BUDGET
    per_person_total: float = 0
    categories: list[BudgetCategory] = Field(default_factory=list)
    optimization_suggestions: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
