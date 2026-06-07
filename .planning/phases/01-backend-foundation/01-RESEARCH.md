# Phase 1: Backend Foundation - Research

**Researched:** 2026-06-07
**Domain:** FastAPI, sqlite3 (Python Standard Library), Pydantic v2
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Dynamically add columns to the SQLite `tasks` table on start:
  - `description` (TEXT, optional)
  - `priority` (TEXT, NOT NULL, default 'low', validated `CHECK(priority IN ('low', 'medium', 'high'))`)
  - `due_date` (TEXT, optional)
  - `deleted` (INTEGER, NOT NULL, default 0, validated `CHECK(deleted IN (0, 1))`)
- **D-02:** Database table creation/initialization automatically runs `PRAGMA table_info` and executes `ALTER TABLE` statements to add new columns to an existing database if they are missing.
- **D-03:** Missing descriptions are stored as `NULL` in the database, returning `None` / `null` in the API output.
- **D-04:** `GET /tasks` query parameter `deleted` (boolean, default False) determines if it returns active tasks (`deleted = 0`) or soft-deleted tasks (`deleted = 1`). Soft-deleted tasks are hidden by default.
- **D-05:** Task creation and updates allow past due dates (overdue/backdated tasks) to be saved, only enforcing the string format `YYYY-MM-DD`.
- **D-06:** Implement REST endpoints:
  - `PUT /tasks/{id}` (updates title, status, description, priority, due_date)
  - `DELETE /tasks/{id}` (soft-deletes task by setting `deleted = 1`)
  - `POST /tasks/{id}/restore` (restores task by setting `deleted = 0`)
  - `DELETE /tasks/{id}/permanent` (hard-deletes the task record from the database)

### the agent's Discretion
- The exact structure of custom error response details returned in the 422 validations can follow standard FastAPI/Pydantic validation details.

### Deferred Ideas (OUT OF SCOPE)
- None (all core requirements mapped to Phase 1 backend).
</user_constraints>

<architectural_responsibility_map>
## Architectural Responsibility Map

Single-tier application — all capabilities reside in API/Backend (FastAPI + SQLite).
</architectural_responsibility_map>

<research_summary>
## Summary

This phase focuses on upgrading the existing tracer bullet API to support full CRUD operations and a persistent database schema that dynamically migrates itself. The database uses python's standard library `sqlite3` module.

We researched:
1. Dynamic SQLite schema migrations via `PRAGMA table_info('tasks')` to identify missing columns at runtime and issue `ALTER TABLE` statements safely.
2. Pydantic validation rules, particularly string format validation for `due_date` (enforcing `YYYY-MM-DD` or allowing `None`) and checking that priority is one of `low`, `medium`, or `high`.
3. Soft-deletion and restoration patterns in SQL queries, ensuring query parameter filters return active/deleted tasks appropriately.

**Primary recommendation:** Initialize the database on startup by querying the existing table schema. Inspect the columns, run differential `ALTER TABLE tasks ADD COLUMN ...` statements, and use Pydantic field validators to ensure dates and priority options are clean before saving to SQLite.
</research_summary>

<standard_stack>
## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| fastapi | 0.115.x | REST API Framework | Python standard for high-performance async web APIs |
| pydantic | 2.10.x | Data validation and parsing | Built-in data modeling for FastAPI |
| sqlite3 | (std library) | Relational Database | Zero-dependency serverless local database |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| sqlite3 (std library) | SQLAlchemy / SQLModel | High overhead and code separation; standard `sqlite3` matches flat layout and is lightweight |
| sqlite3 migrations | Alembic | Too complex for a single flat file project; dynamic schema checks are simpler and zero-config |

</standard_stack>

<architecture_patterns>
## Architecture Patterns

### Dynamic SQLite Schema Checks
To implement dynamic auto-migrations on start without external libraries, we use:
```python
def migrate_db():
    # Cold-start case: Ensure tasks table exists first before running migrations
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                title      TEXT NOT NULL,
                status     TEXT NOT NULL DEFAULT 'todo'
                           CHECK(status IN ('todo', 'in_progress', 'done')),
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        conn.commit()

    columns_to_add = {
        "description": "TEXT",
        "priority": "TEXT NOT NULL DEFAULT 'low' CHECK(priority IN ('low', 'medium', 'high'))",
        "due_date": "TEXT",
        "deleted": "INTEGER NOT NULL DEFAULT 0 CHECK(deleted IN (0, 1))"
    }
    with sqlite3.connect(DB_PATH) as conn:
        # Check existing columns
        cursor = conn.execute("PRAGMA table_info(tasks)")
        existing_cols = {row[1] for row in cursor.fetchall()}
        
        for col_name, col_def in columns_to_add.items():
            if col_name not in existing_cols:
                conn.execute(f"ALTER TABLE tasks ADD COLUMN {col_name} {col_def}")
        conn.commit()
```

