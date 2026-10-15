"""
Core application configuration.

All settings are loaded from environment variables with sensible defaults.
Configuration is centralized here — no magic strings scattered across the codebase.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Application ---
    app_env: str = "development"
    app_name: str = "AI Travel Planner"
    app_version: str = "1.0.0"
    debug: bool = True

    # --- Database ---
    database_url: str = "sqlite+aiosqlite:///./travel_planner.db"

    # --- Redis (optional) ---
    redis_url: str | None = None

    # --- LLM Provider ---
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o-mini"
    llm_api_key: str = ""
    llm_base_url: str | None = None
    llm_temperature: float = 0.3
    llm_max_retries: int = 2
    llm_request_timeout: int = 30

    # --- Agent Configuration ---
    max_agent_iterations: int = 5
    max_agent_retries: int = 2
    agent_timeout_seconds: int = 60

    # --- Output Token Limits ---
    output_tokens_brief: int = 500
    output_tokens_standard: int = 1200
    output_tokens_detailed: int = 2500

    # --- External API Keys (optional — mock when absent) ---
    weather_api_key: str | None = None
    bus_api_key: str | None = None
    train_api_key: str | None = None
    flight_api_key: str | None = None
    hotel_api_key: str | None = None

    # --- CORS ---
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # --- Security & Authentication ---
    jwt_secret_key: str = "dev-insecure-secret-key-change-in-production-min32chars"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 1440
    max_request_body_bytes: int = 65536

    # --- Proxy & Networking ---
    trusted_proxies: list[str] = ["127.0.0.1", "::1"]
    trust_all_proxies: bool = False

    # --- Rate Limiting ---
    rate_limit_enabled: bool = True
    rate_limit_auth_per_minute: int = 5
    rate_limit_anonymous_per_minute: int = 10
    rate_limit_user_per_minute: int = 20
    travel_plans_per_user_per_day: int = 10
    travel_plans_per_ip_per_day: int = 20
    max_concurrent_plans_total: int = 3
    max_llm_calls_per_plan: int = 20

    # --- Cost & Budget Guardrails (USD) ---
    daily_llm_budget_usd: float = 2.00
    monthly_llm_budget_usd: float = 20.00

    # --- Server ---
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> list[str]:
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @field_validator("trusted_proxies", mode="before")
    @classmethod
    def parse_trusted_proxies(cls, v: Any) -> list[str]:
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [p.strip() for p in v.split(",") if p.strip()]
        return v

    # --- Derived Properties ---

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def is_sqlite(self) -> bool:
        return "sqlite" in self.database_url

    @property
    def output_token_limits(self) -> dict[str, int]:
        return {
            "brief": self.output_tokens_brief,
            "standard": self.output_tokens_standard,
            "detailed": self.output_tokens_detailed,
        }

    @property
    def use_mock_providers(self) -> bool:
        """Use mock providers when API keys are not configured."""
        return not any([
            self.bus_api_key,
            self.train_api_key,
            self.flight_api_key,
            self.hotel_api_key,
        ])

    def validate_production_settings(self) -> list[str]:
        """Validate settings for production safety. Returns list of warning/error messages."""
        issues: list[str] = []
        if self.is_production:
            if self.debug:
                issues.append("DEBUG is True in production environment.")
            if "dev-insecure-secret-key" in self.jwt_secret_key or len(self.jwt_secret_key) < 32:
                issues.append("JWT_SECRET_KEY is using an insecure or default key. Provide a secure 32+ character key.")
            if self.is_sqlite:
                issues.append("DATABASE_URL is using SQLite in production. PostgreSQL is required for multi-user durability.")
            if not self.llm_api_key and not self.use_mock_providers:
                issues.append("LLM_API_KEY is not configured.")
        return issues


# --- Transport Ranking Weights (Section 38) ---

TRANSPORT_WEIGHTS: dict[str, dict[str, float]] = {
    "budget": {
        "cost": 0.50,
        "duration": 0.20,
        "comfort": 0.10,
        "preference": 0.20,
    },
    "standard": {
        "cost": 0.30,
        "duration": 0.25,
        "comfort": 0.20,
        "preference": 0.25,
    },
    "premium": {
        "cost": 0.15,
        "duration": 0.25,
        "comfort": 0.30,
        "preference": 0.30,
    },
    "luxury": {
        "cost": 0.10,
        "duration": 0.20,
        "comfort": 0.40,
        "preference": 0.30,
    },
}

# --- Budget Thresholds ---

BUDGET_THRESHOLDS = {
    "within_budget": 0.90,   # <= 90% of budget
    "near_budget": 1.00,     # 90% — 100%
    "over_budget": 1.00,     # > 100%
}

# --- Travel Styles ---

TRAVEL_STYLES = ["budget", "standard", "premium", "luxury", "custom"]

# --- Budget Modes ---

BUDGET_MODES = ["auto", "budget", "standard", "premium", "luxury", "custom"]


def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
