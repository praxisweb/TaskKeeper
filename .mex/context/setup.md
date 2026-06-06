---
name: setup
description: Dev environment setup and commands. Load when setting up the project for the first time or when environment issues arise.
triggers:
  - "setup"
  - "install"
  - "environment"
  - "getting started"
  - "how do I run"
  - "local development"
edges:
  - target: context/stack.md
    condition: when specific technology versions or library details are needed (Python, SQLAlchemy, Pydantic versions)
  - target: context/architecture.md
    condition: when understanding how components connect during setup (StaticFiles mount, database init on startup)
last_updated: 2026-06-06
---

# Setup

## Prerequisites

- Python 3.11+
- pip (comes with Python)
- A modern browser (Chrome, Firefox, Edge) for the Kanban frontend

## First-time Setup

1. Clone the repository and navigate to it
2. Create a virtual environment: `python -m venv .venv`
3. Activate it:
   - Windows: `.venv\Scripts\activate`
   - macOS/Linux: `source .venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Start the server: `uvicorn main:app --reload`
6. Open the app: http://localhost:8000
7. Open API docs: http://localhost:8000/docs

The SQLite database file (`taskkeeper.db`) is created automatically on first run.

## Environment Variables

No environment variables required. This is an intentionally configuration-free local application.

- `DATABASE_URL` (optional) — defaults to `sqlite:///./taskkeeper.db`; override only if you want a different path

## Common Commands

- `uvicorn main:app --reload` — start dev server on port 8000 with hot reload
- `pip install -r requirements.txt` — install all dependencies
- `pytest` — run full test suite
- `pytest -v` — verbose test output
- `ruff check .` — run linter
- `ruff format .` — run formatter

## Common Issues

**Port 8000 already in use:**
Run `uvicorn main:app --reload --port 8001` to use a different port.

**`taskkeeper.db` schema is wrong after a model change:**
Delete `taskkeeper.db` and restart the server — `create_all()` will recreate it. (This is acceptable for local dev; no migration tool is used.)

**Frontend not updating after API changes:**
Hard refresh the browser (`Ctrl+Shift+R`) to clear any cached JS.
