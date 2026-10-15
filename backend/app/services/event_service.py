"""Agent Event Service — in-memory event hub for real-time agent lifecycle tracking.

Dispatches and subscribes to live agent events per request_id.
Used by the SSE endpoint and planning service.
"""
from __future__ import annotations

import asyncio
import datetime
import json
from typing import Any, AsyncGenerator
from collections import defaultdict


class AgentEvent:
    """A single agent lifecycle event."""

    def __init__(
        self,
        request_id: str,
        agent_name: str,
        event_type: str,
        message: str = "",
        metadata: dict[str, Any] | None = None,
    ):
        self.request_id = request_id
        self.agent_name = agent_name
        self.event_type = event_type  # agent_started, agent_completed, agent_error
        self.message = message
        self.metadata = metadata or {}
        self.timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

    def to_sse_dict(self) -> dict[str, str]:
        event_name_map = {
            "running": "agent_started",
            "completed": "agent_completed",
            "error": "agent_failed",
            "complete": "planning_complete",
        }
        sse_event_name = event_name_map.get(self.event_type, "agent_progress")
        payload = {
            "type": sse_event_name,
            "request_id": self.request_id,
            "agent": self.agent_name,
            "status": self.event_type,
            "message": self.message,
            "timestamp": self.timestamp,
            **self.metadata,
        }
        return {
            "event": sse_event_name,
            "data": json.dumps(payload),
        }


class EventService:
    """In-memory event hub for agent lifecycle events."""

    def __init__(self):
        self._events: dict[str, list[AgentEvent]] = defaultdict(list)
        self._subscribers: dict[str, list[asyncio.Queue]] = defaultdict(list)
        self._completed: set[str] = set()

    def emit(self, event: AgentEvent) -> None:
        """Emit an event — stores it and pushes to all subscribers."""
        self._events[event.request_id].append(event)
        for queue in self._subscribers.get(event.request_id, []):
            queue.put_nowait(event)

    def emit_started(self, request_id: str, agent_name: str, message: str = "") -> None:
        msg = message or f"{agent_name} is processing..."
        self.emit(AgentEvent(request_id, agent_name, "running", msg))

    def emit_completed(self, request_id: str, agent_name: str, message: str = "", metadata: dict | None = None) -> None:
        msg = message or f"{agent_name} completed."
        self.emit(AgentEvent(request_id, agent_name, "completed", msg, metadata))

    def emit_error(self, request_id: str, agent_name: str, error: str) -> None:
        self.emit(AgentEvent(request_id, agent_name, "error", f"{agent_name} failed: {error}"))

    def mark_complete(self, request_id: str) -> None:
        """Mark the entire workflow as complete."""
        self._completed.add(request_id)
        complete_event = AgentEvent(request_id, "workflow", "complete", "Travel plan ready.")
        self.emit(complete_event)

    def get_events(self, request_id: str) -> list[AgentEvent]:
        """Get all events for a request."""
        return self._events.get(request_id, [])

    async def subscribe(self, request_id: str) -> AsyncGenerator[AgentEvent, None]:
        """Subscribe to live events for a request. Yields events as they arrive."""
        queue: asyncio.Queue[AgentEvent] = asyncio.Queue()
        self._subscribers[request_id].append(queue)

        # First, replay existing events
        for event in self._events.get(request_id, []):
            yield event

        # If already complete, stop
        if request_id in self._completed:
            return

        # Then stream new events
        try:
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=120.0)
                    yield event
                    if event.event_type == "complete":
                        return
                except asyncio.TimeoutError:
                    return
        finally:
            self._subscribers[request_id].remove(queue)

    def cleanup(self, request_id: str) -> None:
        """Clean up events for a completed request."""
        self._events.pop(request_id, None)
        self._subscribers.pop(request_id, None)
        self._completed.discard(request_id)


# Global singleton
_event_service: EventService | None = None


def get_event_service() -> EventService:
    global _event_service
    if _event_service is None:
        _event_service = EventService()
    return _event_service
