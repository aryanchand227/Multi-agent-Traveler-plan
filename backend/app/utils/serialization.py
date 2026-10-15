"""Serialization utilities."""
from __future__ import annotations

import datetime
import json
from typing import Any


class DateTimeEncoder(json.JSONEncoder):
    """JSON encoder that handles datetime objects."""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        return super().default(obj)


def serialize_to_json(data: Any) -> str:
    """Serialize data to JSON string with datetime support."""
    return json.dumps(data, cls=DateTimeEncoder, default=str)


def safe_json_loads(text: str, default: Any = None) -> Any:
    """Safely parse JSON, returning default on failure."""
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return default
