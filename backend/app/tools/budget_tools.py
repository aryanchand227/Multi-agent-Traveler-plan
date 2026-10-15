"""Deterministic budget calculation and optimization tools."""
from __future__ import annotations

from typing import Dict, Any


def calculate_per_person_cost(total_cost: float, travelers: int) -> float:
    """Calculate per-person cost safely."""
    return round(total_cost / max(1, travelers), 2)


def calculate_budget_utilization(total_cost: float, budget: float | None) -> dict[str, Any]:
    """Calculate budget ratio, remaining balance, and status."""
    if not budget or budget <= 0:
        return {
            "budget": budget,
            "total_cost": total_cost,
            "remaining": None,
            "utilization_pct": None,
            "status": "within_budget",
        }

    remaining = round(budget - total_cost, 2)
    ratio = total_cost / budget
    utilization_pct = round(ratio * 100, 1)

    if ratio <= 0.90:
        status = "within_budget"
    elif ratio <= 1.00:
        status = "near_budget"
    else:
        status = "over_budget"

    return {
        "budget": budget,
        "total_cost": total_cost,
        "remaining": remaining,
        "utilization_pct": utilization_pct,
        "status": status,
    }
