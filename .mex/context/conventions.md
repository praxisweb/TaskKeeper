---
name: conventions
description: How code is written in this project — naming, structure, patterns, and style. Load when writing new code or reviewing existing code.
triggers:
  - "convention"
  - "pattern"
  - "naming"
  - "style"
  - "how should I"
  - "what's the right way"
edges:
  - target: context/architecture.md
    condition: when a convention depends on understanding how the router/service/repository layers relate
  - target: context/stack.md
    condition: when a convention is tied to a specific library (SQLAlchemy session handling, Pydantic v2 API)
  - target: patterns/add-endpoint.md
    condition: when writing a new API endpoint and need the full step-by-step pattern
last_updated: 2026-06-06
---

# Conventions

## Naming

- **Python files**: `snake_case` (`task_service.py`, not `TaskService.py`)
- **Python functions and variables**: `snake_case`, verb-first for functions (`get_task_by_id`, `create_task`)
- **Python classes**: `PascalCase` (`TaskService`, `TaskRepository`)
- **Pydantic schemas**: suffix with `Create`, `Update`, `Response` (`TaskCreate`, `TaskUpdate`, `TaskResponse`)
- **SQLAlchemy model**: `Task` (singular, no suffix)
- **API endpoints**: kebab-case paths (`/tasks/{id}/permanent-delete`) — use hyphens in URLs, not underscores
- **Frontend JS variables**: `camelCase`; DOM element refs prefixed with `$` (`$board`, `$trashList`)

## Structure

```
taskkeeper/
├── main.py                    # FastAPI app, startup, static file mount
├── models/
│   └── task.py                # SQLAlchemy Task model
├── schemas/
│   └── task.py                # Pydantic request/response schemas
├── routers/
│   └── tasks.py               # /tasks route handlers (thin — delegate to service)
├── services/
│   └── task_service.py        # Business logic (soft-delete rules, restore logic)
├── repositories/
│   └── task_repository.py     # All SQLAlchemy queries
├── database.py                # Engine, SessionLocal, Base
├── frontend/
│   ├── index.html             # Kanban SPA
│   └── app.js                 # Frontend JS (fetch calls, render logic)
└── tests/
    └── test_tasks.py          # pytest tests for all endpoints
```

- Business logic lives in `services/`, never in route handlers
- All DB queries live in `repositories/`, never in services or handlers directly
- Route handlers should be thin: validate input (Pydantic does this), call service, return response

## Patterns

**Soft-delete pattern** — tasks are never hard-deleted via the standard DELETE endpoint:
```python
# Correct — in TaskRepository
def soft_delete(self, db: Session, task_id: int) -> Task:
    task = db.get(Task, task_id)
    task.deleted = True
    db.commit()
    return task

# Wrong — never do this in the standard delete route
db.delete(task)
db.commit()
```

**SQLAlchemy session pattern** — always use the dependency-injected session:
```python
# In routers/tasks.py — correct
def get_tasks(db: Session = Depends(get_db)):
    ...

# Wrong — never create a session manually in a route handler
db = SessionLocal()
```

**Pydantic v2 pattern** — use current v2 API:
```python
# Correct
task_response = TaskResponse.model_validate(db_task)

# Wrong (v1 API — will break)
task_response = TaskResponse.from_orm(db_task)
```

## Verify Checklist

Before presenting any code:
- [ ] Business logic is not in route handlers (it's in `services/`)
- [ ] All database access goes through `repositories/` (no `db.query()` in services or handlers)
- [ ] Soft-delete uses `deleted=True` flag; never `db.delete()` in standard flows
- [ ] Pydantic schemas use v2 API (`model_validate`, `model_dump`, not `.dict()` or `.from_orm()`)
- [ ] SQLAlchemy uses 2.0-style `db.execute()` / `db.get()`; not legacy `db.query(Model).filter()`
- [ ] New files follow the naming and folder conventions above
- [ ] No authentication logic introduced (it is explicitly out of scope)
