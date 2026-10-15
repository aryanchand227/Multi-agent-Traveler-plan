"""API v1 router — aggregates all endpoint routers."""
from fastapi import APIRouter

from app.api.v1.endpoints import health, travel, preferences, events, auth

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(travel.router, prefix="/travel", tags=["Travel"])
api_router.include_router(preferences.router, prefix="/preferences", tags=["Preferences"])
api_router.include_router(events.router, prefix="/travel", tags=["Events"])

