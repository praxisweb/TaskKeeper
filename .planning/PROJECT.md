# TaskKeeper

## What This Is

A single-user personal task tracker with a FastAPI REST backend, SQLite persistence, and a single-page HTML/JS Kanban frontend. No authentication — local use only.

## Core Value

A fast, friction-free way to manage personal tasks across a Kanban board (To Do / In Progress / Done) without cloud accounts, logins, or external dependencies.

## Context

- **Who it's for:** A single developer running this locally on their own machine
- **How it runs:** Local only — user starts the server manually, no deployment or hosting needed
- **Tech stack:** FastAPI (Python) + SQLite + vanilla HTML/JS SPA
- **Constraint:** No auth, no multi-user, no cloud — intentionally simple

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] **TASK-01**: User can create a task with a title, optional description, due date, and priority (low / medium / high)
- [ ] **TASK-02**: User can edit any field of an existing task
- [ ] **TASK-03**: User can mark a task complete (moves it to Done column)
- [ ] **TASK-04**: User can move tasks between To Do, In Progress, and Done columns
- [ ] **TASK-05**: User can soft-delete a task (removed from main board)
- [ ] **TASK-06**: User can view a trash screen showing all soft-deleted tasks
- [ ] **TASK-07**: User can restore a soft-deleted task back to its previous status
- [ ] **TASK-08**: User can permanently delete a task from trash
- [ ] **API-01**: REST API exposes CRUD endpoints for tasks
- [ ] **API-02**: API supports filtering tasks by status and deleted state
- [ ] **UI-01**: Kanban board with three columns: To Do, In Progress, Done
- [ ] **UI-02**: Task cards show title, priority, and due date at a glance
- [ ] **UI-03**: Inline create form within each column (or global add button)
- [ ] **UI-04**: Task detail view/modal for editing description and all fields
- [ ] **UI-05**: Trash view accessible from main board
- [ ] **PERSIST-01**: All task data persisted in SQLite on disk (survives server restart)

### Out of Scope

- Authentication or user accounts — single user, no login
- Multi-user or real-time collaboration
- Cloud sync or external database (Postgres, MySQL, etc.)
- Email/push notifications
- Recurring tasks or task dependencies
- Mobile-native app (web only, but responsive is acceptable)
- Tags/labels — deliberately deferred to keep v1 simple

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| FastAPI over Flask/Django | Async-ready, automatic OpenAPI docs, Pydantic validation built in | — Pending |
| SQLite over Postgres | No external server to manage; single user means no concurrency concerns | — Pending |
| Vanilla HTML/JS over React/Vue | No build toolchain; single file the browser can open directly | — Pending |
| Soft-delete with trash view | Prevents accidental data loss without adding complexity of undo history | — Pending |
| No authentication | Explicitly out of scope — single user running locally | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-06-06 after initialization*
