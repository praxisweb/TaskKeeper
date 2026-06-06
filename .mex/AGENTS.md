---
name: agents
description: Always-loaded project anchor. Read this first. Contains project identity, non-negotiables, commands, and pointer to ROUTER.md for full context.
last_updated: 2026-06-06
---

# TaskKeeper

## What This Is

A single-user personal task tracker with a FastAPI REST backend, SQLite persistence, and a single-page HTML/JS Kanban frontend. No authentication — local use only.

## Non-Negotiables

- Never add authentication or multi-user logic — this is single-user, local-only by design
- Never write database queries outside of the repository/service layer (no raw SQL in route handlers)
- Never commit secrets or API keys
- Always soft-delete via the `deleted` flag; never hard-delete unless the user explicitly calls the permanent-delete endpoint
- All API inputs must be validated by Pydantic before touching the database

## Commands

- Dev: `uvicorn main:app --reload`
- Install: `pip install -r requirements.txt`
- Test: `pytest`
- Lint: `ruff check .`
- Open API docs: http://localhost:8000/docs

## Scaffold Growth
After every task: if no pattern exists for the task type you just completed, create one. If a pattern or context file is now out of date, update it. The scaffold grows from real work, not just setup. See the GROW step in `ROUTER.md` for details.

## Navigation
At the start of every session, read `ROUTER.md` before doing anything else.
For full project context, patterns, and task guidance — everything is there.
