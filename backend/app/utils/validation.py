"""Common validation utilities."""
from __future__ import annotations


def validate_travelers(count: int | None) -> bool:
    """Validate traveler count is reasonable."""
    if count is None:
        return False
    return 1 <= count <= 20


def validate_budget(budget: float | None) -> bool:
    """Validate budget is positive."""
    if budget is None:
        return True  # Budget is optional
    return budget > 0


def validate_transport_mode(mode: str) -> bool:
    """Validate transport mode."""
    valid_modes = {"bus", "train", "flight"}
    return mode.lower() in valid_modes


def validate_travel_style(style: str) -> bool:
    """Validate travel style."""
    valid_styles = {"budget", "standard", "premium", "luxury", "custom"}
    return style.lower() in valid_styles
