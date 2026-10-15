# Production Deployment Guide

This guide covers deploying the Multi-Agent AI Travel Planner using **Render** for the backend + database and **Vercel** for the frontend.

---

## 1. Architecture Overview

```text
                     Internet
                        │
                        ▼
               ┌────────────────┐
               │ Vercel (HTTPS) │
               │ Next.js App    │
               └───────┬────────┘
                       │ HTTPS API Requests (with JWT & CORS)
                       ▼
               ┌────────────────┐
               │ Render (HTTPS) │
               │ FastAPI API    │
               └───────┬────────┘
                       │
         ┌─────────────┴─────────────┐
         ▼                           ▼
┌──────────────────┐       ┌──────────────────┐
│ Supabase Postgres│       │     Groq LLM     │
│   (Free Tier)    │       │   API Gateway    │
│ (Users, Plans,   │       │(14 Travel Agents)│
│  Usage, Memory)  │       └──────────────────┘
└──────────────────┘
```

---

## 2. Part 1: Provision Supabase PostgreSQL Database (Free)

1. Sign up or log into [Supabase](https://supabase.com).
2. Create a new project on the **Free** tier.
3. Once provisioned, click **Connect** in the top navigation bar.
4. Under the **URI** tab, copy the connection string:
   - **Pooler (Port 6543, Transaction mode)**: Recommended for cloud web services.
   - **Direct (Port 5432)**: Direct PostgreSQL connection.
5. Replace `[YOUR-PASSWORD]` with your actual Supabase database password.
6. The backend's `app/db/url.py` automatically normalizes `postgresql://` to `postgresql+asyncpg://`, handles SSL, and configures statement caches.

---

## 3. Part 2: Deploy Backend Web Service on Render (Free)

### Option A: Using the Render Blueprint (Recommended)
1. Push your repository to GitHub.
2. In the [Render Dashboard](https://dashboard.render.com), click **New +** -> **Blueprint**.
3. Connect your repository and select `render.yaml`.
4. Render detects the web service configured on the **Free** plan.
5. In the settings, provide:
   - `DATABASE_URL`: Your Supabase connection string.
   - `LLM_API_KEY`: Your real Groq API key (`gsk_...`).
   - `CORS_ORIGINS`: `["http://localhost:3000"]` (update once frontend is created).
6. Click **Apply**.

---

### Option B: Manual Configuration

#### Step 1: Create Web Service
1. In Render Dashboard, click **New +** -> **Web Service**.
2. Connect your GitHub repository.
3. Configure the service:
   - **Name**: `travel-planner-api`
   - **Root Directory**: `backend`
   - **Runtime**: `Python`
   - **Build Command**: `pip install --no-cache-dir -r requirements.txt && alembic upgrade head`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path**: `/api/v1/health`
4. Configure Environment Variables:

| Variable | Recommended Value | Notes |
|---|---|---|
| `APP_ENV` | `production` | Enables JSON logging & strict security checks |
| `DEBUG` | `false` | Disables traceback exposure |
| `DATABASE_URL` | `postgresql+asyncpg://user:pass@host/db` | Use Render Internal DB URL with asyncpg prefix |
| `JWT_SECRET_KEY` | *(generate random 32+ hex string)* | `python -c "import secrets; print(secrets.token_hex(32))"` |
| `TRUST_ALL_PROXIES` | `true` | Required for Render reverse proxy IP resolution |
| `CORS_ORIGINS` | `["https://your-frontend.vercel.app"]` | Your Vercel domain |
| `LLM_PROVIDER` | `groq` | Configured LLM provider |
| `LLM_MODEL` | `openai/gpt-oss-120b` | Supported working Groq model |
| `LLM_BASE_URL` | `https://api.groq.com/openai/v1` | Groq OpenAI-compatible base URL |
| `LLM_API_KEY` | `gsk_...` | Groq secret API key |
| `RATE_LIMIT_ENABLED`| `true` | Enables sliding window limiter |
| `TRAVEL_PLANS_PER_USER_PER_DAY` | `10` | Daily limit per account |
| `MAX_CONCURRENT_PLANS_TOTAL` | `3` | Prevents server starvation |
| `DAILY_LLM_BUDGET_USD` | `2.00` | Hard stop on daily LLM consumption |

5. Deploy and verify:
   - Visit `https://your-backend.onrender.com/api/v1/health` (should return `status: "healthy"`).
   - Visit `https://your-backend.onrender.com/api/v1/ready` (should return `database: "connected"`).

---

## 3. Part 2: Deploy Frontend on Vercel

1. In the [Vercel Dashboard](https://vercel.com/new), import your GitHub repository.
2. In Project Configuration:
   - **Framework Preset**: Next.js
   - **Root Directory**: Click edit and choose `frontend`.
   - **Build Command**: `npm run build` (default)
   - **Output Directory**: `.next` (default)
3. Add Environment Variable:

| Key | Value | Notes |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `https://your-backend.onrender.com` | No trailing slash! Points to your Render backend |

4. Click **Deploy**.
5. Once deployed, copy your assigned Vercel URL (e.g. `https://travel-planner.vercel.app`).
6. Return to your Render backend settings and update `CORS_ORIGINS` to include your Vercel URL:
   `["https://travel-planner.vercel.app"]`

---

## 4. Free Tier vs Production Limitations

| Feature | Free Tier Demo | Production Starter Tier ($7-$14/mo) |
|---|---|---|
| **Render Web Service** | Spins down after 15 min inactivity; cold start 50-70 seconds | Always-on, 512MB RAM, no cold starts |
| **Render Database** | Expires after 30 days (Render free Postgres policy) | Persistent PostgreSQL, automatic backups |
| **Real-time SSE** | Free tier may drop idle connections after 60s | Stable SSE streaming with 15s keep-alive heartbeats |
| **Groq Free Quota** | ~30 requests/minute depending on model | Paid tier allows higher TPM/RPM |