### Date Validation in Pydantic
We validate the date format string `YYYY-MM-DD` using a custom regex validator:
```python
import re
from typing import Literal
from pydantic import BaseModel, field_validator

DATE_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}$")

class TaskIn(BaseModel):
    title: str
    description: str | None = None
    priority: Literal["low", "medium", "high"] = "low"
    due_date: str | None = None
    status: Literal["todo", "in_progress", "done"] = "todo"

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v: str | None) -> str | None:
        if v is None:
            return None
        if not DATE_REGEX.match(v):
            raise ValueError("due_date must be in YYYY-MM-DD format")
        return v
```

### Anti-Patterns to Avoid
- **Hard-resetting the database file:** Deleting the SQLite db file to apply migrations deletes existing user data. Always use `ALTER TABLE`.
- **Formatting dates as datetimes in SQLite:** Store dates purely as `YYYY-MM-DD` strings for simple dictionary representation and filtering.
</architecture_patterns>

<dont_hand_roll>
## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| String Validation | Custom parsing and manual dictionary checks | Pydantic fields and models | Standardizes HTTP 422 error outputs and handles schema serialization automatically |
| Database Connections | Global open connection pools | Lifespan context manager and connection helper | Prevents database lock errors and file corruption on concurrency |

</dont_hand_roll>

<common_pitfalls>
## Common Pitfalls

### Pitfall 1: SQLite ALTER TABLE Constraints
**What goes wrong:** SQLite has limited support for modifying constraints on existing columns or adding multiple columns in a single query.
**Why it happens:** Standard SQL dialects support multi-alter; SQLite only allows one `ADD COLUMN` statement per execution.
**How to avoid:** Execute separate `ALTER TABLE tasks ADD COLUMN ...` statements for each new column in a loop.

### Pitfall 2: Python 3.11/3.12 syntax vs older syntax
**What goes wrong:** Mixing type annotations like `Union[str, None]` and `str | None` can lead to parser inconsistency.
**Why it happens:** Project requires Python 3.11+ syntax.
**How to avoid:** Consistently use pipe union syntax `str | None` as established in the tracer bullet.

### Pitfall 3: PUT Endpoint reset semantics vs Pydantic defaults
**What goes wrong:** If the client updates a task via `PUT /tasks/{id}` but omits the `status` field (which defaults to `"todo"` in `TaskIn`), the task status will be silently overwritten and reset to `"todo"`.
**Why it happens:** Pydantic assigns defaults for missing fields when parsing input payloads.
**How to avoid:** Ensure that PUT requests use a model where `status` is required (no default value), or distinguish between creation (`TaskIn` with default status) and full update models (`TaskUpdate` with no default status). In a pure PUT API, status should be a required field of `TaskIn` or `TaskUpdate` to represent the complete resource state.
</common_pitfalls>

<code_examples>
## Code Examples

### Querying with Soft-Delete Filter
```python
from typing import Literal

@app.get("/tasks")
def get_tasks(deleted: bool = False, status: Literal["todo", "in_progress", "done"] | None = None):
    # Note: SQLite stores 'deleted' as an INTEGER (0 or 1). FastAPI coerces query param 'deleted' 
    # from a boolean (True/False) to a Python bool, which we map to SQLite INTEGER 1 or 0.
    query = "SELECT * FROM tasks WHERE deleted = ?"
    params = [1 if deleted else 0]
    if status:
        query += " AND status = ?"
        params.append(status)
    query += " ORDER BY created_at ASC"
    # Execute query...
```
</code_examples>

<sota_updates>
## State of the Art (2025-2026)


- **Pydantic v2:** Pydantic v2 replaces `validator` with `field_validator` and is significantly faster due to its Rust core.
- **FastAPI Lifespan:** `@app.on_event("startup")` is deprecated. Use `asynccontextmanager` `lifespan` as already implemented.
</sota_updates>

<sources>
## Sources

### Primary (HIGH confidence)
- FastAPI official documentation (lifespan and dependency injection)
- Pydantic v2 field_validator guidelines
- SQLite3 documentation on dynamic `PRAGMA table_info` and `ALTER TABLE`
</sources>

<metadata>
## Metadata

**Research scope:**
- Core technology: FastAPI, Pydantic, sqlite3
- Patterns: sqlite3 migrations, Pydantic validations, soft-deletion

**Confidence breakdown:**
- Standard stack: HIGH
- Architecture: HIGH
- Pitfalls: HIGH

**Research date:** 2026-06-07
**Valid until:** 2026-07-07
</metadata>

---

*Phase: 1-Backend Foundation*
*Research completed: 2026-06-07*
*Ready for planning: yes*
