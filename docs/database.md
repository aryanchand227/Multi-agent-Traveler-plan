# Database & Persistence Architecture

The Multi-Agent AI Travel Planner uses an asynchronous SQLAlchemy ORM layer supporting **SQLite** for local development and **managed PostgreSQL** for production.

---

## 1. Production Connection Pooling

Configured in `backend/app/db/session.py`:

```python
kwargs.update({
    "pool_size": 20,         # Maximum persistent connections
    "max_overflow": 10,      # Additional temporary connections under spike load
    "pool_pre_ping": True,   # Health-checks connections before use (prevents closed connection drops)
    "pool_recycle": 3600,    # Recreates connections hourly
})
```

---

## 2. Database Schema & Entities

| Table | Purpose | Key Constraints |
|---|---|---|
| `users` | User accounts & credentials | `email` unique index, `hashed_password`, `is_active` |
| `user_preferences` | User travel styles, transport & currency | `user_id` unique foreign key to `users.id` |
| `travel_requests` | Trip input parameters & constraints | `user_id` foreign key, indexed |
| `travel_runs` | LangGraph workflow execution status & final plan | `request_id` foreign key, indexed |
| `llm_usage_records` | Token counts, duration, and estimated cost | `user_id`, `request_id`, `agent_name` indexed |
| `agent_events` | Historical agent lifecycle events | `request_id` indexed |

---

## 3. Alembic Migrations

Migrations are stored in `backend/migrations/versions/`.

### Initial Migration
- Revision: `134b62b01968_initial_schema.py`
- Created: October 15, 2026
- Generates `llm_usage_records` and adds `hashed_password` and `is_active` to `users`.

### Migration Commands
Run from the `backend/` directory:

```powershell
# Apply all pending migrations to database
.venv\Scripts\python.exe -m alembic upgrade head

# Create a new migration after editing ORM models
.venv\Scripts\python.exe -m alembic revision --autogenerate -m "describe_changes"

# Rollback one migration
.venv\Scripts\python.exe -m alembic downgrade -1
```

*Note: In the Render deployment blueprint, `alembic upgrade head` executes automatically during the build command.*

---

## 4. Backup & Disaster Recovery (Render Managed PostgreSQL)

### Automatic Daily Backups
Render managed PostgreSQL automatically takes daily backups and retains them based on your plan (7 days on Starter).

### Manual Backup via `pg_dump`
```bash
# Export production database backup
pg_dump "postgresql://travel_user:SECRET@dpg-xxx.oregon-postgres.render.com/travel_planner" -F c -b -v -f travel_planner_backup.dump
```

### Restore from Backup
```bash
# Restore to database
pg_restore -d "postgresql://travel_user:SECRET@dpg-xxx.oregon-postgres.render.com/travel_planner" -v travel_planner_backup.dump
```
