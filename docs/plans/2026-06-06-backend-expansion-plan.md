# Backend Expansion (Complete Phase 1) Implementation Plan

> **For Antigravity:** REQUIRED WORKFLOW: Use `.agent/workflows/execute-plan.md` to execute this plan in single-flow mode.

**Goal:** Extend database schema columns, add PUT task modification, DELETE soft-delete, POST restore, and DELETE permanent-delete endpoints with exhaustive testing and safe migrations.

**Architecture:** Database updates handled dynamically in `init_db()` using `ALTER TABLE` to avoid breaking local dev databases. FastAPI models and routes updated to support full CRUD and soft-deletion filters.

**Tech Stack:** FastAPI, SQLite, Pydantic v2, pytest

---

## Task 1: Database Migration & Schema Alterations

**Files:**
- Modify: `main.py`
- Modify: `tests/test_main.py`

**Step 1: Write database schema tests**

Add to `tests/test_main.py`:

```python
import sqlite3
import main

def test_database_migrations_safe(tmp_path):
    # Setup: Create a legacy database without description, priority, due_date, deleted columns
    legacy_db = str(tmp_path / "legacy.db")
    with sqlite3.connect(legacy_db) as conn:
        conn.execute("""
            CREATE TABLE tasks (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                title      TEXT NOT NULL,
                status     TEXT NOT NULL DEFAULT 'todo'
                           CHECK(status IN ('todo', 'in_progress', 'done')),
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        conn.execute("INSERT INTO tasks (title, status) VALUES ('Legacy Task', 'todo')")
        conn.commit()

    # Execution: Trigger init_db with the patched path
    import os
    orig_db = main.DB_PATH
    main.DB_PATH = legacy_db
    try:
        main.init_db()
        
        # Verification: Check that new columns exist and legacy data is intact
        with sqlite3.connect(legacy_db) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM tasks WHERE title = 'Legacy Task'").fetchone()
            assert row["description"] is None
            assert row["priority"] == "medium"
            assert row["due_date"] is None
            assert row["deleted"] == 0
    finally:
        main.DB_PATH = orig_db
```

**Step 2: Run tests to verify failure**

Run: `cmd.exe /c "set PYTHONPATH=c:\Users\jason\Documents\Code\TaskKeeper && python -m pytest c:\Users\jason\Documents\Code\TaskKeeper\tests\test_main.py -k test_database_migrations_safe -v -p no:cacheprovider"`
Expected: FAIL (KeyError or sqlite3.OperationalError: no such column)

**Step 3: Modify `main.py` to add migrations to `init_db`**

Update the `init_db` function:

```python
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT NOT NULL,
                status      TEXT NOT NULL DEFAULT 'todo'
                            CHECK(status IN ('todo', 'in_progress', 'done')),
                created_at  TEXT NOT NULL DEFAULT (datetime('now')),
                description TEXT,
                priority    TEXT NOT NULL DEFAULT 'medium'
                            CHECK(priority IN ('low', 'medium', 'high')),
                due_date    TEXT,
                deleted     INTEGER NOT NULL DEFAULT 0
                            CHECK(deleted IN (0, 1))
            )
        """)
        # Auto-migration: Check if columns exist and add them if missing
        cursor = conn.execute("PRAGMA table_info(tasks)")
        columns = {row[1] for row in cursor.fetchall()}
        if "description" not in columns:
            conn.execute("ALTER TABLE tasks ADD COLUMN description TEXT")
        if "priority" not in columns:
            conn.execute("ALTER TABLE tasks ADD COLUMN priority TEXT NOT NULL DEFAULT 'medium' CHECK(priority IN ('low', 'medium', 'high'))")
        if "due_date" not in columns:
            conn.execute("ALTER TABLE tasks ADD COLUMN due_date TEXT")
        if "deleted" not in columns:
            conn.execute("ALTER TABLE tasks ADD COLUMN deleted INTEGER NOT NULL DEFAULT 0 CHECK(deleted IN (0, 1))")
        conn.commit()
```

**Step 4: Run test to verify it passes**

