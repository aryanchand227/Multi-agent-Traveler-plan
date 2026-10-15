"""Tests for JSON-safe serialization and database persistence of final_plan with datetimes."""
from __future__ import annotations

import datetime
import enum
import json
import uuid
import pytest
from sqlalchemy import select

from app.core.serialization import to_json_safe
from app.db.repositories.travel import TravelRepository
from app.models.user import User
from app.models.travel_run import TravelRequest, TravelRun
from app.schemas.travel import TravelRunResponse, TravelRunStatus


class SampleEnum(str, enum.Enum):
    FLIGHT = "flight"
    TRAIN = "train"


def test_to_json_safe_primitives():
    """Verify that primitive types and None are preserved as-is."""
    assert to_json_safe(None) is None
    assert to_json_safe("hello") == "hello"
    assert to_json_safe(42) == 42
    assert to_json_safe(3.14) == 3.14
    assert to_json_safe(True) is True
    assert to_json_safe(False) is False


def test_to_json_safe_datetimes_preserves_offset():
    """Verify that datetimes and dates convert to ISO 8601 strings and preserve timezone offset."""
    # UTC aware datetime
    dt_utc = datetime.datetime(2026, 10, 16, 14, 30, 45, tzinfo=datetime.timezone.utc)
    res_utc = to_json_safe(dt_utc)
    assert res_utc == "2026-10-16T14:30:45+00:00"

    # Specific timezone offset (+05:30)
    ist = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
    dt_ist = datetime.datetime(2026, 10, 16, 20, 0, 0, tzinfo=ist)
    res_ist = to_json_safe(dt_ist)
    assert res_ist == "2026-10-16T20:00:00+05:30"

    # Date and Time objects
    d = datetime.date(2026, 10, 16)
    assert to_json_safe(d) == "2026-10-16"

    t = datetime.time(12, 30, 0)
    assert to_json_safe(t) == "12:30:00"


def test_to_json_safe_nested_structures():
    """Verify recursive serialization of dicts, lists, sets, enums, UUIDs, and datetimes."""
    uid = uuid.uuid4()
    now_utc = datetime.datetime.now(datetime.timezone.utc)

    nested = {
        "id": uid,
        "mode": SampleEnum.FLIGHT,
        "timestamps": [now_utc, datetime.date(2026, 11, 1)],
        "metadata": {
            "created_at": now_utc,
            "tags": {"travel", "vacation"},
            "count": 5,
        },
    }

    serialized = to_json_safe(nested)

    # Must be valid JSON without raising TypeError
    json_str = json.dumps(serialized)
    decoded = json.loads(json_str)

    assert decoded["id"] == str(uid)
    assert decoded["mode"] == "flight"
    assert decoded["timestamps"][0] == now_utc.isoformat()
    assert decoded["timestamps"][1] == "2026-11-01"
    assert decoded["metadata"]["created_at"] == now_utc.isoformat()
    assert set(decoded["metadata"]["tags"]) == {"travel", "vacation"}
    assert decoded["metadata"]["count"] == 5


