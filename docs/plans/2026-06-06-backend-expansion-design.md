# Design: Complete Backend Foundation (Phase 1 Expansion)

## Goal
Extend the database schema and implement the remaining backend endpoints (PUT update, DELETE soft-delete, POST restore, DELETE permanent-delete) with full test coverage and robust migration-less column detection.

## Architecture & Data Schema
We will continue using `sqlite3` without an ORM or migration framework. 

### SQLite Database Table: `tasks`
* `id` INTEGER PRIMARY KEY AUTOINCREMENT
* `title` TEXT NOT NULL
* `status` TEXT NOT NULL DEFAULT 'todo' CHECK(status IN ('todo', 'in_progress', 'done'))
* `created_at` TEXT NOT NULL DEFAULT (datetime('now'))
* `description` TEXT
* `priority` TEXT NOT NULL DEFAULT 'medium' CHECK(priority IN ('low', 'medium', 'high'))
* `due_date` TEXT
* `deleted` INTEGER NOT NULL DEFAULT 0 CHECK(deleted IN (0, 1))

### Schema Initialization & Migrations
On startup, `init_db()` will run. It will execute `CREATE TABLE IF NOT EXISTS`. To handle backward compatibility for existing `tasks.db` files that do not have the newly introduced columns, `init_db()` will dynamically check the table columns using `PRAGMA table_info(tasks)` and execute `ALTER TABLE tasks ADD COLUMN ...` statements as necessary.

---

## API Design

### Schemas
* **`TaskIn`**
  * `title`: str (non-blank check)
  * `status`: Literal["todo", "in_progress", "done"] = "todo"
  * `description`: str | None = None
  * `priority`: Literal["low", "medium", "high"] = "medium"
  * `due_date`: str | None = None (validated using Regex for `YYYY-MM-DD` if provided)
* **`TaskOut`**
  * Represents all fields retrieved, with `deleted` mapped to a boolean value.

### Endpoints
* **`GET /tasks`**
  * Query parameters:
    * `status`: Literal["todo", "in_progress", "done"] | None = None
    * `deleted`: bool = False
  * Query logic:
    * Filters by status if provided.
    * Filters by `deleted` (0 if False, 1 if True) to keep active tasks and soft-deleted tasks separated.
* **`PUT /tasks/{id}`**
  * Request body: `TaskIn`
  * Action: Updates all editable fields of the task matching `id`.
  * Returns: 200 + `TaskOut` (or 404 if not found).
* **`DELETE /tasks/{id}`**
  * Action: Soft-deletes a task by setting `deleted = 1`.
  * Returns: 200 + `TaskOut` (or 404 if not found).
* **`POST /tasks/{id}/restore`**
  * Action: Restores a soft-deleted task by setting `deleted = 0`.
  * Returns: 200 + `TaskOut` (or 404 if not found).
* **`DELETE /tasks/{id}/permanent`**
  * Action: Hard-deletes the task from the database.
  * Returns: 200 + `{"detail": "Task permanently deleted"}` (or 404 if not found).

---

## Testing Plan
- DB migrations check: verify that starting the app with an existing schema safely adds the missing columns without data loss.
- Endpoint validation:
  - `PUT /tasks/{id}` validation errors, happy path, 404.
  - `DELETE /tasks/{id}` status changes to deleted, tasks no longer appear in standard `GET /tasks` output.
  - `POST /tasks/{id}/restore` returns task to active status.
  - `DELETE /tasks/{id}/permanent` removes the row completely.
