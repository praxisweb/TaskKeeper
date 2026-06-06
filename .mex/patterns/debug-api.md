---
name: debug-api
description: Diagnosing failures in the FastAPI request pipeline — covers 4xx/5xx errors, SQLAlchemy errors, and frontend fetch failures.
triggers:
  - "debug"
  - "error"
  - "500"
  - "422"
  - "fetch failed"
  - "not found"
  - "broken"
edges:
  - target: context/architecture.md
    condition: when tracing which layer the failure is in (router vs service vs repository)
  - target: patterns/add-endpoint.md
    condition: when a broken endpoint needs to be compared against the correct pattern
last_updated: 2026-06-06
---

# Debug API Failures

## Context

Load `context/architecture.md`. The failure boundary map is:

```
Browser fetch → FastAPI router → Service → Repository → SQLite
     ↑                ↑              ↑            ↑
  CORS/URL         422/500       HTTPException  OperationalError
```

Start at the outermost layer and work inward.

## Task: Debug HTTP 422 Unprocessable Entity

### Steps
1. Check the response body — FastAPI returns a detailed `{"detail": [...]}` JSON with field-level errors
2. Compare field names in the request JSON to the Pydantic schema in `schemas/task.py`
3. Check field types — `"priority": "high"` vs `"priority": 1` (type mismatch)
4. Check for required vs optional fields — missing required fields cause 422

### Gotchas
- `422` from FastAPI means Pydantic rejected the input before the route handler ran
- Query parameter type coercion: `?deleted=True` (capital T) may not parse as bool — use `?deleted=true`

---

## Task: Debug HTTP 500 Internal Server Error

### Steps
1. Check the Uvicorn terminal for the Python traceback — it is always printed there
2. Find the failing line and identify which layer it's in (router / service / repository)
3. Common causes:
   - `AttributeError: 'NoneType'` — `db.get(Task, id)` returned `None`; add a 404 guard before using the result
   - `OperationalError: no such column` — model changed but DB not recreated; delete `taskkeeper.db`
   - `DetachedInstanceError` — SQLAlchemy object used after session closed; check `db.refresh()` placement

---

## Task: Debug Frontend Fetch Failures

### Steps
1. Open browser DevTools → Network tab → find the failing request
2. Check the request URL — is the port correct? Is the path correct (no typos, right `/tasks/{id}` format)?
3. Check the request body — open the failing request → Payload tab → verify JSON shape matches the Pydantic schema
4. Check the response — if `{"detail": ...}`, that is a FastAPI validation or business logic error; read it
5. Check for CORS errors in the Console — if present, add `CORSMiddleware` to `main.py`

### Gotchas
[VERIFY AFTER FIRST IMPLEMENTATION]
- Fetch default method is `GET` — always specify `method: "POST"` etc. explicitly
- `Content-Type: application/json` header must be set on POST/PUT requests or FastAPI returns 422
- If the frontend is opened as a local file (`file://`) rather than served by FastAPI, `fetch` to `localhost:8000` will trigger CORS — serve the frontend via FastAPI `StaticFiles` instead

---

## Task: Debug SQLAlchemy / Database Errors

### Steps
1. `OperationalError: no such table` → `Base.metadata.create_all()` not called on startup; check `main.py` startup event
2. `OperationalError: no such column` → Model changed after DB created; delete `taskkeeper.db` and restart
3. `IntegrityError` → Constraint violation (e.g. NOT NULL on a required field); check the data being inserted
4. `MissingGreenlet` → Async/sync SQLAlchemy mismatch; check you are using sync `Session`, not `AsyncSession`

## Update Scaffold
- [ ] If a new failure mode is discovered, add it to the appropriate "Gotchas" section above
- [ ] If a new component was the source of failure, update `context/architecture.md` with the boundary note
