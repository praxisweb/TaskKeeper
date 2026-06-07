# Phase 1: Backend Foundation - Context

**Gathered:** 2026-06-06
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase delivers a complete REST API backend utilizing FastAPI and SQLite on disk, supporting task CRUD operations (including soft-delete, restore, and permanent deletion), dynamic schema updates for backward compatibility, and thorough validation.

</domain>

<decisions>
## Implementation Decisions

### SQLite Database Schema Expansion
- **D-01:** Dynamically add columns to the SQLite `tasks` table on start:
  - `description` (TEXT, optional)
  - `priority` (TEXT, NOT NULL, default 'low', validated `CHECK(priority IN ('low', 'medium', 'high'))`)
  - `due_date` (TEXT, optional)
  - `deleted` (INTEGER, NOT NULL, default 0, validated `CHECK(deleted IN (0, 1))`)
- **D-02:** Database table creation/initialization automatically runs `PRAGMA table_info` and executes `ALTER TABLE` statements to add new columns to an existing database if they are missing.
- **D-03:** Missing descriptions are stored as `NULL` in the database, returning `None` / `null` in the API output.

### API Validation & Endpoints
- **D-04:** `GET /tasks` query parameter `deleted` (boolean, default False) determines if it returns active tasks (`deleted = 0`) or soft-deleted tasks (`deleted = 1`). Soft-deleted tasks are hidden by default.
- **D-05:** Task creation and updates allow past due dates (overdue/backdated tasks) to be saved, only enforcing the string format `YYYY-MM-DD`.
- **D-06:** Implement REST endpoints:
  - `PUT /tasks/{id}` (updates title, status, description, priority, due_date)
  - `DELETE /tasks/{id}` (soft-deletes task by setting `deleted = 1`)
  - `POST /tasks/{id}/restore` (restores task by setting `deleted = 0`)
  - `DELETE /tasks/{id}/permanent` (hard-deletes the task record from the database)

### the agent's Discretion
- The exact structure of custom error response details returned in the 422 validations can follow standard FastAPI/Pydantic validation details.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Specifications & Roadmaps
- [.planning/ROADMAP.md](file:///.planning/ROADMAP.md) — Defines the milestones, phases, and success criteria for Milestone 1.
- [.planning/REQUIREMENTS.md](file:///.planning/REQUIREMENTS.md) — Lists core task tracking requirements (TASK-01 through TASK-08 and API-01 through API-04).
- [.planning/PROJECT.md](file:///.planning/PROJECT.md) — Outlines the high-level architecture stack, value proposition, and boundaries.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `get_db()` generator context manager in `main.py` handles SQLite connection creation, mapping row factories to `sqlite3.Row` for dictionary conversions.
- `lifespan` context manager handles server-startup database initialization hooks.

### Established Patterns
- Python 3.11+ type syntax is used throughout (e.g. `VALID_STATUSES | None` instead of `Optional[VALID_STATUSES]`).
- Clean separation of Pydantic models for incoming data validation (`TaskIn`) and output representation (`TaskOut`).

### Integration Points
- Database file `tasks.db` sits in the workspace root alongside `main.py`, resolved dynamically relative to `__file__`.

</code_context>

<specifics>
## Specific Ideas

No additional specific requirements — open to standard approaches.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 1-Backend Foundation*
*Context gathered: 2026-06-06*