@pytest.mark.asyncio
async def test_travel_repo_update_run_status_with_nested_datetimes(db_session):
    """Regression test: updating travel_runs with a final_plan containing timezone-aware datetimes
    persists successfully without 'TypeError: Object of type datetime is not JSON serializable',
    and the plan can be read back as valid JSON.
    """
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    departure_dt = datetime.datetime(2026, 11, 15, 8, 30, tzinfo=datetime.timezone.utc)

    # 1. Setup user, request, and initial run
    user = User(id="user-json-1", email="json_test@example.com")
    db_session.add(user)
    await db_session.flush()

    req = TravelRequest(id="req-json-1", user_id=user.id, raw_request="Trip to Goa")
    db_session.add(req)
    await db_session.flush()

    run = TravelRun(id="run-json-1", request_id=req.id, status="in_progress", started_at=now_utc)
    db_session.add(run)
    await db_session.commit()

    # 2. Build final_plan with nested timezone-aware datetime objects
    final_plan_with_datetimes = {
        "trip_summary": {
            "request_id": "req-json-1",
            "origin": "Mumbai",
            "destination": "Goa",
            "departure_date": "2026-11-15",
            "return_date": "2026-11-20",
            "travelers": 2,
            "duration_days": 5,
            "budget": 30000.0,
            "currency": "INR",
            "travel_style": "relaxed",
            "interests": ["beaches", "seafood"],
        },
        "transportation": {
            "selected": {
                "id": "opt-101",
                "mode": "flight",
                "provider": "IndiGo",
                "provider_type": "airline",
                "origin": "BOM",
                "destination": "GOI",
                "departure_time": "08:30",
                "arrival_time": "09:45",
                "duration_minutes": 75,
                "price_per_person": 3500.0,
                "total_price": 7000.0,
                "stops": 0,
                "comfort_level": "standard",
                "availability": "available",
                "source": "mock",
                "source_type": "mock",
                # Nested timezone-aware Python datetime object
                "retrieved_at": now_utc,
            },
            "alternatives": [],
        },
        "accommodation": {
            "id": "acc-101",
            "name": "Goa Beach Resort",
            "location": "Calangute",
            "accommodation_type": "resort",
            "rating": 4.5,
            "nightly_price": 4000.0,
            "total_price": 16000.0,
            "source": "mock",
            "source_type": "mock",
            "availability": "available",
            # Nested timezone-aware Python datetime object
            "retrieved_at": now_utc,
        },
        "accommodation_alternatives": [],
        "activities": [],
        "weather": None,
        "budget": {
            "total": 23000.0,
            "breakdown": {"transport": 7000.0, "accommodation": 16000.0},
            "status": "within_budget",
            "remaining": 7000.0,
            "cost_saving_suggestions": [],
        },
        "itinerary": None,
        "decision_factors": ["Best match for relaxed travel style"],
        "warnings": [],
        "data_sources": [
            {
                "provider": "MockTransport",
                "source_type": "mock",
                # Python datetime object
                "retrieved_at": departure_dt,
            }
        ],
        "validation": {"is_valid": True, "errors": [], "warnings": [], "checks_passed": []},
        "human_readable_summary": "Your 5-day relaxed trip from Mumbai to Goa for 2 travelers is planned.",
        # Python datetime object
        "generated_at": now_utc,
    }

    # 3. Call repository update_run_status with the un-serialized plan containing datetimes
    travel_repo = TravelRepository(db_session)
    await travel_repo.update_run_status(
        run_id="run-json-1",
        status="completed",
        final_plan=final_plan_with_datetimes,
    )

    # 4. Fetch the run from the database and verify final_plan was stored and is valid JSON
    result = await db_session.execute(select(TravelRun).where(TravelRun.id == "run-json-1"))
    stored_run = result.scalar_one()

    assert stored_run.status == "completed"
    assert stored_run.completed_at is not None
    assert stored_run.final_plan is not None

    stored_plan = stored_run.final_plan
    # Verify that datetime fields were safely converted to ISO 8601 strings
    assert stored_plan["transportation"]["selected"]["retrieved_at"] == now_utc.isoformat()
    assert stored_plan["accommodation"]["retrieved_at"] == now_utc.isoformat()
    assert stored_plan["data_sources"][0]["retrieved_at"] == departure_dt.isoformat()
    assert stored_plan["generated_at"] == now_utc.isoformat()

    # 5. Verify the stored plan validates cleanly in the API response model and dumps to JSON
    response = TravelRunResponse(
        request_id="req-json-1",
        run_id=stored_run.id,
        status=TravelRunStatus(stored_run.status),
        started_at=stored_run.started_at,
        completed_at=stored_run.completed_at,
        final_plan=stored_plan,
    )
    json_output = response.model_dump_json()
    assert "Mumbai" in json_output
    assert "2026-11-15T08:30:00" in json_output
    assert response.final_plan.transportation.selected.retrieved_at == now_utc
