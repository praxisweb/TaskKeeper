# PRD: TaskKeeper v0.1 — Tracer Bullet (Create & View Tasks)

> **Labels:** `ready-for-agent`
> **Publish to:** https://github.com/praxisweb/TaskKeeper/issues/new

---

## Problem Statement

As a developer running TaskKeeper locally, I have no way to create or view tasks. The project is fully scaffolded with a defined tech stack and requirements, but zero application code exists. There is no running server, no database, and no UI — nothing that actually manages tasks.

The core friction: a personal task tracker that doesn't yet track tasks.

## Solution

Build a single working vertical slice — one feature, full stack — that connects the browser to SQLite through a FastAPI API. The user can type a task name into a form, submit it, and see it appear on a three-column Kanban board. The task survives a page refresh (it's in the database). This slice validates the entire stack in the simplest possible way before adding more features.

## User Stories

1. As a developer, I want to open a browser and see a Kanban board with three columns (To Do, In Progress, Done), so that I have a visual overview of my task state.
2. As a developer, I want to see a "No tasks" placeholder in each empty column, so that the board communicates state clearly rather than showing a blank white box.
3. As a developer, I want to type a task name into a form and click "Add Task", so that I can create a new task without leaving the board.
4. As a developer, I want a newly created task to immediately appear in the "To Do" column, so that I get instant feedback that my task was saved.
5. As a developer, I want tasks to appear in the order I created them (oldest first), so that the board feels like a queue I work through top-to-bottom.
6. As a developer, I want my tasks to survive a page refresh, so that I know my data is actually persisted and not just held in memory.
7. As a developer, I want the server to reject a blank or whitespace-only task title, so that I can't accidentally create empty task cards.
8. As a developer, I want to see a specific, readable error message when my input is rejected (e.g., "title cannot be blank"), so that I understand what went wrong without inspecting network traffic.
9. As a developer, I want task titles containing special characters like `&`, `<`, and `>` to display correctly as text on the board, so that no title corrupts the UI.
10. As a developer, I want the app to show an error message if the server is unreachable (rather than a blank board), so that I know the server is down rather than thinking I have no tasks.
11. As a developer, I want to access interactive API documentation at `/docs`, so that I can explore and test the API without writing `curl` commands.
12. As a developer, I want to start the server with a single command (`uvicorn main:app --reload`), so that there's no build step or complex setup required.
13. As a developer, I want the database file to be created automatically on first run, so that I don't need to run migrations or schema setup scripts manually.
14. As a developer, I want the database file to live next to `main.py` regardless of which directory I invoke `uvicorn` from, so that I always write to the same database.
15. As a developer, I want the API to validate the `status` field and reject invalid values, so that the database never contains tasks in an undefined state.

## Implementation Decisions

### Project Structure
- Flat layout: `main.py`, `index.html`, `requirements.txt`, `tests/` — no `src/` package until there is a concrete reason to add one.

### Database
- SQLite, single file, lives next to `main.py` — always co-located, configurable via `DB_PATH` environment variable for tests.
- Schema initialised on server startup using `CREATE TABLE IF NOT EXISTS` — no migration tool.
- `status` column is `TEXT` with a `CHECK(status IN ('todo', 'in_progress', 'done'))` constraint — human-readable in the DB file and enforced at the DB layer in addition to the API layer.
- `created_at` stored as `TEXT` using SQLite's `datetime('now')` — UTC, sufficient for ordering.
- Tasks ordered `ASC` by `created_at` (oldest first) — queue semantics, new tasks arrive at the bottom.

### API
- `POST /tasks` — accepts `{title, status?}`, returns 201 + task object. A field validator rejects empty/blank titles with a 422 before the DB is touched.
- `GET /tasks` — returns all tasks; optional `?status=` query param filters by status. Invalid status values return 422.
- FastAPI lifespan context manager handles DB init — no deprecated `on_event` approach.
- Python 3.11+ syntax throughout: `X | None` instead of `Optional[X]`, `list[T]` instead of `List[T]`.

### Frontend
- Single `index.html` served from `GET /`. Path resolved relative to the server file — works from any working directory.
- No framework, no build step. On load: fetch all tasks, render into three column divs.
- API calls use relative URLs — no hardcoded port.
- An `escapeHtml()` helper used for all user-generated content rendered into the DOM — prevents `&` rendering as broken entities and blocks XSS.
- 422 responses parsed and shown in the UI with the specific validation message, not swallowed as a generic error code.
- Network/server errors caught and shown in a visible error element — board never goes silently blank.

### Testing
- Test isolation: shared SQLite file in the system temp directory (not `:memory:` — a new in-memory DB is created per connection, so POST and GET would see different databases). Rows deleted between tests via `DELETE FROM tasks` in an autouse fixture teardown.
- `DB_PATH` env var set in `conftest.py` before any import of `main` — module-load-time resolution requires this ordering.
- Dependencies: `>=` pinned — personal local tool, not a published library.

## Testing Decisions

**What makes a good test here:** test through the HTTP API (FastAPI `TestClient`), not through the DB init or connection helpers directly. The DB layer is thin SQL — the interesting behavior is the API contract (status codes, response shapes, validation errors). Don't test implementation details like which SQL query ran.

**Coverage:**
- `POST /tasks` — happy path (201 + correct fields), custom status, missing title (422), empty title (422), whitespace-only title (422), invalid status (422)
- `GET /tasks` — empty DB returns `[]`, created task appears in response, ordering is ASC (explicit test), status filter returns only matching tasks, invalid status query param returns 422
- `GET /` — route exists and returns 200
- `GET /health` — smoke test that the app starts and responds

**Prior art:** No existing tests in the codebase (greenfield). These are the foundation tests.

**Test runner:** `pytest tests/ -v`

## Out of Scope

- Moving tasks between columns (no `PATCH /tasks/{id}` in this slice)
- Editing any field of an existing task
- Soft-delete and trash view
- Priority, due date, description fields (schema columns deferred to Phase 2)
- Drag-and-drop reordering
- Any authentication or multi-user support (permanently out of scope for this project)
- Pagination
- Mobile-optimised layout
- Tags or labels

## Further Notes

- This slice is explicitly a tracer bullet — the goal is a working end-to-end loop in the minimum code possible. Subsequent phases will extend the schema and add endpoints without changing the architecture.
- The flat file structure and absence of a migration tool are intentional decisions, not shortcuts. They will be revisited when the schema has more than one revision or the file count exceeds ~5 Python modules.
- `tasks.db` and `*.db` are in `.gitignore` — the live database should never be committed (personal data) and is not needed for reproducible builds.
- **Implementation plan:** `docs/plans/2026-06-06-tracer-bullet-plan.md` (rev 4) contains the full TDD step-by-step plan to implement this PRD.
