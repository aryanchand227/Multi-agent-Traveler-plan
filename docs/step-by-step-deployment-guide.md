# 🚀 Complete Beginner Step-by-Step Deployment Guide
### Multi-Agent AI Travel Planner (GitHub ➔ Render ➔ Vercel)

This guide takes you through the entire deployment process from start to finish—even if you have never deployed an app before.

---

## 📑 Table of Contents
1. [How GitHub Works in this Architecture](#1-how-github-works-in-this-architecture)
2. [Step 1: Push Your Code to GitHub](#step-1-push-your-code-to-github)
3. [Step 2: Create a Render Account & Deploy Backend + Database](#step-2-create-a-render-account--deploy-backend--database)
4. [Step 3: Create a Vercel Account & Deploy Frontend](#step-3-create-a-vercel-account--deploy-frontend)
5. [Step 4: Connect Frontend and Backend (The Handshake)](#step-4-connect-frontend-and-backend-the-handshake)
6. [Step 5: Test the Live Deployed Application](#step-5-test-the-live-deployed-application)
7. [Step 6: How Future Code Changes & Updates Work](#step-6-how-future-code-changes--updates-work)

---

## 1. How GitHub Works in this Architecture

### What is GitHub's Role?
GitHub acts as the **central single source of truth** and the **trigger engine** for your deployments.

```text
               Your Laptop
             (Local Codebase)
                   │
                   │ git push origin main
                   ▼
               GitHub Repository
             (ai-travel-agent)
                   │
         ┌─────────┴─────────┐
         │ (Watches backend) │ (Watches frontend)
         ▼                   ▼
    Render.com           Vercel.com
 (FastAPI Backend     (Next.js Frontend
  + PostgreSQL DB)        Website)
```

### Key Principles:
1. **Monorepo Structure**: Both `backend/` (FastAPI) and `frontend/` (Next.js) live in the same GitHub repository.
2. **Automated Continuous Deployment (CI/CD)**:
   - When you push changes to GitHub, **Render** automatically detects changes in the `backend/` directory and rebuilds your API.
   - Simultaneously, **Vercel** detects changes in the `frontend/` directory and rebuilds your user interface.
3. **Secret Hygiene**: Real secrets (like your Groq API key, database passwords, and JWT secret) are **never pushed to GitHub**. They are kept in your local `.env` and typed directly into the Render/Vercel private settings dashboards.

---

## Step 1: Push Your Code to GitHub

### 1.1 Create a New Repository on GitHub
1. Open your browser and go to [github.com/new](https://github.com/new).
2. Sign in to your GitHub account (or sign up if you don't have one).
3. Fill in:
   - **Repository name**: `ai-travel-agent` (or any name you prefer)
   - **Visibility**: Select **Public** or **Private** (Private is fine, Render & Vercel can connect to private repos)
   - **Initialize repository with**: Leave **ALL checkboxes unchecked** (Do NOT add a README, .gitignore, or license, as we already have them in our project).
4. Click **Create repository**.
5. Copy the HTTPS repository URL (it looks like `https://github.com/YOUR_USERNAME/ai-travel-agent.git`).

---

### 1.2 Push Your Local Code via PowerShell
Open PowerShell in `d:\Multi_Agent\ai-travel-agent` and run the following commands:

```powershell
# 1. Stage all project files (ignoring .env and virtual environments automatically)
git add .

# 2. Check what is staged (you should see green files, and NO .env files)
git status

# 3. Create your initial commit
git commit -m "feat: complete production-ready multi-agent travel planner"

# 4. Ensure your default branch is named 'main'
git branch -M main

# 5. Link your local project to your new GitHub repository (replace with your real URL)
git remote add origin https://github.com/YOUR_USERNAME/ai-travel-agent.git

# 6. Push your code to GitHub
git push -u origin main
```

> **Note**: If Git asks you to authenticate, sign in with your GitHub credentials or Personal Access Token.

---

## Step 2: Create a Render Account & Deploy Backend + Database

Render will host your **FastAPI Python server** and your **PostgreSQL database**.

### 2.1 Create an Account on Render
1. Go to [render.com](https://render.com).
2. Click **Get Started** or **Sign In**.
3. **Important**: Choose **Sign in with GitHub**. This allows Render to access your GitHub repositories with one click.

---

### 2.2 Create the PostgreSQL Database
1. In the Render Dashboard, click the blue **New +** button in the top right.
2. Select **PostgreSQL**.
3. Fill in the fields:
   - **Name**: `travel-planner-db`
   - **Database**: `travel_planner`
   - **User**: `travel_user`
   - **Region**: Choose the region closest to you (e.g., `Oregon (US West)` or `Frankfurt (EU)`)
   - **PostgreSQL Version**: `16`
   - **Plan**: Select **Free** (or Starter $7/mo)
4. Click **Create Database**.
5. Render will take ~1 minute to create your database.
6. Once it displays **Available**, scroll down to the **Connections** section:
   - Find **Internal Database URL** (e.g. `postgres://travel_user:xxxx@dpg-xxxx-a/travel_planner`)
   - Click the copy button next to it.
   - Save this URL in a notepad!

> ⚠️ **CRITICAL SQLALCHEMY RULE**:
> Render gives you a URL starting with `postgres://` or `postgresql://`.
> Our async backend requires the `asyncpg` driver!
> You **MUST** change the beginning from `postgres://` (or `postgresql://`) to:
> `postgresql+asyncpg://`
> 
> *Example:*
> `postgresql+asyncpg://travel_user:password123@dpg-cxxxx-a/travel_planner`

---

### 2.3 Create the FastAPI Web Service
1. In the Render Dashboard, click the blue **New +** button in the top right.
2. Select **Web Service**.
3. Choose **Build and deploy from a Git repository** -> click **Next**.
4. Select your `ai-travel-agent` repository from the list (click **Connect**).
5. Configure the service settings:
   - **Name**: `travel-planner-api`
   - **Region**: Choose the **same region** you chose for your database!
   - **Branch**: `main`
   - **Root Directory**: `backend` *(CRITICAL: type `backend` so Render only runs the Python app)*
   - **Runtime**: `Python`
   - **Build Command**:
     ```bash
     pip install --no-cache-dir -r requirements.txt && alembic upgrade head
     ```
   - **Start Command**:
     ```bash
     uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```
   - **Plan**: Select **Free** (or Starter $7/mo)

6. Scroll down to **Environment Variables** and click **Add Environment Variable** for each:

| Key | Value | Notes |
|---|---|---|
| `APP_ENV` | `production` | Enforces production security checks |
| `DEBUG` | `false` | Hides internal tracebacks |
| `PYTHON_VERSION` | `3.11.9` | Reliable Python version |
| `DATABASE_URL` | *(paste your internal database URL with `postgresql+asyncpg://`)* | Copied from Step 2.2 |
| `JWT_SECRET_KEY` | *(generate any random 32+ character string)* | e.g. `a8f3b2c9e1d4f7a0b5c8e2d1f4a7b0c3` |
| `TRUST_ALL_PROXIES` | `true` | Allows Render's reverse proxy to pass IP addresses safely |
| `LLM_PROVIDER` | `groq` | Specifies Groq as the AI provider |
| `LLM_MODEL` | `openai/gpt-oss-120b` | Working Groq model identifier |
| `LLM_BASE_URL` | `https://api.groq.com/openai/v1` | Groq endpoint |
| `LLM_API_KEY` | *(Your real Groq API key: `gsk_...`)* | From [console.groq.com/keys](https://console.groq.com/keys) |
| `RATE_LIMIT_ENABLED` | `true` | Enables anti-abuse limiter |
| `TRAVEL_PLANS_PER_USER_PER_DAY` | `10` | Daily limit per account |
| `MAX_CONCURRENT_PLANS_TOTAL` | `3` | Max simultaneous workflows |
| `DAILY_LLM_BUDGET_USD` | `2.00` | Safety limit on Groq spend |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | We will update this with Vercel URL in Step 4 |

7. Click **Create Web Service**.
8. Render will now start building your backend. You can watch the build logs in real-time.
9. When the log displays `Application startup complete` and **Live**, copy your public backend URL from the top left of the Render dashboard:
   - Example: `https://travel-planner-api-xxxx.onrender.com`

---

### 2.4 Verify Backend is Healthy
Open your browser and visit:
1. `https://travel-planner-api-xxxx.onrender.com/api/v1/health`
   - Should return: `{"status":"healthy","app_name":"AI Travel Planner",...}`
2. `https://travel-planner-api-xxxx.onrender.com/api/v1/ready`
   - Should return: `{"status":"ready","database":"connected",...}`

✅ **Your backend and PostgreSQL database are fully operational!**

---

## Step 3: Create a Vercel Account & Deploy Frontend

Vercel will host your **Next.js frontend application** on a worldwide CDN with free HTTPS.

### 3.1 Create an Account on Vercel
1. Go to [vercel.com](https://vercel.com).
2. Click **Sign Up**.
3. Choose **Continue with GitHub**.

---

### 3.2 Import and Configure Your Project
1. In the Vercel Dashboard, click **Add New...** -> **Project**.
2. Find your `ai-travel-agent` repository and click **Import**.
3. In the **Configure Project** screen:
   - **Project Name**: `ai-travel-planner` (or any name you like)
   - **Framework Preset**: `Next.js` (detected automatically)
   - **Root Directory**: Click the **Edit** button next to `./` and select `frontend`! *(CRITICAL: Must be `frontend`)*
   - **Build and Output Settings**: Leave default (`npm run build`).

4. Open the **Environment Variables** dropdown and add:
   - **Key**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://travel-planner-api-xxxx.onrender.com` *(Paste your Render backend URL from Step 2.3. Make sure there is **NO trailing slash** `/` at the end!)*
5. Click **Deploy**.
6. Vercel will compile your Next.js application in about 1-2 minutes.
7. When complete, fireworks will display with **Congratulations!**
8. Click on the preview image or click the domain link to view your live frontend:
   - Example: `https://ai-travel-planner-xxxx.vercel.app`

---

## Step 4: Connect Frontend and Backend (The Handshake)

By default, web browsers block web pages on one domain (`https://ai-travel-planner-xxxx.vercel.app`) from talking to an API on another domain (`https://travel-planner-api-xxxx.onrender.com`) unless the backend explicitly authorizes it via **CORS (Cross-Origin Resource Sharing)**.

### Update Render CORS:
1. Go back to your [Render Dashboard](https://dashboard.render.com).
2. Click on your `travel-planner-api` Web Service.
3. In the left navigation, click **Environment**.
4. Find the `CORS_ORIGINS` variable.
5. Click **Edit** and set its value to include your Vercel domain:
   ```json
   ["https://ai-travel-planner-xxxx.vercel.app", "http://localhost:3000"]
   ```
   *(Replace with your actual Vercel domain! Remember: no trailing slash)*.
6. Click **Save Changes**.
7. Render will automatically redeploy the service in ~20 seconds to apply the new CORS policy.

---

## Step 5: Test the Live Deployed Application

Now test your production setup:

1. Open your Vercel website: `https://ai-travel-planner-xxxx.vercel.app`
2. Click **Sign Up** in the top navigation.
3. Register with an email (e.g. `mytest@example.com`) and password (minimum 8 characters).
4. Notice you are automatically logged in, and your email/name appears in the header.
5. Click **Plan Trip**.
6. Enter a sample trip:
   - Origin: `Mumbai`
   - Destination: `Goa`
   - Travelers: `2`
   - Budget: `25000`
   - Travel Style: `Standard`
7. Click **Plan My Trip**.
8. Watch the **Real-time Agent Progress**:
   - `IntakeAgent` ➔ `ClarificationAgent` ➔ `TravelManager` ➔ `TransportSupervisor` ➔ `AccommodationAgent` ➔ `DestinationAgent` ➔ `WeatherAgent` ➔ `BudgetAgent` ➔ `ItineraryAgent` ➔ `ValidationAgent` ➔ `FinalPlannerAgent`.
9. The **Results Dashboard** will load with:
   - Trip summary
   - Selected vs Cheapest vs Fastest transport options
   - Selected accommodation
   - Weather forecast
   - Day-by-day itinerary
   - Deterministic budget breakdown
   - Interactive replanning bar
10. Click **Preferences** in the header to save your preferred travel style and currency, and refresh to verify they persist from PostgreSQL.

---

## Step 6: How Future Code Changes & Updates Work

Once this setup is complete, you never need to manually reconfigure Render or Vercel again!

Whenever you make improvements or bug fixes on your laptop:

```powershell
# 1. Edit your code in VS Code / Antigravity

# 2. Stage your changes
git add .

# 3. Commit your changes
git commit -m "feat: improve itinerary UI and add new prompt features"

# 4. Push to GitHub
git push origin main
```

### What Happens Automatically:
- GitHub receives your commit on branch `main`.
- **Render** detects the push and immediately redeploys the backend.
- **Vercel** detects the push and immediately rebuilds the frontend.
- Within 2 minutes, your live production site is updated with your latest code!

---

## 🛠️ Summary Reference Sheet

| Item | Local Development | Production |
|---|---|---|
| **Frontend URL** | `http://localhost:3000` | `https://your-app.vercel.app` |
| **Backend URL** | `http://localhost:8000` | `https://your-api.onrender.com` |
| **Database** | SQLite (`travel_planner.db`) | Managed PostgreSQL (`asyncpg`) |
| **Authentication** | Auto-provisions dev user | Secure Bcrypt + JWT (24h) |
| **AI Provider** | Groq (`openai/gpt-oss-120b`) | Groq (`openai/gpt-oss-120b`) |
| **Rate Limiter** | Active in-memory | Active in-memory + Semaphore |
| **Budget Cap** | Configured in `.env` | $2.00/day hard limit on Render |
