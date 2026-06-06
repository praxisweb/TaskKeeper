---
name: stack
description: Technology stack, library choices, and the reasoning behind them. Load when working with specific technologies or making decisions about libraries and tools.
triggers:
  - "library"
  - "package"
  - "dependency"
  - "which tool"
  - "technology"
edges:
  - target: context/decisions.md
    condition: when the reasoning behind a tech choice is needed (why FastAPI over Flask, why SQLite over Postgres)
  - target: context/conventions.md
    condition: when understanding how to use a technology in this codebase (e.g. how SQLAlchemy sessions are managed)
  - target: context/architecture.md
    condition: when understanding how stack components fit together in the system
last_updated: 2026-06-06
---

# Stack

## Core Technologies

- **Python 3.11+** — primary language
- **FastAPI** — web framework; async route handlers, automatic OpenAPI docs at `/docs`
- **SQLite** — database; single file at `./taskkeeper.db`, no external server needed
- **SQLAlchemy 2.x** — ORM for all database access; declarative models
- **Pydantic v2** — request/response validation (integrated into FastAPI)
- **Uvicorn** — ASGI server; `uvicorn main:app --reload` for local dev

## Key Libraries

- **SQLAlchemy** (not raw sqlite3) — all DB access through the ORM; no raw SQL in route handlers
- **Pydantic v2** (not marshmallow, not dataclasses alone) — all request bodies and response models
- **pytest** (not unittest) — all tests use pytest style with `httpx.AsyncClient` for API testing
- **ruff** (not flake8/black separately) — linter and formatter in one tool
- **httpx** — async HTTP client used in tests via FastAPI's `TestClient`

## What We Deliberately Do NOT Use

- No PostgreSQL, MySQL, or any external database — SQLite only; no connection string management
- No SQLModel — use SQLAlchemy + Pydantic separately for clear layer boundaries
- No React, Vue, or any JS framework — vanilla HTML/JS only; no build toolchain
- No Alembic migrations — `Base.metadata.create_all()` handles schema on startup (acceptable for single-user local app)
- No Redis, Celery, or background workers — all operations are synchronous
- No authentication libraries (JWT, OAuth, etc.) — explicitly out of scope

## Version Constraints

- SQLAlchemy 2.x (not 1.x) — use the 2.0-style `Session.execute()` API, not legacy `Query`
- Pydantic v2 (not v1) — use `model_validate`, `model_dump`; not `.dict()` or `.from_orm()`
