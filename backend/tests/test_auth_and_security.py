"""Tests for Authentication, Authorization/User Isolation, Rate Limiting, and Readiness."""
from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.core.rate_limit import reset_rate_limiter


@pytest.fixture(autouse=True)
def clean_rate_limits():
    """Reset rate limiter counts before each test to ensure test isolation."""
    reset_rate_limiter()
    yield
    reset_rate_limiter()


@pytest.mark.asyncio
async def test_readiness_probe(client: AsyncClient):
    """Test that GET /api/v1/ready verifies database connectivity."""
    response = await client.get("/api/v1/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["database"] == "connected"



@pytest.mark.asyncio
async def test_user_registration_and_login_flow(client: AsyncClient):
    """Test user registration, duplicate prevention, and authentication login."""
    # 1. Register a new user
    reg_payload = {
        "email": "traveler@example.com",
        "password": "SecurePassword123!",
        "display_name": "Traveler One",
    }
    reg_resp = await client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_resp.status_code == 201
    reg_data = reg_resp.json()
    assert "access_token" in reg_data
    assert reg_data["user"]["email"] == "traveler@example.com"
    token = reg_data["access_token"]

    # 2. Duplicate registration must fail with 400
    dup_resp = await client.post("/api/v1/auth/register", json=reg_payload)
    assert dup_resp.status_code == 400

    # 3. Login with wrong password must fail with 401
    bad_login = await client.post(
        "/api/v1/auth/login",
        json={"email": "traveler@example.com", "password": "WrongPassword"},
    )
    assert bad_login.status_code == 401

    # 4. Login with correct password must succeed
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "traveler@example.com", "password": "SecurePassword123!"},
    )
    assert login_resp.status_code == 200
    login_data = login_resp.json()
    assert "access_token" in login_data

    # 5. Access /me with token
    me_resp = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "traveler@example.com"


