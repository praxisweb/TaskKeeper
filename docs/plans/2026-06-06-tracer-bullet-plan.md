# TaskKeeper v0.1 — Tracer Bullet Implementation Plan (rev 2)

> **For Antigravity:** REQUIRED WORKFLOW: Use `.agent/workflows/execute-plan.md` to execute this plan in single-flow mode.

**Goal:** Build one working vertical slice — create a task via a form, persist it in SQLite, and render all tasks on a Kanban board.

**Architecture:** Flat three-file layout: `main.py` (FastAPI app + DB + routes), `tasks.db` (SQLite, auto-created), `index.html` (vanilla JS SPA). No auth, no migrations tool, no build step.

**Tech Stack:** Python 3.11+, FastAPI, uvicorn, SQLite (stdlib `sqlite3`), Pydantic v2, vanilla HTML/CSS/JS

**Changes from rev 1 (CEO review fixes):**
- Test isolation: in-memory SQLite via `conftest.py` (prevents flaky tests from shared state)
- Empty title validation: `field_validator` on `TaskIn` rejects blank strings
- Frontend uses relative URLs: no hardcoded `http://localhost:8000`
- Lifespan pattern replaces deprecated `@app.on_event("startup")`
- Added missing 422 tests: empty title, invalid status on GET

---

## Task 1: Project Bootstrap

**Files:**
- Create: `requirements.txt`
- Create: `main.py`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`

**Step 1: Write `requirements.txt`**

```
fastapi>=0.111.0
uvicorn[standard]>=0.29.0
httpx>=0.27.0
pytest>=8.0.0
```

> `httpx` is required by FastAPI's `TestClient`. Add it explicitly so installs don't break.

**Step 2: Install dependencies**

```bash
pip install -r requirements.txt
```

Expected: packages install without errors.

**Step 3: Create test isolation fixture**

Create `tests/__init__.py` (empty file).

Create `tests/conftest.py`:

```python
import os
import pytest

# Must be set before importing main so DB_PATH is resolved at module load
os.environ["DB_PATH"] = ":memory:"

from fastapi.testclient import TestClient
from main import app, init_db


@pytest.fixture(autouse=True)
def fresh_db():
    """Give every test a clean in-memory database."""
    init_db()
    yield


@pytest.fixture
def client():
    return TestClient(app)
```

> `autouse=True` means every test gets a fresh DB without having to request the fixture.
> In-memory SQLite is isolated per-connection, so state never bleeds between tests.

**Step 4: Write the failing smoke test**

Create `tests/test_main.py`:

```python
def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

**Step 5: Run test — verify it fails**

```bash
pytest tests/test_main.py::test_health -v
```

Expected: FAIL — `main` module not found.

**Step 6: Write `main.py`**

```python
import os
import sqlite3
from contextlib import asynccontextmanager, contextmanager
from typing import Literal, Optional

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel, field_validator

DB_PATH = os.getenv("DB_PATH", "tasks.db")

VALID_STATUSES = Literal["todo", "in_progress", "done"]


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


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="TaskKeeper", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok"}
```

**Step 7: Run test — verify it passes**

```bash
pytest tests/test_main.py::test_health -v
```

Expected: PASS.

**Step 8: Commit**

```bash
git add requirements.txt main.py tests/__init__.py tests/conftest.py tests/test_main.py
git commit -m "feat: bootstrap FastAPI app with health endpoint, SQLite init, and test isolation"
```

---

## Task 2: POST /tasks endpoint

**Files:**
- Modify: `main.py`
- Modify: `tests/test_main.py`

**Step 1: Write the failing tests**

Add to `tests/test_main.py`:

```python
def test_create_task_returns_201(client):
    response = client.post("/tasks", json={"title": "Buy milk"})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Buy milk"
    assert data["status"] == "todo"
    assert "id" in data
    assert "created_at" in data


def test_create_task_custom_status(client):
    response = client.post("/tasks", json={"title": "Doing this", "status": "in_progress"})
    assert response.status_code == 201
    assert response.json()["status"] == "in_progress"


def test_create_task_rejects_missing_title(client):
    response = client.post("/tasks", json={})
    assert response.status_code == 422


def test_create_task_rejects_empty_title(client):
    response = client.post("/tasks", json={"title": ""})
    assert response.status_code == 422


def test_create_task_rejects_blank_title(client):
    response = client.post("/tasks", json={"title": "   "})
    assert response.status_code == 422


def test_create_task_rejects_invalid_status(client):
    response = client.post("/tasks", json={"title": "X", "status": "flying"})
    assert response.status_code == 422
```

**Step 2: Run tests — verify they fail**

```bash
pytest tests/test_main.py -v
```

Expected: 6 new tests fail — route not defined.

**Step 3: Add Pydantic models and POST route to `main.py`**

Add after the `health` route:

```python
class TaskIn(BaseModel):
    title: str
    status: VALID_STATUSES = "todo"

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("title cannot be blank")
        return v.strip()


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
git commit -m "feat: add POST /tasks with Pydantic validation and blank title guard"
```

---

## Task 3: GET /tasks endpoint

**Files:**
- Modify: `main.py`
- Modify: `tests/test_main.py`

**Step 1: Write the failing tests**

Add to `tests/test_main.py`:

