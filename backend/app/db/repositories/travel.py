"""Travel request/run database operations."""
from __future__ import annotations

import datetime
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.travel_run import TravelRequest, TravelRun
from app.core.serialization import to_json_safe


class TravelRepository:
    """Repository for travel requests and runs."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_request(self, **kwargs: Any) -> TravelRequest:
        request = TravelRequest(**kwargs)
        self.session.add(request)
        await self.session.commit()
        await self.session.refresh(request)
        return request

    async def create_run(self, request_id: str) -> TravelRun:
        run = TravelRun(
            request_id=request_id,
            status="pending",
            started_at=datetime.datetime.now(datetime.timezone.utc),
        )
        self.session.add(run)
        await self.session.commit()
        await self.session.refresh(run)
        return run

    async def get_request(self, request_id: str) -> TravelRequest | None:
        result = await self.session.execute(
            select(TravelRequest).where(TravelRequest.id == request_id)
        )
        return result.scalar_one_or_none()

    async def get_request_for_user(self, request_id: str, user_id: str) -> TravelRequest | None:
        """Enforces ownership boundary — returns request only if it belongs to user_id."""
        result = await self.session.execute(
            select(TravelRequest)
            .where(TravelRequest.id == request_id)
            .where(TravelRequest.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def list_user_requests(self, user_id: str, limit: int = 20) -> list[TravelRequest]:
        """Fetch historical travel requests for a specific user."""
        result = await self.session.execute(
            select(TravelRequest)
            .where(TravelRequest.user_id == user_id)
            .order_by(TravelRequest.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_run(self, run_id: str) -> TravelRun | None:
        result = await self.session.execute(
            select(TravelRun).where(TravelRun.id == run_id)
        )
        return result.scalar_one_or_none()

    async def get_run_by_request(self, request_id: str) -> TravelRun | None:
        result = await self.session.execute(
            select(TravelRun)
            .where(TravelRun.request_id == request_id)
            .order_by(TravelRun.created_at.desc())
        )
        return result.scalar_one_or_none()

    async def update_run_status(
        self,
        run_id: str,
        status: str,
        error: str | None = None,
        final_plan: dict | None = None,
        agent_states: dict | None = None,
    ) -> None:
        values: dict[str, Any] = {"status": status}
        if error is not None:
            values["error"] = error
        if final_plan is not None:
            values["final_plan"] = to_json_safe(final_plan)
        if agent_states is not None:
            values["agent_states"] = to_json_safe(agent_states)
        if status in ("completed", "failed", "cancelled"):
            values["completed_at"] = datetime.datetime.now(datetime.timezone.utc)
        await self.session.execute(
            update(TravelRun).where(TravelRun.id == run_id).values(**values)
        )
        await self.session.commit()
