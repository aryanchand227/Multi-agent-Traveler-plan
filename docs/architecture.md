# System Architecture: Multi-Agent AI Travel Planner

This document provides a comprehensive architectural overview of the **Multi-Agent AI Travel Planner**, detailing the agent orchestration, workflow state, provider abstractions, persistence layer, and security boundaries.

---

## 1. High-Level Architecture

The platform follows a decoupled, cloud-ready architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                      Client Layer                           │
│  Next.js 15 (React 19, TypeScript, Tailwind CSS, Lucide)    │
│  - Interactive Plan Builder & Natural Language Intake       │
│  - Real-time Agent Execution Timeline (SSE)                 │
│  - Transport Comparison, Itinerary Views & Budget Breakdown │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTPS / SSE
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway & Backend                    │
│  FastAPI (Python 3.11+)                                     │
│  - JWT Bearer Authentication & IDOR Authorization           │
│  - Sliding-Window Rate Limiting & Proxy IP Resolution       │
│  - Daily / Monthly LLM Cost & Budget Guardrails             │
│  - Pydantic v2 Request / Response Validation                │
└──────────────────────────────┬──────────────────────────────┘
                               │
            ┌──────────────────┴──────────────────┐
            ▼                                     ▼
┌──────────────────────────────┐    ┌──────────────────────────────┐
│    LangGraph Orchestrator    │    │      Persistence Layer       │
│  - 14 Specialized AI Agents  │    │  PostgreSQL (Neon / Render)  │
│  - Typed TravelState Flow    │    │  SQLAlchemy 2.0 Async ORM    │
│  - Context Slicers & Reducers│    │  Alembic Migrations          │
└──────────────┬───────────────┘    └──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│                Provider Abstraction Layer                   │
│  - LLM: Groq (via LangChain ChatOpenAI / gpt-oss-120b)      │
│  - Transport: Flight, Train, Bus Providers (Mock + Extensible)
│  - Accommodation: Hotel & Resort Providers (Mock + Extensible)
│  - Destination: Activities & Attraction Providers           │
│  - Weather: Forecast & Advisory Providers                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Multi-Agent Orchestration via LangGraph

The core workflow engine is built using **LangGraph** (`backend/app/graph/workflow.py`). It coordinates 14 distinct specialized agents across sequential and parallel planning stages.

```
                  [User Natural Language Prompt]
                                │
                                ▼
                       ┌─────────────────┐
                       │   IntakeAgent   │
                       └────────┬────────┘
                                │
                                ▼
                      /───────────────────\
                     <  Needs Clarification? >
                      \───────────────────/
                        │               │
                     Yes│               │No
                        ▼               ▼
            ┌──────────────────┐  ┌──────────────────┐
            │ClarificationAgent│  │  TravelManager   │
            └──────────────────┘  └────────┬─────────┘
                                           │
         ┌─────────────────────────────────┼─────────────────────────────────┐
         ▼                                 ▼                                 ▼
┌──────────────────┐             ┌──────────────────┐             ┌──────────────────┐
│TransportSupervis.│             │AccommodationAgent│             │ DestinationAgent │
└────────┬─────────┘             └────────┬─────────┘             └────────┬─────────┘
         │                                │                                │
    ┌────┼────┐                           │                                │
    ▼    ▼    ▼                           │                                │
  [Bus][Train][Flight]                    │                                │
    │    │    │                           │                                │
    └────┼────┘                           │                                │
         │                                │                                │
         └────────────────────────────────┼────────────────────────────────┘
                                          │
                                          ▼
                                ┌──────────────────┐
                                │   WeatherAgent   │
                                └────────┬─────────┘
                                          │
                                          ▼
                                ┌──────────────────┐
                                │   BudgetAgent    │
                                └────────┬─────────┘
                                          │
                                          ▼
                                ┌──────────────────┐
                                │  ItineraryAgent  │
                                └────────┬─────────┘
                                          │
                                          ▼
                                ┌──────────────────┐
                                │ ValidationAgent  │
                                └────────┬─────────┘
                                          │
                                          ▼
                                ┌──────────────────┐
                                │FinalPlannerAgent │
                                └────────┬─────────┘
                                          │
                                          ▼
                             [Final Validated Itinerary]
```

### The 14 Specialized Agents

