---
name: add-task-field
description: Adding a new field to the Task model — covers the DB model, Pydantic schemas, API response, and frontend card rendering.
triggers:
  - "add field"
  - "new column"
  - "add attribute"
  - "task field"
edges:
  - target: context/conventions.md
    condition: when verifying Pydantic v2 schema conventions and naming
  - target: context/stack.md
    condition: when checking SQLAlchemy 2.x vs 1.x syntax for model columns
  - target: patterns/add-endpoint.md
    condition: when the new field requires a new endpoint or changes an existing one
last_updated: 2026-06-06
---

# Add a New Field to the Task Model

## Context

Load `context/stack.md` before starting — specifically the SQLAlchemy 2.x and Pydantic v2 version constraints.

Adding a field touches 4 layers: DB model → Pydantic schemas → API endpoints → frontend rendering.

**Important:** We do not use Alembic. After changing the model, delete `taskkeeper.db` and let `create_all()` recreate it. This is acceptable for local dev — document any data loss in your commit message.

## Steps

1. **Add the column to the SQLAlchemy model** in `models/task.py`:
   ```python
   # Example: adding a nullable string field
   notes: Mapped[Optional[str]] = mapped_column(String, nullable=True, default=None)
   ```
   - Use `Mapped[T]` type annotations (SQLAlchemy 2.x declarative style)
   - New fields should be `nullable=True` with a default so existing rows (after DB recreate) are not broken

2. **Update Pydantic schemas** in `schemas/task.py`:
   - Add to `TaskCreate` if it's user-supplied on creation
   - Add to `TaskUpdate` if it's user-editable
   - Add to `TaskResponse` always — this is what the API returns
   - Mark optional fields as `Optional[str] = None`

3. **Verify the API response** includes the new field:
   - `GET /tasks` and `GET /tasks/{id}` should now return the field
   - No endpoint changes needed unless you're adding a new filter/query param

4. **Update the frontend** in `frontend/app.js`:
   - Add the field to the task card render function if it should be visible on the card
   - Add the field to the edit modal form if it should be editable
   - Add the field to the `createTask` / `updateTask` fetch calls if it's user-supplied

5. **Delete `taskkeeper.db`** and restart the server to apply the schema change.

6. **Update the test** in `tests/test_tasks.py`:
   - Add the field to any fixture task dicts
   - Assert the field appears in the response JSON

## Gotchas

[VERIFY AFTER FIRST IMPLEMENTATION]
- **Schema drift**: If you forget to add the field to `TaskResponse`, FastAPI will silently drop it from the response (Pydantic only serializes declared fields).
- **DB file not deleted**: Old `taskkeeper.db` will not have the new column — you'll get a `OperationalError: table tasks has no column named X`. Always delete and restart.
- **Pydantic v2 `model_config`**: Response schemas need `model_config = ConfigDict(from_attributes=True)` to read from SQLAlchemy ORM objects.

## Verify

- [ ] Field added to SQLAlchemy model with `Mapped[T]` annotation
- [ ] Field added to all relevant Pydantic schemas (`TaskCreate`, `TaskUpdate`, `TaskResponse`)
- [ ] `taskkeeper.db` deleted and server restarted
- [ ] `GET /tasks/{id}` response JSON contains the new field
- [ ] Frontend renders or edits the new field where appropriate
- [ ] Test updated and passing

## Update Scaffold
- [ ] If this field fundamentally changes what a Task is, update the Task Entity section in `context/architecture.md`
- [ ] Update `.mex/ROUTER.md` Current Project State if a requirement is now satisfied
