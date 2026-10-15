# Troubleshooting & Operational Guide

Common production issues and step-by-step diagnostic and remediation instructions.

---

## 1. CORS Issues (Cross-Origin Request Blocked)

### Symptom
Browser console displays:
`Access to fetch at 'https://api.onrender.com/api/v1/travel/plan' from origin 'https://app.vercel.app' has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.`

### Fix
1. Verify `CORS_ORIGINS` in Render Web Service environment variables.
2. Ensure there is **no trailing slash** on the URL:
   - ✅ Correct: `["https://my-app.vercel.app"]`
   - ❌ Incorrect: `["https://my-app.vercel.app/"]`
3. If using Vercel preview branch deployments, add them or use wildcard preview origins:
   ```json
   ["https://my-app.vercel.app", "http://localhost:3000"]
   ```

---

## 2. Database Connection Failures (`asyncpg`)

### Symptom
Backend logs display:
`sqlalchemy.exc.NoSuchModuleError: Can't load plugin: sqlalchemy.dialects:postgresql`

### Fix
Render provides PostgreSQL connection strings with the prefix `postgresql://` or `postgres://`. SQLAlchemy async engine requires the asyncpg driver prefix:
- Replace `postgresql://` with `postgresql+asyncpg://` in your `DATABASE_URL` environment variable.

---

## 3. Server-Sent Events (SSE) Progress Drops

### Symptom
The UI stays on "Initializing agents..." and SSE stream closes after 60 seconds without finishing.

### Fix
1. Reverse proxies (Cloudflare, Render, AWS) close idle HTTP connections if no bytes are sent for 60 seconds.
2. In `backend/app/api/v1/endpoints/events.py`, heartbeat pings are configured to emit every 15 seconds:
   ```python
   EventSourceResponse(event_generator(request_id), ping=15)
   ```
3. Ensure the browser request passes credentials if authenticated cookies are used.

---

## 4. Render Cold Starts (Free Tier)

### Symptom
The first request after 15 minutes of inactivity takes 50-70 seconds.

### Explanation
Render free web services spin down after 15 minutes of inactivity. When the Next.js frontend sends a request, Render spins up the container and initializes the database connection.
- **Mitigation for Student Demo**: Add a friendly loading banner on the frontend indicating "Server waking up from standby (takes ~45s on free tier)..."
- **Permanent Fix**: Upgrade the Render web service to Starter tier ($7/month) to enable always-on background execution with 0 cold starts.

---

## 5. Groq Rate Limit / Quota Exceeded (`429`)

### Symptom
Backend logs display:
`openai.RateLimitError: Error code: 429 - Rate limit reached for model 'openai/gpt-oss-120b'`

### Fix
1. Verify your Groq plan limits at [Groq Rate Limits](https://console.groq.com/settings/limits).
2. The application will catch this and emit an error event to the frontend:
   `The AI travel assistant is currently busy. Please retry in a few moments.`
3. You can configure a fallback model in `LLM_MODEL` (e.g. `llama-3.3-70b-versatile`) if the 120b model encounters temporary regional capacity constraints.
