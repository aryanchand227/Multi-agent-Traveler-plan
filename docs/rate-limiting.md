# Rate Limiting & Abuse Prevention

The application implements a multi-tier rate limiting system to protect against denial of service, credential stuffing, and uncontrolled LLM API quota consumption.

---

## 1. Rate Limiting Rules & Defaults

Configured via environment variables in `app/core/config.py`:

| Target / Operation | Limit | Window | Tracking Key | Behavior on Breach |
|---|---|---|---|---|
| **Auth (Login/Register)** | 5 requests | 60 seconds | `auth:<client_ip>` | HTTP 429 with `Retry-After` header |
| **Anonymous Traffic** | 10 requests | 60 seconds | `plan_ip:<client_ip>` | HTTP 429 with `Retry-After` header |
| **User Planning** | 20 requests | 60 seconds | `plan_user:<user_id>` | HTTP 429 with `Retry-After` header |
| **Daily Plans per User** | 10 plans | 24 hours | `user_id` database records | HTTP 429 with recoverable error |
| **Active Concurrency** | 3 workflows | Real-time | Global Semaphore | HTTP 429: "Server is currently processing maximum concurrent plans" |

---

## 2. Sliding Window Algorithm

Implemented in `backend/app/core/rate_limit.py`:
- Records request timestamps in memory using thread-safe `asyncio.Lock()`.
- Calculates current window `[now - window_seconds, now]`.
- Automatically computes exact `Retry-After` in seconds:
  ```python
  retry_after = max(1, int(earliest + window_seconds - now))
  ```
- Periodically purges stale entries to prevent memory leaks.

---

## 3. Concurrency Semaphore

Generating a travel plan invokes 14 AI agents and several structured model evaluations. Running dozens of workflows concurrently would exhaust server memory and trigger Groq rate limits.

The global semaphore (`get_workflow_semaphore()`) limits active LangGraph pipeline invocations:
```python
semaphore = get_workflow_semaphore()
if semaphore.locked():
    raise HTTPException(status_code=429, detail="Server busy...")
async with semaphore:
    result = await self._run_graph_with_events(...)
```

---

## 4. Configuration Reference

```env
# Enable/disable rate limiting
RATE_LIMIT_ENABLED=true

# Auth endpoint rate limit
RATE_LIMIT_AUTH_PER_MINUTE=5

# Anonymous IP rate limit
RATE_LIMIT_ANONYMOUS_PER_MINUTE=10

# Authenticated user per-minute rate limit
RATE_LIMIT_USER_PER_MINUTE=20

# Daily plan limits
TRAVEL_PLANS_PER_USER_PER_DAY=10
TRAVEL_PLANS_PER_IP_PER_DAY=20

# Max concurrent heavy agent workflows
MAX_CONCURRENT_PLANS_TOTAL=3
```
