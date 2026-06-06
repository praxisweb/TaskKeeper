---
name: architecture
description: How the major pieces of this project connect and flow. Load when working on system design, integrations, or understanding how components interact.
triggers:
  - "architecture"
  - "system design"
  - "how does X connect to Y"
  - "integration"
  - "flow"
edges:
  - target: context/stack.md
    condition: when specific technology details about FastAPI, SQLAlchemy, or SQLite are needed
  - target: context/decisions.md
    condition: when understanding why the architecture is structured this way (no auth, soft-delete pattern, SPA choice)
  - target: context/conventions.md
    condition: when writing new routes or components and need to know how pieces are organized
last_updated: 2026-06-06
---

# Architecture

## System Overview

HTTP request from browser → FastAPI router (route handler) → service/repository layer → SQLAlchemy ORM → SQLite file on disk. Response flows back up the same chain as a Pydantic-validated JSON response.

The frontend is a single static HTML file served by FastAPI's `StaticFiles` mount (or opened directly from disk). It calls the REST API via `fetch` and re-renders the Kanban board from the API response. There are no WebSockets, no SSE, no page reloads.

All state lives in SQLite. The frontend is stateless between page loads.

## Key Components

- **FastAPI app (`main.py`)** — entry point, mounts routers and static file serving
- **Task router (`routers/tasks.py`)** — all `/tasks` endpoints; delegates to TaskService
- **TaskService (`services/task_service.py`)** — business logic: soft-delete rules, restore logic, status transitions
- **TaskRepository (`repositories/task_repository.py`)** — all SQLAlchemy queries; the only layer that touches the DB
- **Task model (`models/task.py`)** — SQLAlchemy ORM model; defines the schema
- **Pydantic schemas (`schemas/task.py`)** — request/response validation and serialization
- **Frontend (`frontend/index.html`)** — single-page Kanban board; all JS is inline or in a companion `app.js`

## External Dependencies

- **SQLite** — primary (and only) data store; file at `./taskkeeper.db`; created automatically on first run
- **Uvicorn** — ASGI server; started with `uvicorn main:app --reload` for local dev
- **FastAPI `/docs`** — auto-generated OpenAPI UI; available at http://localhost:8000/docs during development

## What Does NOT Exist Here

- No authentication or session management — single user, no login
- No background jobs or task queues — all operations are synchronous request/response
- No external API calls — the backend only talks to its local SQLite file
- No build step for the frontend — plain HTML/JS, no bundler
