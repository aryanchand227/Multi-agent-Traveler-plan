"""
Custom exception hierarchy for the application.

Provides structured errors that agents, services, and API endpoints can use
for consistent error handling without crashing the entire workflow.
"""

from __future__ import annotations


class TravelPlannerError(Exception):
    """Base exception for the travel planning platform."""

    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


# --- Agent Errors ---

class AgentError(TravelPlannerError):
    """Error raised by an agent during execution."""

    def __init__(
        self,
        message: str,
        agent_name: str,
        details: dict | None = None,
    ) -> None:
        super().__init__(message, details)
        self.agent_name = agent_name


class AgentTimeoutError(AgentError):
    """Agent execution exceeded the configured timeout."""


class AgentRetryExhaustedError(AgentError):
    """Agent exhausted all retry attempts."""


# --- Provider Errors ---

class ProviderError(TravelPlannerError):
    """Error from an external data provider."""

    def __init__(
        self,
        message: str,
        provider_name: str,
        details: dict | None = None,
    ) -> None:
        super().__init__(message, details)
        self.provider_name = provider_name


class ProviderUnavailableError(ProviderError):
    """Provider is temporarily unavailable."""


class ProviderTimeoutError(ProviderError):
    """Provider request timed out."""


# --- LLM Errors ---

class LLMError(TravelPlannerError):
    """Error from the LLM provider."""


class LLMOutputError(LLMError):
    """LLM produced invalid or unparseable output."""


class LLMRateLimitError(LLMError):
    """LLM provider rate limit exceeded."""


# --- Validation Errors ---

class ValidationError(TravelPlannerError):
    """Validation failure in data or plan."""

    def __init__(
        self,
        message: str,
        field: str | None = None,
        details: dict | None = None,
    ) -> None:
        super().__init__(message, details)
        self.field = field


class BudgetOverflowError(ValidationError):
    """Requested plan exceeds budget constraints."""

    def __init__(
        self,
        message: str,
        estimated_cost: float,
        budget: float,
        suggestions: list[str] | None = None,
        details: dict | None = None,
    ) -> None:
        super().__init__(message, details=details)
        self.estimated_cost = estimated_cost
        self.budget = budget
        self.suggestions = suggestions or []


# --- Database Errors ---

class DatabaseError(TravelPlannerError):
    """Database operation failure."""


# --- Travel Planning Errors ---

class InsufficientInformationError(TravelPlannerError):
    """Not enough information to proceed with planning."""

    def __init__(
        self,
        message: str,
        missing_fields: list[str],
        details: dict | None = None,
    ) -> None:
        super().__init__(message, details)
        self.missing_fields = missing_fields


class PlanningError(TravelPlannerError):
    """Error during the travel planning workflow."""


class ReplanningError(TravelPlannerError):
    """Error during plan modification/replanning."""
