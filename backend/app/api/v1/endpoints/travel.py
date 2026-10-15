"""Travel planning API endpoints with authentication and ownership enforcement."""
from __future__ import annotations

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user_id, get_database
from app.db.repositories.travel import TravelRepository
from app.core.rate_limit import rate_limit_planning
from app.schemas.travel import (
    TravelPlanRequest,
    TravelRunResponse,
    ClarificationResponse,
    ReplanRequest,
)
from app.services.planning import TravelPlanningService

router = APIRouter(tags=["travel"])

# Singleton service instance
_planning_service: TravelPlanningService | None = None


def get_planning_service() -> TravelPlanningService:
    global _planning_service
    if _planning_service is None:
        _planning_service = TravelPlanningService()
    return _planning_service


@router.post("/plan", response_model=TravelRunResponse)
async def create_travel_plan(
    plan_request: TravelPlanRequest,
    http_request: Request,
    user_id: str = Depends(get_current_user_id),
) -> TravelRunResponse:
    """Start a new travel planning workflow with rate limiting and user isolation."""
    await rate_limit_planning(http_request, user_id)
    service = get_planning_service()
    return await service.create_plan(plan_request, user_id)


@router.post("/clarify", response_model=TravelRunResponse)
async def submit_clarification(
    response: ClarificationResponse,
    user_id: str = Depends(get_current_user_id),
) -> TravelRunResponse:
    """Submit answers to clarification questions."""
    service = get_planning_service()
    result = await service.handle_clarification(
        response.request_id,
        response.responses,
        user_id,
    )
    if result.status.value == "failed" and result.error == "Request not found.":
        raise HTTPException(status_code=404, detail="Request not found.")
    return result


@router.get("/history", response_model=list[dict[str, Any]])
async def list_travel_history(
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_database),
) -> list[dict[str, Any]]:
    """List historical travel plans created by the authenticated user."""
    repo = TravelRepository(session)
    records = await repo.list_user_requests(user_id)
    history = []
    for req in records:
        run = await repo.get_run_by_request(req.id)
        history.append({
            "request_id": req.id,
            "origin": req.origin,
            "destination": req.destination,
            "departure_date": req.departure_date,
            "travelers": req.travelers,
            "budget": req.budget,
            "currency": req.currency,
            "status": run.status if run else "pending",
            "created_at": req.created_at.isoformat() if req.created_at else None,
        })
    return history


@router.get("/{request_id}", response_model=TravelRunResponse)
async def get_travel_plan(
    request_id: str,
    user_id: str = Depends(get_current_user_id),
) -> TravelRunResponse:
    """Get the status/result of a travel planning run, enforcing user ownership."""
    service = get_planning_service()
    result = await service.get_plan(request_id, user_id=user_id)
    if not result:
        raise HTTPException(status_code=404, detail="Travel plan not found.")
    return result


@router.post("/{request_id}/replan", response_model=TravelRunResponse)
async def replan_travel(
    request_id: str,
    replan: ReplanRequest,
    user_id: str = Depends(get_current_user_id),
) -> TravelRunResponse:
    """Modify an existing travel plan with intelligent replanning."""
    service = get_planning_service()
    existing = await service.get_plan(request_id, user_id=user_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Travel plan not found.")

    result = await service.replan(
        request_id,
        replan.message,
        replan.changes,
        user_id,
    )
    return result
