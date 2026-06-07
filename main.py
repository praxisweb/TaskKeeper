import os
import re
import sqlite3
from contextlib import asynccontextmanager, contextmanager
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, field_validator

BASE_DIR = Path(__file__).parent
DB_PATH = os.getenv("DB_PATH", str(BASE_DIR / "tasks.db"))

VALID_STATUSES = Literal["todo", "in_progress", "done"]


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
            conn.execute("ALTER TABLE tasks ADD COLUMN priority TEXT NOT NULL DEFAULT 'medium'")
        if "due_date" not in columns:
            conn.execute("ALTER TABLE tasks ADD COLUMN due_date TEXT")
        if "deleted" not in columns:
            conn.execute("ALTER TABLE tasks ADD COLUMN deleted INTEGER NOT NULL DEFAULT 0")
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


@app.delete("/tasks/{task_id}/permanent")
def permanent_delete_task(task_id: int):
    with get_db() as conn:
        existing = conn.execute("SELECT id FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Task not found")
        
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
    return {"detail": "Task permanently deleted"}


@app.get("/", response_class=FileResponse)
def serve_frontend():
    # Absolute path — works regardless of where uvicorn is invoked from
    return FileResponse(BASE_DIR / "index.html")



