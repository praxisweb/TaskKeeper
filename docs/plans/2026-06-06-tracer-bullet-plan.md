# TaskKeeper v0.1 — Tracer Bullet Implementation Plan

> **For Antigravity:** REQUIRED WORKFLOW: Use `.agent/workflows/execute-plan.md` to execute this plan in single-flow mode.

**Goal:** Build one working vertical slice — create a task via a form, persist it in SQLite, and render all tasks on a Kanban board.

**Architecture:** Flat three-file layout: `main.py` (FastAPI app + DB + routes), `tasks.db` (SQLite, auto-created), `index.html` (vanilla JS SPA). No auth, no migrations tool, no build step.

**Tech Stack:** Python 3.11+, FastAPI, uvicorn, SQLite (stdlib `sqlite3`), Pydantic v2, vanilla HTML/CSS/JS

---

## Task 1: Project Bootstrap

**Files:**
- Create: `requirements.txt`
- Create: `main.py`

**Step 1: Write `requirements.txt`**

```
fastapi>=0.111.0
uvicorn[standard]>=0.29.0
```

**Step 2: Install dependencies**

```bash
pip install -r requirements.txt
```

Expected: packages install without errors.

**Step 3: Write the failing smoke test**

Create `tests/test_main.py`:

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

**Step 4: Run test — verify it fails**

```bash
pytest tests/test_main.py::test_health -v
```

Expected: FAIL — `main` module not found or `/health` not defined.

**Step 5: Write minimal `main.py`**

```python
import sqlite3
from contextlib import contextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

DB_PATH = "tasks.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                title      TEXT NOT NULL,
                status     TEXT NOT NULL DEFAULT 'todo',
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        conn.commit()

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

app = FastAPI(title="TaskKeeper")

@app.on_event("startup")
def startup():
    init_db()

@app.get("/health")
def health():
    return {"status": "ok"}
```

**Step 6: Run test — verify it passes**

```bash
pytest tests/test_main.py::test_health -v
```

Expected: PASS.

**Step 7: Commit**

```bash
git add requirements.txt main.py tests/test_main.py
git commit -m "feat: bootstrap FastAPI app with health endpoint and SQLite init"
```

---

## Task 2: POST /tasks endpoint

**Files:**
- Modify: `main.py`
- Modify: `tests/test_main.py`

**Step 1: Write the failing test**

Add to `tests/test_main.py`:

```python
def test_create_task_returns_201():
    response = client.post("/tasks", json={"title": "Buy milk"})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Buy milk"
    assert data["status"] == "todo"
    assert "id" in data
    assert "created_at" in data

def test_create_task_rejects_missing_title():
    response = client.post("/tasks", json={})
    assert response.status_code == 422

def test_create_task_rejects_invalid_status():
    response = client.post("/tasks", json={"title": "X", "status": "flying"})
    assert response.status_code == 422
```

**Step 2: Run tests — verify they fail**

```bash
pytest tests/test_main.py -v
```

Expected: 3 new tests fail — route not defined.

**Step 3: Add Pydantic models and POST route to `main.py`**

Add after the `health` route:

```python
from typing import Literal, Optional
from pydantic import BaseModel
from fastapi import Response

VALID_STATUSES = Literal["todo", "in_progress", "done"]

class TaskIn(BaseModel):
    title: str
    status: VALID_STATUSES = "todo"

class TaskOut(BaseModel):
    id: int
    title: str
    status: str
    created_at: str

@app.post("/tasks", response_model=TaskOut, status_code=201)
def create_task(task: TaskIn):
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO tasks (title, status) VALUES (?, ?)",
            (task.title, task.status),
        )
        conn.commit()
        row = conn.execute(
            "SELECT id, title, status, created_at FROM tasks WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()
    return dict(row)
```

**Step 4: Run tests — verify they pass**

```bash
pytest tests/test_main.py -v
```

Expected: all tests PASS.

**Step 5: Commit**

```bash
git add main.py tests/test_main.py
git commit -m "feat: add POST /tasks endpoint with Pydantic validation"
```

---

## Task 3: GET /tasks endpoint

**Files:**
- Modify: `main.py`
- Modify: `tests/test_main.py`

**Step 1: Write the failing tests**

Add to `tests/test_main.py`:

```python
def test_get_tasks_returns_list():
    # Create a known task first
    client.post("/tasks", json={"title": "Get tasks test"})
    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(t["title"] == "Get tasks test" for t in data)

def test_get_tasks_filter_by_status():
    client.post("/tasks", json={"title": "Filter test", "status": "in_progress"})
    response = client.get("/tasks?status=in_progress")
    assert response.status_code == 200
    data = response.json()
    assert all(t["status"] == "in_progress" for t in data)
```

**Step 2: Run tests — verify they fail**

```bash
pytest tests/test_main.py::test_get_tasks_returns_list tests/test_main.py::test_get_tasks_filter_by_status -v
```

Expected: FAIL — route not defined.

