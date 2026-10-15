# Database & Persistence Architecture

The Multi-Agent AI Travel Planner uses an asynchronous SQLAlchemy 2.0 ORM layer supporting **SQLite** for local development and **managed PostgreSQL (Supabase Free Tier)** for production.

---

## 1. Supported Databases & URL Normalization

The backend automatically detects and normalizes connection strings in `backend/app/db/url.py`:

| Environment | Supported URL Formats | Normalized Async Scheme | SSL / Pooler Handling |
|---|---|---|---|
| **Development** | `sqlite+aiosqlite:///./travel_planner.db`<br>`sqlite:///:memory:` | Preserved as-is | `check_same_thread: False` |
| **Supabase Direct** | `postgresql://...:5432/postgres`<br>`postgres://...:5432/postgres` | `postgresql+asyncpg://...` | `ssl: "require"` |
| **Supabase Pooler** | `postgresql://...:6543/postgres`<br>`postgresql://...pooler.supabase.com:6543/postgres` | `postgresql+asyncpg://...` | `ssl: "require"`, `statement_cache_size: 0` |

### Supabase Connection Notes:
- Standard `postgresql://` and `postgres://` URLs copied from the Supabase dashboard are automatically converted to `postgresql+asyncpg://`.
- If `?sslmode=require` is present in the connection string, it is stripped from the URL and passed properly via `connect_args={"ssl": "require"}` to prevent asyncpg errors.
- When connecting via the PgBouncer transaction pooler (port `6543`), the prepared statement cache is automatically disabled (`statement_cache_size: 0`) to prevent transaction pooler conflicts.

---

## 2. Production Connection Pooling

Configured in `backend/app/db/url.py` and `backend/app/db/session.py`:

```python
engine_kwargs.update({
    "pool_size": 20,         # Maximum persistent connections
    "max_overflow": 10,      # Additional temporary connections under spike load
    "pool_pre_ping": True,   # Health-checks connections before use (prevents closed drops)
    "pool_recycle": 3600,    # Recreates connections hourly
})
```

---

## 3. Database Schema & Entities (All 13 Core Tables)

| # | Table | Purpose | Key Constraints & Indexes |
|---|---|---|---|
| 1 | `users` | User accounts & credentials | `id` (PK, UUID), `email` (unique index), `hashed_password`, `is_active` |
| 2 | `user_preferences` | User travel styles, transport & currency | `user_id` (unique FK to `users.id`, indexed) |
| 3 | `travel_requests` | Trip input parameters & constraints | `id` (PK), `user_id` (FK to `users.id`, indexed) |
| 4 | `travel_runs` | LangGraph workflow execution status & final plan | `id` (PK, UUID), `request_id` (FK to `travel_requests.id`, indexed) |
| 5 | `transport_options` | Scored bus, train, flight alternatives | `id` (PK, UUID), `run_id` (FK to `travel_runs.id`, indexed) |
| 6 | `accommodation_options` | Curated hotels, resorts, hostels | `id` (PK, UUID), `run_id` (FK to `travel_runs.id`, indexed) |
| 7 | `activities` | Points of interest, tours, activities | `id` (PK, UUID), `run_id` (FK to `travel_runs.id`, indexed) |
| 8 | `itineraries` | High-level trip summary & day count | `id` (PK, UUID), `run_id` (FK to `travel_runs.id`, unique index) |
| 9 | `itinerary_days` | Daily schedule themes and dates | `id` (PK, UUID), `itinerary_id` (FK to `itineraries.id`, indexed) |
| 10 | `itinerary_items` | Individual timed stops and activities | `id` (PK, UUID), `day_id` (FK to `itinerary_days.id`, indexed) |
| 11 | `memory_entries` | Long-term user preferences & constraints | `id` (PK, UUID), `user_id` (indexed), `key` (indexed) |
| 12 | `agent_events` | Real-time SSE agent execution timeline | `id` (PK, UUID), `run_id` (FK to `travel_runs.id`, indexed) |
| 13 | `llm_usage_records` | Token counts, duration, and estimated cost | `id` (PK, UUID), `user_id` (FK to `users.id`), `request_id` (indexed) |

---

## 4. Alembic Migrations

Migrations are stored in `backend/migrations/versions/`.

- **Revision**: `134b62b01968_initial_schema.py`
- **Behavior**:
  - On a fresh database (Supabase PostgreSQL): Creates all 13 core tables with primary keys, foreign keys, and indexes in correct dependency order.
  - On existing databases (local SQLite): Preserves existing tables without data loss and adds missing columns/tables idempotently.
- **Async Execution**: `backend/migrations/env.py` uses `normalize_database_url` and `get_async_db_config` so migration commands work against both SQLite and Supabase PostgreSQL.

### Migration Commands
Run from the `backend/` directory:

```bash
# Apply migrations to database
alembic upgrade head

# Check current revision
alembic current

# Rollback one migration
alembic downgrade -1
```

---

## 5. Production SQLite Protection

In `production` (`APP_ENV=production`), the backend strictly enforces PostgreSQL:
- If `DATABASE_URL` is set to SQLite, `backend/app/main.py` aborts startup with a `RuntimeError`.
- This prevents silent data loss on ephemeral container platforms (such as Render) where SQLite files are wiped on restart.
