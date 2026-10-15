from __future__ import annotations
import datetime
from enum import Enum
from pydantic import BaseModel

class AgentEventType(str, Enum):
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    TOOL_CALLED = "tool_called"
    PROGRESS = "progress"

class AgentEvent(BaseModel):
    id: str | None = None
    run_id: str
    agent_name: str
    event_type: AgentEventType
    message: str | None = None
    metadata: dict | None = None
    duration_ms: int | None = None
    timestamp: datetime.datetime

class AgentProgressUpdate(BaseModel):
    """SSE event payload for real-time frontend updates."""
    type: str
    agent: str
    message: str
    progress_pct: float | None = None
    details: dict | None = None