**Step 3: Add GET route to `main.py`**

```python
from typing import Optional

@app.get("/tasks", response_model=list[TaskOut])
def get_tasks(status: Optional[VALID_STATUSES] = None):
    with get_db() as conn:
        if status:
            rows = conn.execute(
                "SELECT id, title, status, created_at FROM tasks WHERE status = ? ORDER BY created_at DESC",
                (status,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT id, title, status, created_at FROM tasks ORDER BY created_at DESC"
            ).fetchall()
    return [dict(r) for r in rows]
```

**Step 4: Run all tests — verify they pass**

```bash
pytest tests/ -v
```

Expected: all PASS.

**Step 5: Manual smoke test**

```bash
uvicorn main:app --reload
# In another terminal:
curl -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d '{"title":"Hello TaskKeeper"}'
curl http://localhost:8000/tasks
```

Expected: task created, returned in GET response.

**Step 6: Commit**

```bash
git add main.py tests/test_main.py
git commit -m "feat: add GET /tasks endpoint with optional status filter"
```

---

## Task 4: Serve the frontend

**Files:**
- Modify: `main.py`
- Create: `index.html`

**Step 1: Add static file serving to `main.py`**

Add this import at the top:
```python
from fastapi.responses import FileResponse
```

Add this route (before other routes):
```python
@app.get("/", response_class=FileResponse)
def serve_frontend():
    return FileResponse("index.html")
```

**Step 2: Create `index.html` — layout first, no JS yet**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>TaskKeeper</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: system-ui, sans-serif; background: #f5f5f5; padding: 24px; }
    h1 { font-size: 1.5rem; margin-bottom: 24px; }
    .board { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
    .column { background: #fff; border-radius: 8px; padding: 16px; min-height: 200px; }
    .column h2 { font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.05em; color: #666; margin-bottom: 12px; }
    .task-card { background: #f9f9f9; border: 1px solid #e5e5e5; border-radius: 6px; padding: 10px 12px; margin-bottom: 8px; font-size: 0.9rem; }
    .add-form { display: flex; gap: 8px; margin-bottom: 24px; }
    .add-form input { flex: 1; padding: 8px 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 0.9rem; }
    .add-form button { padding: 8px 16px; background: #2563eb; color: #fff; border: none; border-radius: 6px; cursor: pointer; font-size: 0.9rem; }
    .add-form button:hover { background: #1d4ed8; }
  </style>
</head>
<body>
  <h1>TaskKeeper</h1>
  <form class="add-form" id="add-form">
    <input type="text" id="task-title" placeholder="New task..." required />
    <button type="submit">Add Task</button>
  </form>
  <div class="board">
    <div class="column">
      <h2>To Do</h2>
      <div id="col-todo"></div>
    </div>
    <div class="column">
      <h2>In Progress</h2>
      <div id="col-in_progress"></div>
    </div>
    <div class="column">
      <h2>Done</h2>
      <div id="col-done"></div>
    </div>
  </div>
  <script>
    const API = 'http://localhost:8000';

    async function loadTasks() {
      const res = await fetch(`${API}/tasks`);
      const tasks = await res.json();
      ['todo', 'in_progress', 'done'].forEach(status => {
        const col = document.getElementById(`col-${status}`);
        col.innerHTML = tasks
          .filter(t => t.status === status)
          .map(t => `<div class="task-card">${t.title}</div>`)
          .join('');
      });
    }

    document.getElementById('add-form').addEventListener('submit', async (e) => {
      e.preventDefault();
      const title = document.getElementById('task-title').value.trim();
      if (!title) return;
      await fetch(`${API}/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title }),
      });
      document.getElementById('task-title').value = '';
      await loadTasks();
    });

    loadTasks();
  </script>
</body>
</html>
```

**Step 3: Run the app and verify end-to-end**

```bash
uvicorn main:app --reload
```

Open http://localhost:8000 — you should see the Kanban board. Type a task name, hit "Add Task", see it appear in the "To Do" column. Refresh the page — task should still be there (persisted in SQLite).

**Step 4: Commit**

```bash
git add main.py index.html
git commit -m "feat: add Kanban frontend — create tasks and view on board"
```

---

## Done Criteria

- [ ] `pytest tests/ -v` — all tests pass
- [ ] `uvicorn main:app --reload` — server starts without errors
- [ ] Open http://localhost:8000 — Kanban board renders
- [ ] Type a task name → "Add Task" → task appears in "To Do" column
- [ ] Refresh the page → task is still there (SQLite persisted)
- [ ] http://localhost:8000/docs — Swagger UI shows both endpoints

---

## Next Steps (Phase 2)

Once this slice is working:
1. Add `priority` (low/medium/high), `description`, `due_date` columns to the schema
2. Add `PATCH /tasks/{id}` to update status (move between columns)
3. Add `DELETE /tasks/{id}` (soft-delete via `deleted` flag)
4. Build trash view
5. Add task cards with full field display
