---
name: decisions
description: Key architectural and technical decisions with reasoning. Load when making design choices or understanding why something is built a certain way.
triggers:
  - "why do we"
  - "why is it"
  - "decision"
  - "alternative"
  - "we chose"
edges:
  - target: context/architecture.md
    condition: when a decision relates to system structure (layered architecture, soft-delete pattern)
  - target: context/stack.md
    condition: when a decision relates to technology choice (FastAPI, SQLite, vanilla JS)
last_updated: 2026-06-06
---

# Decisions

## Decision Log

### FastAPI over Flask or Django
**Date:** 2026-06-06
**Status:** Active
**Decision:** Use FastAPI as the web framework for the REST backend.
**Reasoning:** FastAPI provides automatic OpenAPI/Swagger docs at `/docs` with zero configuration, native Pydantic v2 integration for request/response validation, and async support. Flask would require manual validation wiring; Django is too heavy for a single-user local tool.
**Alternatives considered:** Flask (rejected — no built-in validation or docs generation), Django REST Framework (rejected — excessive boilerplate and ORM coupling for this scale).
**Consequences:** All route handler inputs are automatically validated by Pydantic. OpenAPI docs are available at `/docs` during development. Async route handlers are available if needed.

---

### SQLite over PostgreSQL or other databases
**Date:** 2026-06-06
**Status:** Active
**Decision:** Use SQLite as the sole data store, persisted to a local file (`./taskkeeper.db`).
**Reasoning:** Single user, local-only use means there are no concurrency requirements that would justify an external database server. SQLite requires zero infrastructure setup and the database file is created automatically on first run.
**Alternatives considered:** PostgreSQL (rejected — requires running a separate server process), MySQL (rejected — same reason).
**Consequences:** No Alembic migrations needed — `Base.metadata.create_all()` handles schema on startup. Not suitable if the project ever needs multi-user or remote access (but that's explicitly out of scope).

---

### Vanilla HTML/JS over a JS framework
**Date:** 2026-06-06
**Status:** Active
**Decision:** Build the frontend as plain HTML/JS with no framework and no build toolchain.
**Reasoning:** The frontend is a single-page Kanban board with no complex state management needs. A framework would require npm, a bundler, and a separate dev server. Vanilla JS keeps the frontend as a single file the browser can serve directly via FastAPI's `StaticFiles`.
**Alternatives considered:** React (rejected — requires build toolchain, excessive for this scope), Vue (rejected — same reason).
**Consequences:** No TypeScript, no bundler, no `node_modules`. All JS must be compatible with modern browsers without transpilation. State is held in memory as a JS object rebuilt from API responses on each action.