Run: `cmd.exe /c "set PYTHONPATH=c:\Users\jason\Documents\Code\TaskKeeper && python -m pytest c:\Users\jason\Documents\Code\TaskKeeper\tests\test_main.py -k test_database_migrations_safe -v -p no:cacheprovider"`
Expected: PASS

---

## Task 2: Pydantic Validation & Updates

**Files:**
- Modify: `main.py`
- Modify: `tests/test_main.py`

**Step 1: Write Pydantic validation tests**

Add to `tests/test_main.py`:

```python
def test_create_task_all_fields_success(client):
    payload = {
        "title": "Clean room",
        "status": "todo",
        "description": "Sweep and dust",
        "priority": "high",
        "due_date": "2026-06-30"
    }
    response = client.post("/tasks", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Clean room"
    assert data["description"] == "Sweep and dust"
    assert data["priority"] == "high"
    assert data["due_date"] == "2026-06-30"
    assert data["deleted"] is False


def test_create_task_rejects_invalid_due_date_format(client):
    payload = {
        "title": "Clean room",
        "due_date": "06/30/2026"
    }
    response = client.post("/tasks", json=payload)
    assert response.status_code == 422
```

**Step 2: Run tests to verify failure**

Run: `cmd.exe /c "set PYTHONPATH=c:\Users\jason\Documents\Code\TaskKeeper && python -m pytest c:\Users\jason\Documents\Code\TaskKeeper\tests\test_main.py -k \"test_create_task_all_fields_success or test_create_task_rejects_invalid_due_date_format\" -v -p no:cacheprovider"`
Expected: FAIL (ValidationError or response.status_code mismatch)

**Step 3: Update `TaskIn` and `TaskOut` Pydantic models in `main.py`**

Also update SQL insert fields inside `create_task()` to store description, priority, and due_date.

Update Pydantic models and POST route:

```python
import re

class TaskIn(BaseModel):
    title: str
    status: VALID_STATUSES = "todo"
    description: str | None = None
    priority: Literal["low", "medium", "high"] = "medium"
    due_date: str | None = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("title cannot be blank")
        return v.strip()

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            raise ValueError("due_date must be in YYYY-MM-DD format")
        return v


class TaskOut(BaseModel):
    id: int
    title: str
    status: str
    description: str | None
    priority: str
    due_date: str | None
    created_at: str
    deleted: bool
```

Modify `create_task` route in `main.py`:

```python
@app.post("/tasks", response_model=TaskOut, status_code=201)
def create_task(task: TaskIn):
    with get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO tasks (title, status, description, priority, due_date)
            VALUES (?, ?, ?, ?, ?)
            """,
            (task.title, task.status, task.description, task.priority, task.due_date),
        )
        conn.commit()
        row = conn.execute(
            "SELECT id, title, status, description, priority, due_date, created_at, deleted FROM tasks WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()
    # Map deleted integer (0/1) to bool in python dict
    data = dict(row)
    data["deleted"] = bool(data["deleted"])
    return data
```

**Step 4: Run tests to verify it passes**

Run: `cmd.exe /c "set PYTHONPATH=c:\Users\jason\Documents\Code\TaskKeeper && python -m pytest c:\Users\jason\Documents\Code\TaskKeeper\tests\test_main.py -k \"test_create_task_all_fields_success or test_create_task_rejects_invalid_due_date_format\" -v -p no:cacheprovider"`
Expected: PASS

---

## Task 3: PUT /tasks/{id} Endpoint

**Files:**
- Modify: `main.py`
- Modify: `tests/test_main.py`

**Step 1: Write PUT endpoint tests**

Add to `tests/test_main.py`:

```python
def test_update_task_success(client):
    # Create task
    task = client.post("/tasks", json={"title": "Fix bug", "status": "todo"}).json()
    task_id = task["id"]

    # Update task details
    payload = {
        "title": "Fix critical bug",
        "status": "in_progress",
        "description": "Race condition in queue",
        "priority": "high",
        "due_date": "2026-06-15"
    }
    response = client.put(f"/tasks/{task_id}", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Fix critical bug"
    assert data["status"] == "in_progress"
    assert data["description"] == "Race condition in queue"
    assert data["priority"] == "high"
    assert data["due_date"] == "2026-06-15"


def test_update_task_not_found(client):
    payload = {
        "title": "Not exists",
        "status": "todo"
    }
    response = client.put("/tasks/99999", json=payload)
    assert response.status_code == 404
```