| # | Agent Name | Source File | Core Responsibility |
|---|---|---|---|
| 1 | **IntakeAgent** | `app/agents/intake.py` | Extracts origin, destination, dates, budget, travelers, and interests from natural-language text into structured entities. |
| 2 | **ClarificationAgent** | `app/agents/clarification.py` | Identifies missing or conflicting constraints (e.g. unknown dates or unspecified budget) and produces targeted questions. |
| 3 | **TravelManager** | `app/agents/manager.py` | Central coordinator evaluating prerequisites, determining route feasibility, and provisioning downstream agent tasks. |
| 4 | **TransportSupervisor** | `app/agents/transport_supervisor.py` | Spawns transport sub-agents, aggregates transport options, normalizes durations, and scores options based on user priorities. |
| 5 | **BusAgent** | `app/agents/bus_agent.py` | Queries bus providers for intercity bus routes, sleeper/seater categories, operators, and pricing. |
| 6 | **TrainAgent** | `app/agents/train_agent.py` | Evaluates railway itineraries, train classes (e.g., 1A, 2A, 3A, SL), timetables, and availability. |
| 7 | **FlightAgent** | `app/agents/flight_agent.py` | Queries airlines for direct and connecting flights, baggage policies, departure windows, and fare tiers. |
| 8 | **AccommodationAgent** | `app/agents/accommodation_agent.py` | Selects verified hotels, hostels, and resorts matching user tier, proximity to center, ratings, and amenity preferences. |
| 9 | **DestinationAgent** | `app/agents/destination_agent.py` | Recommends curated attractions, cultural sites, and adventure activities tailored to traveler personas. |
| 10 | **WeatherAgent** | `app/agents/weather_agent.py` | Evaluates weather forecasts for target dates and suggests schedule adjustments or packing advice. |
| 11 | **BudgetAgent** | `app/agents/budget_agent.py` | Computes itemized financial breakdowns across travel, lodging, food, and activities; flags deficit risks. |
| 12 | **ItineraryAgent** | `app/agents/itinerary_agent.py` | Assembles a coherent, realistic day-by-day itinerary with logical sequencing, opening hours, and meal gaps. |
| 13 | **ValidationAgent** | `app/agents/validation_agent.py` | Rigorously audits the schedule: checks for time overlaps, impossible transfers, and budget overruns. |
| 14 | **FinalPlannerAgent** | `app/agents/final_planner.py` | Synthesizes a structured JSON plan along with a formatted, executive trip brief ready for the traveler. |

---

## 3. Workflow State & Context Builders

### State Management (`app/graph/state.py`)
All nodes in the LangGraph graph read and write to a strongly-typed `TravelState` dictionary:
- `request_id`, `user_id`, `status`
- `origin`, `destination`, `start_date`, `end_date`, `duration_days`
- `budget_limit`, `travelers_count`, `travel_style`, `interests`
- `transport_options`, `accommodation_options`, `activities`, `weather_forecast`
- `daily_itineraries`, `budget_breakdown`, `validation_errors`, `final_plan`

### Context Builders (`app/agents/context_builders.py`)
To prevent token bloat and reduce Groq LLM latency, each agent receives a tailored slice of the state rather than the full global state:
- `build_transport_context(state)`
- `build_accommodation_context(state)`
- `build_destination_context(state)`
- `build_budget_context(state)`
- `build_itinerary_context(state)`
- `build_validation_context(state)`

---

## 4. LLM & Data Provider Abstraction

### LLM Factory (`app/providers/llm/factory.py`)
The system abstracts LLM providers via LangChain interfaces:
- **Default**: Groq API via `langchain_openai.ChatOpenAI` configured with:
  - Base URL: `https://api.groq.com/openai/v1`
  - Model: `openai/gpt-oss-120b` or `llama-3.3-70b-versatile`
  - Low temperature (0.3) for consistent structured outputs
- **Fallback**: Compatible with standard OpenAI or Google Gemini.

### Mock Travel Providers
To allow complete local and demo deployments without paid travel APIs (GDS, Amadeus, Skyscanner, IRCTC), the system includes high-fidelity mock providers (`app/providers/`):
- `MockTransportProvider`: Pre-seeded schedules and pricing for high-traffic routes (Hyderabad↔Goa, Delhi↔Mumbai, Bangalore↔Goa).
- `MockAccommodationProvider`: Curated hotel, boutique, and resort listings with real-world amenities.
- `MockWeatherProvider`: Climate-accurate seasonal forecasts for popular destinations.

All mock data is explicitly tagged with `source_type: "mock"` to ensure full transparency.

---

## 5. Security & Production Safeguards

1. **Authentication & Identity**:
   - Secure passlib password hashing (PBKDF2/Bcrypt).
   - Cryptographically signed JWT bearer tokens (`HS256`).
   - IDOR prevention: All user queries, plans, and SSE streams enforce `run.user_id == current_user.id`.

2. **Proxy-Aware Rate Limiting**:
   - Sliding-window rate limiting on login, registration, and plan generation.
   - Dynamic client IP extraction respecting `X-Forwarded-For` when behind trusted reverse proxies (Render, Cloudflare).

3. **LLM Cost & Budget Guardrails**:
   - Application-level spending caps: `DAILY_LLM_BUDGET_USD` and `MONTHLY_LLM_BUDGET_USD`.
   - Max concurrent plan generation semaphore (`MAX_CONCURRENT_PLANS_TOTAL`).
   - Plan-level token budgeting with strict per-run execution caps.

---

## 6. Real-Time Streaming (SSE)

Real-time agent execution events are dispatched via Server-Sent Events (`/api/v1/travel/{request_id}/events`):
- Each agent emits `AgentEvent` payloads (`agent_started`, `agent_completed`, `agent_error`).
- The Next.js frontend connects via `EventSource` (`usePlanningEvents.ts`) and renders real-time status indicators in the user dashboard.
