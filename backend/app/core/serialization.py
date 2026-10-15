"""JSON serialization utilities for database persistence and API boundaries."""
from __future__ import annotations

import datetime
import enum
import uuid
from typing import Any


def to_json_safe(obj: Any) -> Any:
    """Recursively converts an object into a JSON-serializable structure.

    - Converts datetime, date, and time objects to ISO 8601 strings, preserving timezone offsets.
    - Converts Enum members to their primitive values.
    - Converts UUID objects to string representations.
    - Converts Pydantic models (v1 and v2) to dictionaries.
    - Recursively traverses nested dicts, lists, tuples, and sets.
    - Preserves None, strings, numbers (int, float), and booleans as-is.
    """
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj

    if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
        return obj.isoformat()

    if isinstance(obj, enum.Enum):
        return to_json_safe(obj.value)

    if isinstance(obj, uuid.UUID):
        return str(obj)

    # Pydantic v2 model_dump or v1 dict
    if hasattr(obj, "model_dump") and callable(obj.model_dump):
        return to_json_safe(obj.model_dump())
    if hasattr(obj, "dict") and callable(obj.dict) and not isinstance(obj, type):
        return to_json_safe(obj.dict())

    if isinstance(obj, dict):
        return {str(k): to_json_safe(v) for k, v in obj.items()}

    if isinstance(obj, (list, tuple)):
        return [to_json_safe(item) for item in obj]

    if isinstance(obj, (set, frozenset)):
        return [to_json_safe(item) for item in sorted(obj, key=str)]

    # Objects with custom isoformat
    if hasattr(obj, "isoformat") and callable(obj.isoformat):
        return obj.isoformat()

    if hasattr(obj, "__dict__"):
        return to_json_safe(obj.__dict__)

    return str(obj)