**Step 2: Run tests to verify failure**

Run: `cmd.exe /c "set PYTHONPATH=c:\Users\jason\Documents\Code\TaskKeeper && python -m pytest c:\Users\jason\Documents\Code\TaskKeeper\tests\test_main.py -k \"test_update_task_success or test_update_task_not_found\" -v -p no:cacheprovider"`
Expected: FAIL (404 and 405 Method Not Allowed)

**Step 3: Add PUT route in `main.py`**

Add endpoint:

```python
from fastapi import HTTPException

@app.put("/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: int, task: TaskIn):
    with get_db() as conn:
        # Check existence
        existing = conn.execute("SELECT id FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Task not found")
        
        conn.execute(
            """
            UPDATE tasks
            SET title = ?, status = ?, description = ?, priority = ?, due_date = ?
            WHERE id = ?
            """,
            (task.title, task.status, task.description, task.priority, task.due_date, task_id),
        )
        conn.commit()
        
        row = conn.execute(
            "SELECT id, title, status, description, priority, due_date, created_at, deleted FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()
    data = dict(row)
    data["deleted"] = bool(data["deleted"])
    return data
```

**Step 4: Run tests to verify it passes**

Run: `cmd.exe /c "set PYTHONPATH=c:\Users\jason\Documents\Code\TaskKeeper && python -m pytest c:\Users\jason\Documents\Code\TaskKeeper\tests\test_main.py -k \"test_update_task_success or test_update_task_not_found\" -v -p no:cacheprovider"`
Expected: PASS

---

## Task 4: Soft-Delete & Restore Endpoints & GET Updates

**Files:**
- Modify: `main.py`
- Modify: `tests/test_main.py`

**Step 1: Write soft-delete, restore, and GET filtering tests**

Add to `tests/test_main.py`:

```python
def test_soft_delete_task(client):
    task = client.post("/tasks", json={"title": "Trash me"}).json()
    task_id = task["id"]

    # Delete task (soft delete)
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["deleted"] is True

    # Verify task no longer appears in normal active tasks
    active_tasks = client.get("/tasks").json()
    assert all(t["id"] != task_id for t in active_tasks)

    # Verify task appears in deleted tasks list
    deleted_tasks = client.get("/tasks?deleted=true").json()
    assert any(t["id"] == task_id for t in deleted_tasks)


def test_restore_task(client):
    task = client.post("/tasks", json={"title": "Save me"}).json()
    task_id = task["id"]

    # Soft-delete
    client.delete(f"/tasks/{task_id}")

    # Restore
    response = client.post(f"/tasks/{task_id}/restore")
    assert response.status_code == 200
    assert response.json()["deleted"] is False

    # Verify active again
    active_tasks = client.get("/tasks").json()
    assert any(t["id"] == task_id for t in active_tasks)
```

**Step 2: Run tests to verify failure**

Run: `cmd.exe /c "set PYTHONPATH=c:\Users\jason\Documents\Code\TaskKeeper && python -m pytest c:\Users\jason\Documents\Code\TaskKeeper\tests\test_main.py -k \"test_soft_delete_task or test_restore_task\" -v -p no:cacheprovider"`
Expected: FAIL (404 / 405 Method Not Allowed / deleted filters not implemented)

**Step 3: Modify GET, DELETE, and POST restore routes in `main.py`**

Update `get_tasks` endpoint to handle description, priority, due_date, deleted, and filters:

```python
@app.get("/tasks", response_model=list[TaskOut])
def get_tasks(status: VALID_STATUSES | None = None, deleted: bool = False):
    deleted_val = 1 if deleted else 0
    with get_db() as conn:
        if status:
            rows = conn.execute(
                """
                SELECT id, title, status, description, priority, due_date, created_at, deleted 
                FROM tasks 
                WHERE status = ? AND deleted = ? 
                ORDER BY created_at ASC
                """,
                (status, deleted_val),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT id, title, status, description, priority, due_date, created_at, deleted 
                FROM tasks 
                WHERE deleted = ? 
                ORDER BY created_at ASC
                """,
                (deleted_val,),
            ).fetchall()
    
    res = []
    for r in rows:
        d = dict(r)
        d["deleted"] = bool(d["deleted"])
        res.append(d)
    return res
```

