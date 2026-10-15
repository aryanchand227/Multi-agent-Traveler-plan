"""LLM Usage Repository for cost accounting and quota tracking."""
from __future__ import annotations

import datetime
from typing import Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.usage import LLMUsageRecord
from app.models.travel_run import TravelRequest


class UsageRepository:
    """Repository for LLM usage records and cost analytics."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def record_usage(
        self,
        agent_name: str,
        model: str,
        user_id: str | None = None,
        request_id: str | None = None,
        run_id: str | None = None,
        provider: str = "groq",
        provider_requests: int = 1,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        estimated_cost_usd: float = 0.0,
        duration_ms: float = 0.0,
        status: str = "success",
    ) -> LLMUsageRecord:
        """Persist a single agent/model LLM usage metric."""
        total_tokens = prompt_tokens + completion_tokens
        record = LLMUsageRecord(
            user_id=user_id,
            request_id=request_id,
            run_id=run_id,
            agent_name=agent_name,
            provider=provider,
            model=model,
            provider_requests=provider_requests,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            estimated_cost_usd=estimated_cost_usd,
            duration_ms=duration_ms,
            status=status,
        )
        self.session.add(record)
        await self.session.commit()
        await self.session.refresh(record)
        return record

    async def get_daily_user_plan_count(self, user_id: str) -> int:
        """Count travel plan requests created by user today."""
        today_start = datetime.datetime.now(datetime.timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        stmt = (
            select(func.count(TravelRequest.id))
            .where(TravelRequest.user_id == user_id)
            .where(TravelRequest.created_at >= today_start)
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def get_daily_app_cost(self) -> float:
        """Calculate total USD cost consumed by all users today."""
        today_start = datetime.datetime.now(datetime.timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        stmt = (
            select(func.sum(LLMUsageRecord.estimated_cost_usd))
            .where(LLMUsageRecord.created_at >= today_start)
        )
        result = await self.session.execute(stmt)
        return float(result.scalar() or 0.0)

    async def get_monthly_app_cost(self) -> float:
        """Calculate total USD cost consumed by all users this month."""
        month_start = datetime.datetime.now(datetime.timezone.utc).replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        stmt = (
            select(func.sum(LLMUsageRecord.estimated_cost_usd))
            .where(LLMUsageRecord.created_at >= month_start)
        )
        result = await self.session.execute(stmt)
        return float(result.scalar() or 0.0)