@pytest.mark.asyncio
async def test_user_data_isolation(client: AsyncClient):
    """Test that User A cannot read or mutate User B's travel plans or preferences."""
    # Register User A
    user_a_resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "user_a@example.com", "password": "PasswordA123!"},
    )
    token_a = user_a_resp.json()["access_token"]

    # Register User B
    user_b_resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "user_b@example.com", "password": "PasswordB123!"},
    )
    token_b = user_b_resp.json()["access_token"]

    # User A creates a travel plan
    plan_payload = {
        "origin": "Mumbai",
        "destination": "Goa",
        "travelers": 2,
        "budget": 20000,
        "travel_style": "standard",
    }
    create_resp = await client.post(
        "/api/v1/travel/plan",
        json=plan_payload,
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert create_resp.status_code == 200
    request_id = create_resp.json()["request_id"]

    # User A can access the plan
    get_a_resp = await client.get(
        f"/api/v1/travel/{request_id}",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert get_a_resp.status_code == 200

    # User B CANNOT access User A's plan (must return 404)
    get_b_resp = await client.get(
        f"/api/v1/travel/{request_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert get_b_resp.status_code == 404

    # User B CANNOT subscribe to User A's events (must return 403)
    events_b_resp = await client.get(
        f"/api/v1/travel/{request_id}/events",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert events_b_resp.status_code == 403


@pytest.mark.asyncio
async def test_auth_rate_limiting(client: AsyncClient):
    """Test that repeated rapid login attempts are throttled with HTTP 429."""
    # settings.rate_limit_auth_per_minute is 5
    for _ in range(5):
        await client.post(
            "/api/v1/auth/login",
            json={"email": "attacker@example.com", "password": "pass"},
        )

    # 6th attempt must receive HTTP 429 Too Many Requests
    throttled = await client.post(
        "/api/v1/auth/login",
        json={"email": "attacker@example.com", "password": "pass"},
    )
    assert throttled.status_code == 429
    assert "Retry-After" in throttled.headers


# --- CORS Configuration & Preflight Regression Tests ---

PROD_ORIGIN = "https://multi-agent-traveler-plan.vercel.app"


@pytest.mark.asyncio
async def test_cors_preflight_production_origin_travel_plan(client: AsyncClient):
    """OPTIONS preflight request to /api/v1/travel/plan from production origin must return 200 with CORS headers."""
    response = await client.options(
        "/api/v1/travel/plan",
        headers={
            "Origin": PROD_ORIGIN,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type, authorization",
        },
    )
    assert response.status_code == 200
    headers = response.headers
    assert headers.get("access-control-allow-origin") == PROD_ORIGIN
    assert headers.get("access-control-allow-credentials") == "true"
    # Never wildcard origin when credentials are enabled
    assert headers.get("access-control-allow-origin") != "*"
    allowed_methods = headers.get("access-control-allow-methods", "")
    assert "POST" in allowed_methods or "*" in allowed_methods


@pytest.mark.asyncio
async def test_cors_simple_request_production_origin(client: AsyncClient):
    """GET /api/v1/ready with production Origin header must include Access-Control-Allow-Origin."""
    response = await client.get("/api/v1/ready", headers={"Origin": PROD_ORIGIN})
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == PROD_ORIGIN
    assert response.headers.get("access-control-allow-credentials") == "true"


@pytest.mark.asyncio
async def test_cors_error_responses_receive_cors_headers(client: AsyncClient):
    """Error responses (404, 422, 500) must also receive CORS headers so browsers can read the response."""
    # 404 Not Found
    r_404 = await client.get("/api/v1/nonexistent", headers={"Origin": PROD_ORIGIN})
    assert r_404.status_code == 404
    assert r_404.headers.get("access-control-allow-origin") == PROD_ORIGIN

    # 422 Validation Error
    r_422 = await client.post("/api/v1/auth/register", json={}, headers={"Origin": PROD_ORIGIN})
    assert r_422.status_code == 422
    assert r_422.headers.get("access-control-allow-origin") == PROD_ORIGIN


@pytest.mark.asyncio
async def test_cors_unauthorized_origin_rejected(client: AsyncClient):
    """Disallowed origins must not receive an Access-Control-Allow-Origin header."""
    evil_origin = "https://unauthorized-malicious-site.com"
    response = await client.options(
        "/api/v1/travel/plan",
        headers={
            "Origin": evil_origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    # CORSMiddleware does not grant allow-origin to unauthorized origins
    assert response.headers.get("access-control-allow-origin") is None


def test_cors_origins_parsing_robustness():
    """Verify that Settings parses various CORS_ORIGINS environment formats without trailing slashes."""
    from app.core.config import Settings

    # JSON array with trailing slashes
    s1 = Settings(cors_origins='["https://multi-agent-traveler-plan.vercel.app/", "http://localhost:3000/"]')
    assert "https://multi-agent-traveler-plan.vercel.app" in s1.cors_origins
    assert "https://multi-agent-traveler-plan.vercel.app/" not in s1.cors_origins
    assert "http://localhost:3000" in s1.cors_origins

    # Comma-separated string with spaces and trailing slashes
    s2 = Settings(cors_origins="https://multi-agent-traveler-plan.vercel.app/ , http://localhost:3000/ ")
    assert "https://multi-agent-traveler-plan.vercel.app" in s2.cors_origins
    assert "http://localhost:3000" in s2.cors_origins

    # Single-quoted string array
    s3 = Settings(cors_origins="['https://multi-agent-traveler-plan.vercel.app/']")
    assert "https://multi-agent-traveler-plan.vercel.app" in s3.cors_origins

    # Default settings must always include production Vercel frontend
    s_default = Settings()
    assert "https://multi-agent-traveler-plan.vercel.app" in s_default.cors_origins



# --- Authentication & Token Lifecycle Regression Tests ---


@pytest.mark.asyncio
async def test_unauthenticated_request_rejected_in_production(client: AsyncClient, monkeypatch):
    """Unauthenticated requests to protected endpoints must return 401 in production environment."""
    monkeypatch.setenv("APP_ENV", "production")

    # GET /preferences without token
    pref_resp = await client.get("/api/v1/preferences")
    assert pref_resp.status_code == 401
    assert "Authentication required" in pref_resp.json()["detail"]

    # POST /travel/plan without token
    plan_resp = await client.post(
        "/api/v1/travel/plan",
        json={"origin": "Delhi", "destination": "Goa", "budget": 15000},
    )
    assert plan_resp.status_code == 401
    assert "Authentication required" in plan_resp.json()["detail"]


@pytest.mark.asyncio
async def test_expired_token_rejected(client: AsyncClient):
    """Expired JWT access token must return 401 with clear expiration message."""
    import datetime
    from app.core.security import create_access_token

    # Create a token that expired 10 minutes ago
    expired_token = create_access_token(
        data={"sub": "user-123", "email": "expired@example.com"},
        expires_delta=datetime.timedelta(minutes=-10),
    )

    resp = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Token has expired. Please log in again."


@pytest.mark.asyncio
async def test_invalid_token_rejected(client: AsyncClient):
    """Malformed or invalid JWT token must return 401 with clear invalid token message."""
    resp = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid.malformed.jwt.token"},
    )
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid authentication token. Please log in again."
