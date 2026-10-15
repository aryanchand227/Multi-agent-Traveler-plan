# AI Multi-Agent Travel Planner

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-15-black.svg?style=flat&logo=next.js&logoColor=white)](https://nextjs.org)
[![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-blue.svg?style=flat)](https://github.com/langchain-ai/langgraph)
[![Groq](https://img.shields.io/badge/LLM-Groq-orange.svg?style=flat)](https://groq.com)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6.svg?style=flat&logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A full-stack, enterprise-grade **Multi-Agent Travel Planning Platform** orchestrated by **LangGraph**, powered by **Groq** high-throughput LLMs, and built with **FastAPI**, **Next.js 15**, and **PostgreSQL**.

---

## Table of Contents

- [Overview](#overview)
- [Problem Statement & Motivation](#problem-statement--motivation)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [The 14 Specialized Agents](#the-14-specialized-agents)
- [Technology Stack](#technology-stack)
- [Mock Providers vs. Live Data](#mock-providers-vs-live-data)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Environment Configuration](#environment-configuration)
  - [Local Setup (Windows / Linux / macOS)](#local-setup-windows--linux--macos)
  - [Docker Compose Quickstart](#docker-compose-quickstart)
- [Testing](#testing)
- [API Documentation](#api-documentation)
- [Production Deployment](#production-deployment)
- [Security & Cost Guardrails](#security--cost-guardrails)
- [Current Limitations & Roadmap](#current-limitations--roadmap)
- [License](#license)

---

## Overview

Planning an end-to-end trip requires synthesizing dozens of interdependent constraints: travel logistics, multi-modal transport schedules, lodging proximities, seasonal weather risks, daily attraction capacities, and financial limits. 

The **AI Multi-Agent Travel Planner** solves this by decomposing travel planning into a coordinated collective of **14 specialized AI agents**. Guided by a central **LangGraph StateGraph**, each agent possesses dedicated domain expertise, isolated state contexts, and purpose-built tools.

---

## Problem Statement & Motivation

Traditional travel planners are either rigid search aggregators or single-prompt LLM chatbots:
- Aggregators show static lists without context-aware itinerary structuring.
- Single LLM chatbots suffer from context drift, hallucinated schedules, arithmetic errors on budgets, and lack of deterministic validation.

**Our Multi-Agent Architecture solves this through:**
1. **Separation of Concerns**: Specialized agents handle distinct domains (bus vs. train vs. flight vs. lodging vs. weather).
2. **Deterministic Rules + LLM Synthesis**: Calculations (budget subtotals, date spans) are handled by deterministic Python tools, while creative synthesis (recommendations, summaries) is handled by LLMs.
3. **Formal Verification**: A dedicated `ValidationAgent` programmatically audits itineraries against travel times and budget ceilings before finalizing the output.

---

## Key Features

- **Natural Language Trip Intake**: Convert prompts (e.g. *"Plan a 5-day budget trip from Hyderabad to Goa for 2 friends under ₹25,000"*) into structured travel plans.
- **Interactive Clarification Dialog**: Detects ambiguous constraints and prompts the user before launching expensive workflows.
- **14 Specialized Collaborative Agents**: Distributed graph orchestration powered by LangGraph.
- **Multi-Modal Transport Evaluation**: Compares buses, trains, and flights across duration, price, and convenience scores.
- **Live Agent Execution Progress (SSE)**: Real-time event streaming to the frontend so users watch agents deliberate and produce results.
- **Production Security & Auth**: Password hashing (passlib), cryptographically signed JWT bearer tokens, and IDOR mitigation.
- **Cost & Rate Control**: Proxy-aware IP rate limiting, concurrent workflow semaphores, and strict daily/monthly LLM spend caps.

---

## System Architecture

```
User → Next.js 15 Client → FastAPI Gateway (JWT / Rate Limiting)
                                     │
                                     ▼
                          LangGraph StateGraph
                                     │
                    ┌────────────────┴────────────────┐
                    │                                 │
           [Intake / Clarification]             [TravelManager]
                                                      │
         ┌──────────────────┬─────────────────────────┴─────────────────────────┐
         │                  │                         │                         │
┌────────────────┐  ┌────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│ Transport Sup. │  │ Accommodation  │       │   Destination   │       │     Weather     │
│  ┌───┬───┐     │  │     Agent      │       │      Agent      │       │      Agent      │
│  │Bus│Trn│Flt│ │  └───────┬────────┘       └────────┬────────┘       └────────┬────────┘
│  └───┴───┘     │          │                         │                         │
└────────┬───────┘          │                         │                         │
         └──────────────────┴─────────────┬───────────┴─────────────────────────┘
                                          │
                                          ▼
                               ┌─────────────────────┐
                               │     BudgetAgent     │
                               └──────────┬──────────┘
                                          │
                                          ▼
                               ┌─────────────────────┐
                               │   ItineraryAgent    │
                               └──────────┬──────────┘
                                          │
                                          ▼
                               ┌─────────────────────┐
                               │   ValidationAgent   │
                               └──────────┬──────────┘
                                          │
                                          ▼
                               ┌─────────────────────┐
                               │  FinalPlannerAgent  │
                               └─────────────────────┘
```

For an in-depth breakdown of state definitions, context builders, and graph transitions, see [docs/architecture.md](docs/architecture.md).

---

## The 14 Specialized Agents

| # | Agent Name | File Path | Core Role & Responsibilities |
|---|---|---|---|
| 1 | **IntakeAgent** | `backend/app/agents/intake.py` | Parses freeform user text into structured requirements (dates, origin, destination, budget, group size). |
| 2 | **ClarificationAgent** | `backend/app/agents/clarification.py` | Detects missing criteria (e.g. unknown dates or unspecified budget) and generates targeted clarifying questions. |
| 3 | **TravelManager** | `backend/app/agents/manager.py` | Top-level orchestrator that validates prerequisites and schedules transport, lodging, and activity sub-tasks. |
| 4 | **TransportSupervisor** | `backend/app/agents/transport_supervisor.py` | Manages transport sub-agents, aggregates multi-modal options, and produces a weighted ranking score. |
| 5 | **BusAgent** | `backend/app/agents/bus_agent.py` | Evaluates intercity bus schedules, operators, sleeper/seater categories, and pricing. |
| 6 | **TrainAgent** | `backend/app/agents/train_agent.py` | Evaluates train routes, coach classes (1A, 2A, 3A, SL), travel times, and rail schedules. |
| 7 | **FlightAgent** | `backend/app/agents/flight_agent.py` | Evaluates non-stop and connecting commercial flights, airline carriers, baggage allowances, and airfares. |
| 8 | **AccommodationAgent** | `backend/app/agents/accommodation_agent.py` | Selects hotels, hostels, and resorts tailored to style (budget, boutique, luxury) and location proximity. |
| 9 | **DestinationAgent** | `backend/app/agents/destination_agent.py` | Curates points of interest, cultural landmarks, local food, and activities tailored to traveler personas. |
| 10 | **WeatherAgent** | `backend/app/agents/weather_agent.py` | Fetches target-period forecasts, identifies precipitation or heat risks, and recommends itinerary adjustments. |
| 11 | **BudgetAgent** | `backend/app/agents/budget_agent.py` | Itemizes expenditures across travel, stay, dining, and activities; flags deficit risks with deterministic math. |
| 12 | **ItineraryAgent** | `backend/app/agents/itinerary_agent.py` | Builds a chronological day-by-day plan with travel buffers, opening hour awareness, and rest blocks. |
| 13 | **ValidationAgent** | `backend/app/agents/validation_agent.py` | Programmatically validates the complete plan against time collisions, route impossibilities, and budget limits. |
| 14 | **FinalPlannerAgent** | `backend/app/agents/final_planner.py` | Synthesizes an executive travel brief, packing tips, and the finalized structured JSON payload. |

---

## Technology Stack

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com) (Python 3.11+)
- **Agent Orchestration**: [LangGraph](https://github.com/langchain-ai/langgraph) & [LangChain](https://www.langchain.com)
- **Primary LLM Provider**: [Groq](https://groq.com) (`openai/gpt-oss-120b`, `llama-3.3-70b-versatile`)
- **Database & ORM**: PostgreSQL (Production) / SQLite (Local Dev) with [SQLAlchemy 2.0](https://www.sqlalchemy.org) (Async)
- **Migrations**: [Alembic](https://alembic.sqlalchemy.org)
- **Validation**: [Pydantic v2](https://docs.pydantic.dev)
- **Security**: Python-JOSE (JWT), Passlib (Bcrypt), Proxy-aware rate limiter
- **Logging**: Structlog (JSON structured logs in production)

### Frontend
- **Framework**: [Next.js 15](https://nextjs.org) (App Router, React 19)
- **Language**: [TypeScript](https://www.typescriptlang.org)
- **Styling**: [Tailwind CSS](https://tailwindcss.com) & [Lucide Icons](https://lucide.dev)
- **Real-Time Client**: HTML5 Server-Sent Events (`EventSource`)
- **State & Forms**: React Custom Hooks & Zod schema validation

---

## Mock Providers vs. Live Data

> **Transparency Note**: To ensure this project can be cloned and run by anyone without requiring expensive enterprise travel API keys (such as Amadeus, Sabre, IRCTC, or Skyscanner GDS contracts), the application includes realistic, pre-seeded **Mock Data Providers**.

- **Mock Providers**: Included for Indian travel routes (e.g. Hyderabad↔Goa, Delhi↔Mumbai, Bangalore↔Goa). They simulate realistic transport schedules, real hotel price distributions, and historical climate norms.
- **Source Labeling**: Every response item generated by a mock provider is tagged with `source_type: "mock"` in the JSON payload.
- **Extensibility**: All providers implement standard abstract base classes (`TransportProvider`, `AccommodationProvider`, `WeatherProvider`). Connecting live production APIs requires only implementing the base provider interface and setting the corresponding API keys in your `.env`.

---

## Getting Started

### Prerequisites
- **Python**: 3.11 or higher
- **Node.js**: 20.x or higher
- **Package Managers**: `pip` (Python) and `npm` (Node)
- **Groq API Key**: Obtain a free API key at [console.groq.com](https://console.groq.com)

---

### Environment Configuration

1. **Backend Environment**:
   ```bash
   cd backend
   cp .env.example .env
   ```
   Open `backend/.env` and insert your Groq API key:
   ```env
   LLM_PROVIDER=groq
   LLM_MODEL=openai/gpt-oss-120b
   LLM_BASE_URL=https://api.groq.com/openai/v1
   LLM_API_KEY=gsk_your_actual_groq_api_key_here
   ```

2. **Frontend Environment**:
   ```bash
   cd ../frontend
   cp .env.example .env.local
   ```
   Confirm `NEXT_PUBLIC_API_URL` points to `http://localhost:8000`.

---

### Local Setup (Windows / Linux / macOS)

#### 1. Backend Setup

```bash
# Navigate to backend
cd backend

# Create and activate a virtual environment
# On Windows (PowerShell):
python -m venv .venv
.venv\Scripts\activate

# On Linux / macOS:
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Run database migrations
alembic upgrade head

# Start the FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Backend will be live at `http://localhost:8000`. Interactive API documentation is available at `http://localhost:8000/docs`.

#### 2. Frontend Setup

In a new terminal window:
```bash
# Navigate to frontend
cd frontend

# Install packages
npm install

# Start Next.js development server
npm run dev
```
Open your browser to `http://localhost:3000`.

---

### Docker Compose Quickstart

If you prefer to run the entire stack with Docker:

```bash
# Start backend, frontend, and PostgreSQL services
docker compose up -d --build

# View logs
docker compose logs -f

# Stop services
docker compose down
```

---

## Testing

The backend includes a comprehensive suite of unit and integration tests verifying authentication, model validation, provider mocks, tools, security rate limits, and LangGraph workflows:

```bash
# Activate virtual environment
cd backend
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS / Linux

# Run test suite
python -m pytest tests/ -v
```

Frontend production build verification:
```bash
cd frontend
npm run build
```

---

## API Documentation

FastAPI automatically generates interactive OpenAPI/Swagger documentation.
Once the backend is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Primary Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/health` | Service health status, database ping, and environment mode |
| `POST` | `/api/v1/auth/register` | Create a new user account |
| `POST` | `/api/v1/auth/login` | Authenticate user and receive JWT access token |
| `POST` | `/api/v1/travel/plan` | Initialize a new multi-agent travel planning run |
| `POST` | `/api/v1/travel/clarify` | Submit user answers to clarification questions |
| `GET` | `/api/v1/travel/{id}` | Retrieve complete travel plan result and status |
| `GET` | `/api/v1/travel/{id}/events` | Connect to live Server-Sent Events (SSE) agent timeline |
| `GET` | `/api/v1/preferences` | Retrieve authenticated user travel preferences |
| `PUT` | `/api/v1/preferences` | Update authenticated user travel preferences |
| `GET` | `/api/v1/monitoring/health` | Detailed system metrics, token usage, and active semaphores |

---

## Production Deployment

This project is configured for cloud deployment:
- **Backend & Database**: Ready for [Render](https://render.com) using the included Infrastructure-as-Code Blueprint (`render.yaml`).
- **Frontend**: Ready for [Vercel](https://vercel.com).

For step-by-step production deployment instructions, refer to:
- [docs/step-by-step-deployment-guide.md](docs/step-by-step-deployment-guide.md)
- [docs/deployment.md](docs/deployment.md)

---

## Security & Cost Guardrails

- **Zero-Secret Guarantee**: No API keys, passwords, or credentials are tracked in Git.
- **JWT Authentication**: User identity is validated via cryptographic signatures.
- **In-Flight Plan Semaphores**: Limits concurrent long-running agent graphs to prevent server thread exhaustion (`MAX_CONCURRENT_PLANS_TOTAL`).
- **Budget Ceilings**: Strict spending caps (`DAILY_LLM_BUDGET_USD` and `MONTHLY_LLM_BUDGET_USD`) halt LLM requests if thresholds are breached, preventing surprise cloud bills.
- **Rate Limiting**: Defends endpoints against spam and denial-of-service attempts.

---

## Current Limitations & Roadmap

### Current Limitations
- External travel APIs (GDS/flight aggregators) are mocked by default for zero-cost demonstration.
- Real-time airline seat booking and transaction checkout are not supported.
- Pre-seeded routes focus primarily on major Indian travel corridors.

### Planned Enhancements
- [ ] Direct IRCTC / Skyscanner / Booking.com API adapter plugins.
- [ ] Interactive Map routing visualization with Mapbox.
- [ ] Export itinerary directly to Google Calendar and PDF.
- [ ] Multi-traveler collaborative planning sessions over WebSockets.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
