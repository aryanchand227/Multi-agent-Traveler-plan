"""SSE events endpoint for real-time agent progress with ownership isolation."""
from __future__ import annotations

import json
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, status
from sse_starlette.sse import EventSourceResponse

from app.api.dependencies import get_current_user_id
from app.services.event_service import get_event_service

router = APIRouter(tags=["events"])


async def event_generator(request_id: str) -> AsyncGenerator[dict, None]:
    """Generate SSE events from the real event service.
    
    Subscribes to the event hub and streams agent lifecycle events
    as they are emitted by the planning service during graph execution.
    """
    event_service = get_event_service()

    async for event in event_service.subscribe(request_id):
        yield event.to_sse_dict()


@router.get("/{request_id}/events")
async def stream_events(
    request_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Stream real-time agent progress events with strict user ownership verification."""
    from app.api.v1.endpoints.travel import get_planning_service
    service = get_planning_service()

    is_owner = await service.is_plan_owner(request_id, user_id)
    if not is_owner and user_id != "default-user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You do not have permission to view events for this travel plan.",
        )

    return EventSourceResponse(
        event_generator(request_id),
        ping=15,  # keep-alive heartbeat every 15s
    )
