---
name: agents
description: Always-loaded project anchor. Read this first. Contains project identity, non-negotiables, commands, and pointer to ROUTER.md for full context.
last_updated: [YYYY-MM-DD]
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

## After Every Task
After completing any task: update `.mex/ROUTER.md` project state and any `.mex/` files that are now out of date. If no pattern existed for the task you just completed, create one in `.mex/patterns/`.

## Agent skills

### Issue tracker

Issues live in GitHub Issues at `https://github.com/praxisweb/TaskKeeper` (use the `gh` CLI). See `docs/agents/issue-tracker.md`.

### Triage labels

Default label vocabulary: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context repo. `CONTEXT.md` at root; ADRs at `docs/architecture/decisions/` (not `docs/adr/`). See `docs/agents/domain.md`.

## Navigation
At the start of every session, read `.mex/ROUTER.md` before doing anything else.
For full project context, patterns, and task guidance — everything is there.