Add soft-delete and restore routes to `main.py`:

```python
@app.delete("/tasks/{task_id}", response_model=TaskOut)
def soft_delete_task(task_id: int):
    with get_db() as conn:
        existing = conn.execute("SELECT id FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Task not found")
        
        conn.execute("UPDATE tasks SET deleted = 1 WHERE id = ?", (task_id,))
        conn.commit()
        
        row = conn.execute(
            "SELECT id, title, status, description, priority, due_date, created_at, deleted FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()
    data = dict(row)
    data["deleted"] = bool(data["deleted"])
    return data


@app.post("/tasks/{task_id}/restore", response_model=TaskOut)
def restore_task(task_id: int):
    with get_db() as conn:
        existing = conn.execute("SELECT id FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Task not found")
        
        conn.execute("UPDATE tasks SET deleted = 0 WHERE id = ?", (task_id,))
        conn.commit()
        
        row = conn.execute(
            "SELECT id, title, status, description, priority, due_date, created_at, deleted FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()
    data = dict(row)
    data["deleted"] = bool(data["deleted"])
    return data
```

**Step 4: Run tests to verify it passes**

Run: `cmd.exe /c "set PYTHONPATH=c:\Users\jason\Documents\Code\TaskKeeper && python -m pytest c:\Users\jason\Documents\Code\TaskKeeper\tests\test_main.py -k \"test_soft_delete_task or test_restore_task\" -v -p no:cacheprovider"`
Expected: PASS

---

## Task 5: Permanent Delete Endpoint

**Files:**
- Modify: `main.py`
- Modify: `tests/test_main.py`

**Step 1: Write permanent delete tests**

Add to `tests/test_main.py`:

```python
def test_permanent_delete_task(client):
    task = client.post("/tasks", json={"title": "Vanish me"}).json()
    task_id = task["id"]

    # Permanent delete
    response = client.delete(f"/tasks/{task_id}/permanent")
    assert response.status_code == 200
    assert response.json() == {"detail": "Task permanently deleted"}

    # Verify task completely gone (even from deleted/trash tasks list)
    all_deleted = client.get("/tasks?deleted=true").json()
    assert all(t["id"] != task_id for t in all_deleted)


def test_permanent_delete_not_found(client):
    response = client.delete("/tasks/99999/permanent")
    assert response.status_code == 404
```

**Step 2: Run tests to verify failure**

Run: `cmd.exe /c "set PYTHONPATH=c:\Users\jason\Documents\Code\TaskKeeper && python -m pytest c:\Users\jason\Documents\Code\TaskKeeper\tests\test_main.py -k \"test_permanent_delete\" -v -p no:cacheprovider"`
Expected: FAIL (404 / 405 Method Not Allowed)

**Step 3: Add DELETE permanent endpoint to `main.py`**

Add endpoint:

```python
@app.delete("/tasks/{task_id}/permanent")
def permanent_delete_task(task_id: int):
    with get_db() as conn:
        existing = conn.execute("SELECT id FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Task not found")
        
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
    return {"detail": "Task permanently deleted"}
```

**Step 4: Run all tests to verify they pass**

Run: `cmd.exe /c "set PYTHONPATH=c:\Users\jason\Documents\Code\TaskKeeper && python -m pytest c:\Users\jason\Documents\Code\TaskKeeper\tests\test_main.py -v -p no:cacheprovider"`
Expected: 20 passed.

---

## Done Criteria

- [ ] `pytest tests/test_main.py -v -p no:cacheprovider` — all 20 tests pass.
- [ ] Swagger Docs (`/docs`) exposes the new models, fields, and `PUT`, `DELETE` (soft), `POST` (restore), and `DELETE` (permanent) routes.
- [ ] Older task records in the existing `tasks.db` database are migrated automatically on server start with default values (`priority: medium`, `deleted: 0`).