```python
def test_get_tasks_empty(client):
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_get_tasks_returns_created_task(client):
    client.post("/tasks", json={"title": "My task"})
    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "My task"


def test_get_tasks_filter_by_status(client):
    client.post("/tasks", json={"title": "Todo task", "status": "todo"})
    client.post("/tasks", json={"title": "Active task", "status": "in_progress"})
    response = client.get("/tasks?status=in_progress")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Active task"


def test_get_tasks_rejects_invalid_status(client):
    response = client.get("/tasks?status=flying")
    assert response.status_code == 422
```

**Step 2: Run tests — verify they fail**

```bash
pytest tests/test_main.py -k "test_get_tasks" -v
```

Expected: 4 tests fail — route not defined.

**Step 3: Add GET route to `main.py`**

```python
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
```

In another terminal:

```bash
curl -s -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d '{"title":"Hello TaskKeeper"}' | python -m json.tool
curl -s http://localhost:8000/tasks | python -m json.tool
```

Expected: task created with id/title/status/created_at, returned in GET response.

**Step 6: Commit**

```bash
git add main.py tests/test_main.py
git commit -m "feat: add GET /tasks with optional status filter and validation"
```

---

## Task 4: Serve the frontend

**Files:**
- Modify: `main.py`
- Create: `index.html`

**Step 1: Add frontend route to `main.py`**

Add this route (before other routes, so `/` doesn't shadow anything):

```python
@app.get("/", response_class=FileResponse)
def serve_frontend():
    return FileResponse("index.html")
```

**Step 2: Write the test**

Add to `tests/test_main.py`:

```python
def test_frontend_route_exists(client, tmp_path, monkeypatch):
    # Create a minimal index.html so FileResponse doesn't 404
    index = tmp_path / "index.html"
    index.write_text("<html><body>ok</body></html>")
    monkeypatch.chdir(tmp_path)
    response = client.get("/")
    assert response.status_code == 200
```

Run:

```bash
pytest tests/test_main.py::test_frontend_route_exists -v
```

Expected: PASS.

**Step 3: Create `index.html`**

Note: `const API = ''` — relative URL, same origin. No hardcoded port.

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
    .error { color: #dc2626; font-size: 0.85rem; margin-top: 8px; }
  </style>
</head>
<body>
  <h1>TaskKeeper</h1>
  <form class="add-form" id="add-form">
    <input type="text" id="task-title" placeholder="New task..." required />
    <button type="submit">Add Task</button>
  </form>
  <p class="error" id="error-msg" style="display:none"></p>
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
    const API = '';  // same origin — no hardcoded port

    function showError(msg) {
      const el = document.getElementById('error-msg');
      el.textContent = msg;
      el.style.display = 'block';
    }

    function clearError() {
      document.getElementById('error-msg').style.display = 'none';
    }

    async function loadTasks() {
      try {
        const res = await fetch(`${API}/tasks`);
        if (!res.ok) throw new Error(`Server error: ${res.status}`);
        const tasks = await res.json();
        clearError();
        ['todo', 'in_progress', 'done'].forEach(status => {
          const col = document.getElementById(`col-${status}`);
          const filtered = tasks.filter(t => t.status === status);
          col.innerHTML = filtered.length
            ? filtered.map(t => `<div class="task-card">${t.title}</div>`).join('')
            : '<p style="color:#aaa;font-size:0.85rem">No tasks</p>';
        });
      } catch (err) {
        showError(`Could not load tasks: ${err.message}`);
      }
    }

    document.getElementById('add-form').addEventListener('submit', async (e) => {
      e.preventDefault();
      const title = document.getElementById('task-title').value.trim();
      if (!title) return;
      try {
        const res = await fetch(`${API}/tasks`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ title }),
        });
        if (!res.ok) throw new Error(`Server error: ${res.status}`);
        document.getElementById('task-title').value = '';
        clearError();
        await loadTasks();
      } catch (err) {
        showError(`Could not add task: ${err.message}`);
      }
    });

    loadTasks();
  </script>
</body>
</html>
```

**Step 4: Run the full test suite**

```bash
pytest tests/ -v
```

Expected: all PASS.

**Step 5: End-to-end manual verification**

```bash
uvicorn main:app --reload
```

Open http://localhost:8000.

- [ ] Kanban board renders with three columns
- [ ] "No tasks" placeholder shows in each empty column
- [ ] Type a task name → "Add Task" → task appears in "To Do"
- [ ] Refresh the page → task is still there (SQLite persisted)
- [ ] Open http://localhost:8000/docs → both endpoints visible
- [ ] Stop the server → reload the page → error message appears (not a blank board)

**Step 6: Commit**

```bash
git add main.py index.html tests/test_main.py
git commit -m "feat: serve Kanban frontend with error handling and relative API URLs"
```

---

## Done Criteria

- [ ] `pytest tests/ -v` — all tests pass with zero warnings
- [ ] `uvicorn main:app --reload` — starts without deprecation warnings
- [ ] http://localhost:8000 — board renders, tasks persist across refresh
- [ ] Blank title → "Add Task" → no task created (form requires input)
- [ ] Stop server → reload → error message shown, not blank board
- [ ] http://localhost:8000/docs — both endpoints visible

---

## Next Steps (Phase 2)

Once this slice is working:
1. Add `priority` (low/medium/high), `description`, `due_date` columns to the schema
2. Add `PATCH /tasks/{id}` to update status (move between columns)
3. Add `DELETE /tasks/{id}` (soft-delete via `deleted` flag)
4. Build trash view
5. Add task cards with full field display
