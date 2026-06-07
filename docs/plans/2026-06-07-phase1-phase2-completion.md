# Complete Phase 1 and Phase 2 Implementation Plan

> **For Antigravity:** REQUIRED WORKFLOW: Use `.agent/workflows/execute-plan.md` to execute this plan in single-flow mode.

**Goal:** Complete all Phase 1 backend tasks (migrations, PUT, soft-delete, restore, permanent delete, GET filters) and Phase 2 frontend tasks (rich Kanban board UI with creation, details modal, status transitions, and premium responsive aesthetics).

**Architecture:** 
- Backend updates `init_db()` to dynamically detect and add new columns to `tasks` using `PRAGMA table_info` and `ALTER TABLE`.
- FastAPI models and endpoints are expanded to support full CRUD and filtering.
- Frontend is a premium, single-page Kanban board styled with CSS glassmorphism, Outfit font, custom color priority badges, and an interactive task detail modal.

**Tech Stack:** FastAPI, SQLite, Pydantic v2, pytest, HTML5, Vanilla CSS, Vanilla JavaScript.

---

### Task 1: Database Migration & Schema Alterations

**Files:**
- Modify: `main.py`
- Modify: `tests/test_main.py`

**Step 1: Write database schema migration test**

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
    orig_db = main.DB_PATH
    main.DB_PATH = legacy_db
    try:
        main.init_db()
        
        # Verification: Check that new columns exist and legacy data is intact
        with sqlite3.connect(legacy_db) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM tasks WHERE title = 'Legacy Task'").fetchone()
            assert "description" in row.keys()
            assert row["description"] is None
            assert row["priority"] == "medium"
            assert row["due_date"] is None
            assert row["deleted"] == 0
    finally:
        main.DB_PATH = orig_db
```

**Step 2: Run test to verify it fails**

Run: `cmd.exe /c "set PYTHONPATH=. && pytest tests/test_main.py -k test_database_migrations_safe -v -p no:cacheprovider"`
Expected: FAIL (sqlite3.OperationalError or assertion failures on missing columns)

**Step 3: Modify `init_db()` in `main.py`**

Update `init_db` to run migrations dynamically:

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
        # Dynamic migration for existing DB files
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

Run: `cmd.exe /c "set PYTHONPATH=. && pytest tests/test_main.py -k test_database_migrations_safe -v -p no:cacheprovider"`
Expected: PASS

**Step 5: Commit**

```bash
git add main.py tests/test_main.py
git commit -m "feat: implement database dynamic schema migration on start"
```

---

### Task 2: Pydantic Validation & Updates

**Files:**
- Modify: `main.py`
- Modify: `tests/test_main.py`

**Step 1: Write Pydantic schema validation tests**

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

def test_create_task_rejects_invalid_priority(client):
    payload = {
        "title": "Clean room",
        "priority": "critical"
    }
    response = client.post("/tasks", json=payload)
    assert response.status_code == 422
```

**Step 2: Run tests to verify failure**

Run: `cmd.exe /c "set PYTHONPATH=. && pytest tests/test_main.py -k \"all_fields or invalid_due_date or invalid_priority\" -v -p no:cacheprovider"`
Expected: FAIL

**Step 3: Update `TaskIn`, `TaskOut` and `create_task()` in `main.py`**

Modify models and post handler:

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
        if v is None or v == "":
            return None
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
    data = dict(row)
    data["deleted"] = bool(data["deleted"])
    return data
```

**Step 4: Run tests to verify it passes**

Run: `cmd.exe /c "set PYTHONPATH=. && pytest tests/test_main.py -v -p no:cacheprovider"`
Expected: PASS

**Step 5: Commit**

```bash
git add main.py tests/test_main.py
git commit -m "feat: expand Pydantic validations and store extra columns in DB"
```

---

### Task 3: PUT /tasks/{id} Endpoint

**Files:**
- Modify: `main.py`
- Modify: `tests/test_main.py`

**Step 1: Write tests for PUT endpoint**

Add to `tests/test_main.py`:

```python
def test_update_task_success(client):
    task = client.post("/tasks", json={"title": "Fix bug", "status": "todo"}).json()
    task_id = task["id"]

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

Run: `cmd.exe /c "set PYTHONPATH=. && pytest tests/test_main.py -k update_task -v -p no:cacheprovider"`
Expected: FAIL

**Step 3: Implement PUT endpoint in `main.py`**

Add endpoint:

