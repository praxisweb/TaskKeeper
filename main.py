import os
import sqlite3
from contextlib import asynccontextmanager, contextmanager
from pathlib import Path
from typing import Literal

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel, field_validator

BASE_DIR = Path(__file__).parent
DB_PATH = os.getenv("DB_PATH", str(BASE_DIR / "tasks.db"))

VALID_STATUSES = Literal["todo", "in_progress", "done"]


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                title      TEXT NOT NULL,
                status     TEXT NOT NULL DEFAULT 'todo'
                           CHECK(status IN ('todo', 'in_progress', 'done')),
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


@app.get("/tasks", response_model=list[TaskOut])
def get_tasks(status: VALID_STATUSES | None = None):
    with get_db() as conn:
        if status:
            rows = conn.execute(
                "SELECT id, title, status, created_at FROM tasks WHERE status = ? ORDER BY created_at ASC",
                (status,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT id, title, status, created_at FROM tasks ORDER BY created_at ASC"
            ).fetchall()
    return [dict(r) for r in rows]


@app.get("/", response_class=FileResponse)
def serve_frontend():
    # Absolute path — works regardless of where uvicorn is invoked from
    return FileResponse(BASE_DIR / "index.html")



