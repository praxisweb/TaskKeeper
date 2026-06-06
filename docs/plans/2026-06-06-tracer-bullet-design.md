# TaskKeeper v0.1 — Tracer Bullet Design

**Date:** 2026-06-06
**Status:** Approved
**Strategy:** Vertical tracer bullet — one feature, full stack, end-to-end

---

## Goal

Get a running app where you can type a task name, hit submit, and see it appear on a real Kanban board — backed by a real SQLite database. No mocks, no stubs.

Estimated build time: ~30 minutes.

---

## Scope

### In

- SQLite DB with a single `tasks` table
- FastAPI: `POST /tasks` and `GET /tasks`
- HTML/JS: create form + three Kanban columns rendering live data from the API
- Tasks default to `todo` status

### Out (Phase 2+)

- Priority, due date, description
- Edit / delete
- Move tasks between columns
- Soft-delete and trash view
- Full requirements from PROJECT.md

---

## Architecture

Three files to start — flat until there's a reason to split:

```
main.py       # FastAPI app, DB init, Pydantic models, routes
tasks.db      # SQLite file, auto-created on first run
index.html    # Single-page Kanban UI
```

When the API grows past ~5 endpoints, extract to `models.py` and `routes/`.

---

## Data Model

```sql
CREATE TABLE IF NOT EXISTS tasks (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  title      TEXT NOT NULL,
  status     TEXT NOT NULL DEFAULT 'todo',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
```

- `status` allowed values: `'todo'` | `'in_progress'` | `'done'`
- No migration tool — `main.py` runs `CREATE TABLE IF NOT EXISTS` on startup
- Pydantic validates `status` at the API layer; SQLite stores plain strings

---

## API

```
POST /tasks
  Body:    { "title": string, "status"?: "todo"|"in_progress"|"done" }
  Returns: 201 + task object { id, title, status, created_at }
  Errors:  422 if title missing or status invalid

GET /tasks
  Query:   ?status=todo  (optional filter)
  Returns: 200 + list of task objects
```

FastAPI auto-generates `/docs` (Swagger UI) — use it to smoke-test before wiring the frontend.

---

## Frontend

Single `index.html` file. No framework, no build step.

**On load:**
1. `GET /tasks` — fetch all tasks
2. Split results by `status` into three arrays
3. Render each array into its column (`To Do`, `In Progress`, `Done`)

**On form submit:**
1. `POST /tasks` with the title from the input field
2. Re-fetch all tasks and re-render

No optimistic updates. Simple and correct.

---

## Build Order

1. **`main.py`** — DB init + Pydantic models + two endpoints
   - Verify with `curl` or FastAPI `/docs`
2. **`index.html`** — static HTML layout (three columns, form) first
   - Then wire `fetch()` calls to the live API

---

## Run

```bash
pip install fastapi uvicorn
uvicorn main:app --reload
# Open http://localhost:8000
# API docs at http://localhost:8000/docs
```

---

## What This Validates

- The full stack works together (DB → API → UI)
- The data model is correct before adding more columns
- The FastAPI + SQLite setup is sound
- The `index.html` approach is viable for the UI

Once this slice ships, Phase 2 adds: priority, due date, description, move between columns, soft-delete, and trash.