```python
from fastapi import HTTPException

@app.put("/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: int, task: TaskIn):
    with get_db() as conn:
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

Run: `cmd.exe /c "set PYTHONPATH=. && pytest tests/test_main.py -k update_task -v -p no:cacheprovider"`
Expected: PASS

**Step 5: Commit**

```bash
git add main.py tests/test_main.py
git commit -m "feat: implement PUT /tasks/{id} task modification endpoint"
```

---

### Task 4: Soft-Delete, Restore & GET Filtering Endpoints

**Files:**
- Modify: `main.py`
- Modify: `tests/test_main.py`

**Step 1: Write soft-delete, restore, and filtering tests**

Add to `tests/test_main.py`:

```python
def test_soft_delete_task(client):
    task = client.post("/tasks", json={"title": "Trash me"}).json()
    task_id = task["id"]

    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["deleted"] is True

    # Active tasks should not return soft-deleted tasks
    active_tasks = client.get("/tasks").json()
    assert all(t["id"] != task_id for t in active_tasks)

    # Deleted tasks list should return it
    deleted_tasks = client.get("/tasks?deleted=true").json()
    assert any(t["id"] == task_id for t in deleted_tasks)

def test_restore_task(client):
    task = client.post("/tasks", json={"title": "Save me"}).json()
    task_id = task["id"]

    client.delete(f"/tasks/{task_id}")
    response = client.post(f"/tasks/{task_id}/restore")
    assert response.status_code == 200
    assert response.json()["deleted"] is False

    active_tasks = client.get("/tasks").json()
    assert any(t["id"] == task_id for t in active_tasks)
```

**Step 2: Run tests to verify failure**

Run: `cmd.exe /c "set PYTHONPATH=. && pytest tests/test_main.py -k \"soft_delete_task or restore_task\" -v -p no:cacheprovider"`
Expected: FAIL

**Step 3: Update GET /tasks and implement DELETE and POST restore endpoints in `main.py`**

Modify:

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

Run: `cmd.exe /c "set PYTHONPATH=. && pytest tests/test_main.py -v -p no:cacheprovider"`
Expected: PASS

**Step 5: Commit**

```bash
git add main.py tests/test_main.py
git commit -m "feat: implement soft-delete, restore, and GET deleted task filtering"
```

---

### Task 5: Permanent Delete Endpoint

**Files:**
- Modify: `main.py`
- Modify: `tests/test_main.py`

**Step 1: Write permanent delete tests**

Add to `tests/test_main.py`:

```python
def test_permanent_delete_task(client):
    task = client.post("/tasks", json={"title": "Vanish me"}).json()
    task_id = task["id"]

    response = client.delete(f"/tasks/{task_id}/permanent")
    assert response.status_code == 200
    assert response.json() == {"detail": "Task permanently deleted"}

    all_deleted = client.get("/tasks?deleted=true").json()
    assert all(t["id"] != task_id for t in all_deleted)

def test_permanent_delete_not_found(client):
    response = client.delete("/tasks/99999/permanent")
    assert response.status_code == 404
```

**Step 2: Run tests to verify failure**

Run: `cmd.exe /c "set PYTHONPATH=. && pytest tests/test_main.py -k permanent_delete -v -p no:cacheprovider"`
Expected: FAIL

**Step 3: Implement permanent delete endpoint in `main.py`**

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

**Step 4: Run tests to verify it passes**

Run: `cmd.exe /c "set PYTHONPATH=. && pytest tests/test_main.py -v -p no:cacheprovider"`
Expected: PASS

**Step 5: Commit**

```bash
git add main.py tests/test_main.py
git commit -m "feat: implement permanent delete endpoint"
```

---

### Task 6: Kanban Frontend Interface (Phase 2 UI implementation)

**Files:**
- Modify: `index.html`

**Step 1: Design and Implement index.html**

We will build a gorgeous dark/indigo glassmorphism Kanban Board:
- Google Font: Inter & Outfit
- Board layout: 3 columns (To Do, In Progress, Done)
- Tasks are displayed as cards with description (if present), priority badge, and due date.
- Floating Add button or Column-specific inline add buttons.
- Editing via a modal detailing title, status, description, priority, due date.
- Move controls (quick status dropdown on card or buttons) to satisfy "moves tasks between columns".
- Glassmorphism UI elements (deep gradient backgrounds, transparent borders, box shadows, and hover transitions).

**Step 2: Verification**
Manual validation in browser for rendering, saving, editing, status change, and validation errors.

**Step 3: Commit**

```bash
git add index.html
git commit -m "feat: build premium responsive glassmorphism Kanban frontend with modal editing"
```
