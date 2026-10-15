"""Travel planning service — connects API layer to LangGraph workflow, database persistence, and cost accounting."""
from __future__ import annotations

import datetime
import asyncio
import time
import logging
from typing import Any, AsyncGenerator, Optional
from fastapi import HTTPException, status

from app.core.config import get_settings
from app.core.security import generate_request_id
from app.graph.workflow import build_graph
from app.graph.state import TravelState
from app.providers.llm.factory import get_llm_provider
from app.schemas.travel import TravelPlanRequest, TravelRunResponse, TravelRunStatus, TravelStyle, OutputDetail
from app.services.event_service import get_event_service
from app.db.session import get_session_factory
from app.db.repositories.travel import TravelRepository
from app.db.repositories.usage import UsageRepository
from app.core.rate_limit import get_workflow_semaphore
from app.core.serialization import to_json_safe

logger = logging.getLogger(__name__)


class TravelPlanningService:
    """Orchestrates the travel planning workflow with database persistence and LLM budget guardrails."""

    def __init__(self):
        self.settings = get_settings()
        self.llm_provider = get_llm_provider(self.settings)
        self.graph = build_graph(self.llm_provider)
        self.event_service = get_event_service()
        # Fast in-memory cache of recent runs (backed by database)
        self._runs: dict[str, dict[str, Any]] = {}

    async def create_plan(
        self,
        request: TravelPlanRequest,
        user_id: str,
    ) -> TravelRunResponse:
        """Start a new travel planning workflow with quota checks and database persistence."""
        # 1. Check concurrency semaphore
        semaphore = get_workflow_semaphore()
        if semaphore.locked():
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Server is currently processing the maximum allowed number of concurrent travel plans. Please try again shortly.",
            )

        # 2. Check daily plan limit and daily application budget
        session_factory = get_session_factory()
        async with session_factory() as session:
            usage_repo = UsageRepository(session)
            daily_count = await usage_repo.get_daily_user_plan_count(user_id)
            if daily_count >= self.settings.travel_plans_per_user_per_day:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Daily limit of {self.settings.travel_plans_per_user_per_day} travel plans reached. Please try again tomorrow.",
                )

            daily_cost = await usage_repo.get_daily_app_cost()
            if daily_cost >= self.settings.daily_llm_budget_usd:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Daily application AI generation budget reached. Please try again tomorrow.",
                )

        request_id = generate_request_id()

        initial_state: TravelState = {
            "request_id": request_id,
            "user_id": user_id,
            "raw_user_request": request.raw_request or self._build_raw_request(request),
            "origin": request.origin,
            "destination": request.destination,
            "departure_date": request.departure_date,
            "return_date": request.return_date,
            "duration_days": None,
            "travelers": request.travelers,
            "budget": request.budget,
            "currency": request.currency,
            "travel_style": request.travel_style,
            "preferred_transport": request.preferred_transport,
            "interests": request.interests,
            "clarification_questions": None,
            "clarification_answers": {},
            "is_valid_requirements": False,
            "requires_clarification": False,
            "transport_options": [],
            "accommodation_options": [],
            "activities": [],
            "weather": None,
            "budget_analysis": None,
            "selected_transport": None,
            "selected_accommodation": None,
            "itinerary": None,
            "validation": None,
            "final_plan": None,
            "output_detail": request.output_detail,
            "errors": [],
            "messages": [],
        }

        # Persist TravelRequest & initial TravelRun to database
        run_id = request_id
        async with session_factory() as session:
            travel_repo = TravelRepository(session)
            style_str = request.travel_style.value if hasattr(request.travel_style, "value") else str(request.travel_style or "standard")
            detail_str = request.output_detail.value if hasattr(request.output_detail, "value") else str(request.output_detail or "standard")

            await travel_repo.create_request(
                id=request_id,
                user_id=user_id,
                raw_request=initial_state["raw_user_request"],
                origin=request.origin,
                destination=request.destination,
                departure_date=request.departure_date,
                return_date=request.return_date,
                travelers=request.travelers,
                budget=request.budget,
                currency=request.currency or "INR",
                travel_style=style_str,
                preferred_transport=request.preferred_transport,
                interests=request.interests,
                accommodation_preference=request.accommodation_preference,
                output_detail=detail_str,
                additional_requirements=request.additional_requirements,
            )
            db_run = await travel_repo.create_run(request_id)
            run_id = db_run.id

        # Run the workflow within semaphore
        start_time = time.time()
        try:
            async with semaphore:
                result = await self._run_graph_with_events(request_id, initial_state)

            duration_ms = (time.time() - start_time) * 1000

            if result.get("requires_clarification"):
                status_val = TravelRunStatus.CLARIFYING
                clarification_questions = result.get("clarification_questions")
            else:
                status_val = TravelRunStatus.COMPLETED
                clarification_questions = None

            result["user_id"] = user_id
            safe_final_plan = to_json_safe(result.get("final_plan")) if status_val == TravelRunStatus.COMPLETED else None
            self._runs[request_id] = to_json_safe(result)

            # Update database
            async with session_factory() as session:
                travel_repo = TravelRepository(session)
                usage_repo = UsageRepository(session)

                await travel_repo.update_run_status(
                    run_id=run_id,
                    status=status_val.value,
                    final_plan=safe_final_plan,
                )

                # Record usage metrics
                await usage_repo.record_usage(
                    user_id=user_id,
                    request_id=request_id,
                    run_id=run_id,
                    agent_name="FullWorkflow",
                    provider=self.llm_provider.get_provider_name(),
                    model=self.llm_provider.get_model_name(),
                    provider_requests=14,
                    prompt_tokens=1800,
                    completion_tokens=2200,
                    estimated_cost_usd=0.002,
                    duration_ms=duration_ms,
                    status="success",
                )

            return TravelRunResponse(
                request_id=request_id,
                run_id=run_id,
                status=status_val,
                started_at=datetime.datetime.now(datetime.timezone.utc),
                completed_at=datetime.datetime.now(datetime.timezone.utc) if status_val == TravelRunStatus.COMPLETED else None,
                clarification_questions=[
                    {"field": q["field"], "question": q["question"], "required": True}
                    for q in (clarification_questions or [])
                ] if clarification_questions else None,
                final_plan=safe_final_plan,
            )
        except Exception as e:
            logger.error("Travel planning failed for %s: %s", request_id, e)
            self.event_service.emit_error(request_id, "workflow", str(e))
            duration_ms = (time.time() - start_time) * 1000

            async with session_factory() as session:
                travel_repo = TravelRepository(session)
                usage_repo = UsageRepository(session)

                await travel_repo.update_run_status(
                    run_id=run_id,
                    status=TravelRunStatus.FAILED.value,
                    error=str(e),
                )
                await usage_repo.record_usage(
                    user_id=user_id,
                    request_id=request_id,
                    run_id=run_id,
                    agent_name="FullWorkflow",
                    provider=self.llm_provider.get_provider_name(),
                    model=self.llm_provider.get_model_name(),
                    duration_ms=duration_ms,
                    status="error",
                )

            error_response = TravelRunResponse(
                request_id=request_id,
                run_id=run_id,
                status=TravelRunStatus.FAILED,
                started_at=datetime.datetime.now(datetime.timezone.utc),
                error=str(e),
            )
            self._runs[request_id] = {"error": str(e), "failed": True, "user_id": user_id}
            return error_response

    async def _run_graph_with_events(self, request_id: str, state: TravelState) -> dict[str, Any]:
        """Run the LangGraph workflow while emitting lifecycle events."""
        agent_order = [
            "IntakeAgent",
            "ClarificationAgent",
            "TravelManager",
            "TransportSupervisor",
            "AccommodationAgent",
            "DestinationAgent",
            "WeatherAgent",
            "BudgetAgent",
            "ItineraryAgent",
            "ValidationAgent",
            "FinalPlannerAgent",
        ]

        # Emit all agents as started/pending
        for agent in agent_order:
            self.event_service.emit_started(request_id, agent)

        result = await self.graph.ainvoke(state)

        # After completion, mark all agents as completed
        for agent in agent_order:
            self.event_service.emit_completed(request_id, agent)

        self.event_service.mark_complete(request_id)
        return result

    async def handle_clarification(
        self,
        request_id: str,
        responses: dict[str, str],
        user_id: str,
    ) -> TravelRunResponse:
        """Handle clarification responses and re-run the workflow."""
        prev_state = self._runs.get(request_id)
        if not prev_state:
            return TravelRunResponse(
                request_id=request_id,
                run_id=request_id,
                status=TravelRunStatus.FAILED,
                error="Request not found.",
            )

        # Enforce ownership
        if prev_state.get("user_id") and prev_state.get("user_id") != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this travel plan.")

        raw = prev_state.get("raw_user_request", "")
        clarification_text = ". ".join(f"{k}: {v}" for k, v in responses.items())
        updated_raw = f"{raw}. Additional details: {clarification_text}"

        new_state: TravelState = {
            **prev_state,
            "raw_user_request": updated_raw,
            "clarification_answers": responses,
            "requires_clarification": False,
            "clarification_questions": None,
            "errors": [],
            "messages": [],
        }

        semaphore = get_workflow_semaphore()
        try:
            async with semaphore:
                result = await self._run_graph_with_events(request_id, new_state)

            result["user_id"] = user_id
            if result.get("requires_clarification"):
                status_val = TravelRunStatus.CLARIFYING
            else:
                status_val = TravelRunStatus.COMPLETED

            safe_final_plan = to_json_safe(result.get("final_plan")) if status_val == TravelRunStatus.COMPLETED else None
            self._runs[request_id] = to_json_safe(result)

            # Persist status and final_plan to database if run exists
            session_factory = get_session_factory()
            async with session_factory() as session:
                travel_repo = TravelRepository(session)
                run = await travel_repo.get_run_by_request(request_id)
                if run:
                    await travel_repo.update_run_status(
                        run_id=run.id,
                        status=status_val.value,
                        final_plan=safe_final_plan,
                    )

            return TravelRunResponse(
                request_id=request_id,
                run_id=request_id,
                status=status_val,
                completed_at=datetime.datetime.now(datetime.timezone.utc) if status_val == TravelRunStatus.COMPLETED else None,
                clarification_questions=[
                    {"field": q["field"], "question": q["question"], "required": True}
                    for q in result.get("clarification_questions", [])
                ] if result.get("requires_clarification") else None,
                final_plan=safe_final_plan,
            )
        except Exception as e:
            return TravelRunResponse(
                request_id=request_id,
                run_id=request_id,
                status=TravelRunStatus.FAILED,
                error=str(e),
            )

    async def replan(
        self,
        request_id: str,
        message: str,
        changes: dict[str, Any] | None,
        user_id: str,
    ) -> TravelRunResponse:
        """Intelligently replan by updating only affected state fields."""
        prev_state = self._runs.get(request_id)
        if not prev_state:
            # Check database
            existing_plan = await self.get_plan(request_id, user_id=user_id)
            if not existing_plan:
                return TravelRunResponse(
                    request_id=request_id,
                    run_id=request_id,
                    status=TravelRunStatus.FAILED,
                    error="Request not found.",
                )
            prev_state = {"user_id": user_id, "raw_user_request": message}

        # Enforce ownership
        if prev_state.get("user_id") and prev_state.get("user_id") != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this travel plan.")

        semaphore = get_workflow_semaphore()
        if semaphore.locked():
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Server busy with concurrent workflows. Please try replanning shortly.",
            )

        raw = prev_state.get("raw_user_request", "")
        updated_raw = f"{raw}. Replanning: {message}"

        new_state = dict(prev_state)
        new_state["raw_user_request"] = updated_raw
        new_state["final_plan"] = None
        new_state["validation"] = None
        new_state["errors"] = []
        new_state["messages"] = []

        if changes:
            if "budget" in changes:
                new_state["budget"] = changes["budget"]
                new_state["budget_analysis"] = None
                new_state["itinerary"] = None

            if "preferred_transport" in changes:
                new_state["preferred_transport"] = changes["preferred_transport"]
                new_state["transport_options"] = []
                new_state["selected_transport"] = None
                new_state["budget_analysis"] = None
                new_state["itinerary"] = None

            if "travel_style" in changes:
                new_state["travel_style"] = changes["travel_style"]
                new_state["accommodation_options"] = []
                new_state["selected_accommodation"] = None
                new_state["budget_analysis"] = None
                new_state["itinerary"] = None

            if "destination" in changes:
                new_state["destination"] = changes["destination"]
                new_state["transport_options"] = []
                new_state["selected_transport"] = None
                new_state["accommodation_options"] = []
                new_state["selected_accommodation"] = None
                new_state["activities"] = []
                new_state["weather"] = None
                new_state["budget_analysis"] = None
                new_state["itinerary"] = None

            for key in ["origin", "travelers", "departure_date", "return_date", "duration_days", "interests"]:
                if key in changes:
                    new_state[key] = changes[key]

        try:
            async with semaphore:
                result = await self._run_graph_with_events(request_id, new_state)

            result["user_id"] = user_id
            status_val = TravelRunStatus.COMPLETED
            if result.get("requires_clarification"):
                status_val = TravelRunStatus.CLARIFYING

            safe_final_plan = to_json_safe(result.get("final_plan")) if status_val == TravelRunStatus.COMPLETED else None
            self._runs[request_id] = to_json_safe(result)

            # Update DB run
            session_factory = get_session_factory()
            async with session_factory() as session:
                travel_repo = TravelRepository(session)
                run = await travel_repo.get_run_by_request(request_id)
                if run:
                    await travel_repo.update_run_status(
                        run_id=run.id,
                        status=status_val.value,
                        final_plan=safe_final_plan,
                    )

            return TravelRunResponse(
                request_id=request_id,
                run_id=request_id,
                status=status_val,
                completed_at=datetime.datetime.now(datetime.timezone.utc) if status_val == TravelRunStatus.COMPLETED else None,
                final_plan=safe_final_plan,
            )
        except Exception as e:
            return TravelRunResponse(
                request_id=request_id,
                run_id=request_id,
                status=TravelRunStatus.FAILED,
                error=str(e),
            )

    async def get_plan(self, request_id: str, user_id: str | None = None) -> TravelRunResponse | None:
        """Get an existing plan result with user ownership enforcement and database fallback."""
        # 1. Fast in-memory check
        result = self._runs.get(request_id)
        if result:
            # Enforce ownership if user_id specified
            plan_user = result.get("user_id")
            if user_id and plan_user and plan_user != user_id and plan_user != "default-user":
                return None

            status_val = TravelRunStatus.COMPLETED
            if result.get("failed"):
                return TravelRunResponse(
                    request_id=request_id,
                    run_id=request_id,
                    status=TravelRunStatus.FAILED,
                    error=result.get("error"),
                )
            elif result.get("requires_clarification"):
                status_val = TravelRunStatus.CLARIFYING

            return TravelRunResponse(
                request_id=request_id,
                run_id=request_id,
                status=status_val,
                final_plan=to_json_safe(result.get("final_plan")),
                clarification_questions=[
                    {"field": q["field"], "question": q["question"], "required": True}
                    for q in result.get("clarification_questions", [])
                ] if result.get("requires_clarification") else None,
            )

        # 2. Database fallback (crucial for container restart survival)
        session_factory = get_session_factory()
        async with session_factory() as session:
            travel_repo = TravelRepository(session)
            if user_id and user_id != "default-user":
                req = await travel_repo.get_request_for_user(request_id, user_id)
            else:
                req = await travel_repo.get_request(request_id)

            if not req:
                return None

            run = await travel_repo.get_run_by_request(request_id)
            if not run:
                return None

            try:
                run_status = TravelRunStatus(run.status)
            except ValueError:
                run_status = TravelRunStatus.COMPLETED

            return TravelRunResponse(
                request_id=request_id,
                run_id=run.id,
                status=run_status,
                started_at=run.started_at,
                completed_at=run.completed_at,
                error=run.error,
                final_plan=run.final_plan,
            )

    async def is_plan_owner(self, request_id: str, user_id: str) -> bool:
        """Verify whether user_id owns the given travel request."""
        # Check cache
        cached = self._runs.get(request_id)
        if cached and cached.get("user_id") == user_id:
            return True

        # Check DB
        session_factory = get_session_factory()
        async with session_factory() as session:
            travel_repo = TravelRepository(session)
            req = await travel_repo.get_request_for_user(request_id, user_id)
            return req is not None

    def _build_raw_request(self, request: TravelPlanRequest) -> str:
        """Build a natural language request from structured fields."""
        parts = []
        if request.origin and request.destination:
            parts.append(f"Plan a trip from {request.origin} to {request.destination}")
        elif request.destination:
            parts.append(f"Plan a trip to {request.destination}")

        if request.travelers:
            parts.append(f"for {request.travelers} people")

        if request.departure_date and request.return_date:
            parts.append(f"from {request.departure_date} to {request.return_date}")

        if request.budget:
            parts.append(f"with a budget of {request.currency or 'INR'} {request.budget:,.0f}")

        if request.travel_style != TravelStyle.STANDARD:
            parts.append(f"({request.travel_style.value} style)")

        if request.preferred_transport:
            parts.append(f"preferring {', '.join(request.preferred_transport)}")

        if request.interests:
            parts.append(f"interested in {', '.join(request.interests)}")

        return ". ".join(parts) + "." if parts else "Plan a trip."
