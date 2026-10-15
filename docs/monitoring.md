# Production Monitoring & Logging

The platform incorporates structured logging and health probes designed for production visibility on Render and Vercel.

---

## 1. Health & Readiness Probes

Base path: `/api/v1`

### Liveness Probe (`GET /api/v1/health`)
Returns `HTTP 200 OK` as long as the Uvicorn process is running. Used by Render to verify container liveness.
```json
{
  "status": "healthy",
  "app_name": "AI Travel Planner",
  "version": "1.0.0",
  "environment": "production",
  "database": "postgresql",
  "llm_provider": "groq",
  "mock_providers": true,
  "timestamp": "2026-10-15T13:45:00.000Z"
}
```

### Readiness Probe (`GET /api/v1/ready`)
Tests database connectivity with an asynchronous `SELECT 1` without invoking any LLM models.
- If database is connected: returns `HTTP 200 OK` with `status: "ready"`.
- If database is unreachable: returns `HTTP 503 Service Unavailable` with `status: "not_ready"`.

---

## 2. Structured JSON Logging

Implemented in `backend/app/core/logging.py` using `structlog`:
- **Development**: Formatted with human-readable colored console output.
- **Production (`APP_ENV=production`)**: Outputs standard single-line JSON format directly into `stdout`, captured by Render Log Streams.

### Log Redaction & Sanitization Policy
The logging system explicitly redacts:
- Passwords and password hashes
- JWT secret keys
- Groq / LLM API keys
- Authorization headers (`Bearer ...`)
- Raw user credit card or payment information

---

## 3. Log Inspection

### On Render
1. Open [Render Dashboard](https://dashboard.render.com).
2. Select your `travel-planner-api` web service.
3. Click **Logs** on the left menu.
4. Filter by severity or search for `request_id` to trace a specific travel plan across all 14 agents.

### On Vercel
1. Open [Vercel Dashboard](https://vercel.com).
2. Select your travel planner project -> **Deployments**.
3. Click your active production deployment -> **Runtime Logs**.
