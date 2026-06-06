---
name: add-endpoint
description: Adding a new FastAPI route handler with service and repository layers — the full vertical slice from router to DB.
triggers:
  - "add endpoint"
  - "new route"
  - "add API"
  - "new endpoint"
edges:
  - target: context/conventions.md
    condition: when verifying naming, layer boundaries, and Pydantic v2 usage
  - target: context/architecture.md
    condition: when understanding where the new endpoint fits in the router/service/repository stack
  - target: patterns/add-task-field.md
    condition: when the new endpoint involves changes to the Task model schema
last_updated: 2026-06-06
---

# Add a New API Endpoint

## Context

Load `context/architecture.md` and `context/conventions.md` before starting.

The routing stack is: `routers/tasks.py` → `services/task_service.py` → `repositories/task_repository.py` → SQLAlchemy → SQLite.

Route handlers must be thin. All logic lives in the service. All queries live in the repository.

## Steps

1. **Add the Pydantic schema** in `schemas/task.py` if the endpoint has a new request body or a new response shape.
   - Request body: `class TaskXCreate(BaseModel)` or `class TaskXUpdate(BaseModel)`
   - Response: `class TaskXResponse(BaseModel)` with `model_config = ConfigDict(from_attributes=True)`

2. **Add the repository method** in `repositories/task_repository.py`:
   - Method receives a `db: Session` as the first argument
   - Use SQLAlchemy 2.0 style: `db.get(Task, id)`, `db.execute(select(Task).where(...))`, not `db.query(Task)`
   - Call `db.commit()` after writes; call `db.refresh(obj)` if you need the updated state

3. **Add the service method** in `services/task_service.py`:
   - Inject `TaskRepository` (or instantiate it)
   - Handle business rules here (e.g., soft-delete guard, status validation)
   - Raise `HTTPException(status_code=404, detail="Task not found")` for missing resources — not from the repository

4. **Add the route handler** in `routers/tasks.py`:
   - Decorator: `@router.get/post/put/delete("/tasks/...")`
   - Signature: `(db: Session = Depends(get_db), ...path/query params...)`
   - Body: call the service method, return the result (FastAPI serializes via Pydantic)

5. **Write the test** in `tests/test_tasks.py`:
   - Use `TestClient(app)` from `fastapi.testclient`
   - Test the happy path + at least one error case (missing resource, invalid input)

## Gotchas

- **SQLAlchemy 2.0 API**: Use `db.get(Task, id)` (returns `None` if not found, no `.first()`). Use `db.scalars(select(...))` for lists.
- **Pydantic v2**: Use `model_validate(db_obj)` in the route to serialize. `from_orm()` will raise an error.
- **Session lifecycle**: Never call `SessionLocal()` manually in a route. Always use `Depends(get_db)`.
- **Soft-delete filter**: `GET /tasks` must always filter `deleted=False` by default unless the caller explicitly passes `?deleted=true`. Don't forget this in new list endpoints.

## Verify

Before presenting code:
- [ ] Route handler contains no business logic (only calls service)
- [ ] Service contains no raw SQL or `db.query()` calls
- [ ] Repository uses SQLAlchemy 2.0 API throughout
- [ ] Response model uses `model_validate`, not `from_orm`
- [ ] Test covers happy path and 404 case
- [ ] Soft-delete filter applied to any list endpoint

## Debug

- **422 Unprocessable Entity**: Pydantic rejected the request body. Check schema field names and types match the JSON being sent.
- **`greenlet_spawn` errors**: SQLAlchemy async/sync mismatch. Check you are not mixing async DB calls with sync session.
- **`MissingGreenlet` or `DetachedInstanceError`**: Relationship accessed after session closed. Either eager-load with `joinedload` or access within the session scope.

## Update Scaffold
- [ ] Update `.mex/ROUTER.md` "Current Project State" if a new endpoint completes a phase requirement
- [ ] Update `.mex/context/architecture.md` if a new component was introduced
- [ ] If this is the first endpoint of a new domain, consider creating a domain-specific context file
