# Roadmap — TaskKeeper v1

## Milestone 1: Working Personal Task Tracker

---

### Phase 1: Backend Foundation
**Goal:** A working FastAPI + SQLite backend that fully handles task CRUD, status transitions, soft-delete, and restore via a tested REST API.
**Mode:** mvp
**Success Criteria:**
1. `POST /tasks` creates a task and returns it with all fields populated
2. `GET /tasks` returns tasks filtered by status and deleted state
3. `PUT /tasks/{id}` updates any task field; returns the updated task
4. `DELETE /tasks/{id}` soft-deletes (sets deleted=true); task no longer appears in default GET
5. `POST /tasks/{id}/restore` restores a deleted task to its prior status
6. `DELETE /tasks/{id}/permanent` hard-deletes from DB; gone from all endpoints
7. SQLite file is created automatically on first run; data survives server restart
8. `/docs` returns the FastAPI OpenAPI UI

**Plans:**

**Wave 1**
- [x] 01-01 — Database schema, Pydantic validation, and update endpoint

**Wave 2 *(blocked on Wave 1 completion)***
- [x] 01-02 — Soft delete, restore, permanent delete, and query parameter filtering


---

### Phase 2: Kanban Frontend
**Goal:** A single-page HTML/JS Kanban board that renders tasks from the API in three columns and supports creating, editing, and completing tasks without page reloads.
**Mode:** mvp
**Success Criteria:**
1. Page loads and renders tasks from `GET /tasks` in the correct column (To Do / In Progress / Done)
2. User can add a new task via an inline or modal form; it appears in the board immediately
3. User can click a task card to open an edit modal showing all fields; saving calls `PUT /tasks/{id}`
4. User can change a task's status (moves it to the correct column)
5. Task cards display title, priority badge, and due date
6. No page reloads — all interactions use `fetch`

**Plans:**
- [x] 2.1 — Static HTML shell + CSS (board layout, three columns, responsive)
- [x] 2.2 — API client module (fetch wrapper for all task endpoints)
- [x] 2.3 — Task card component and board render logic
- [x] 2.4 — Add task form (inline or modal, column-aware)
- [x] 2.5 — Edit task modal (all fields, save/cancel)
- [x] 2.6 — Status change controls on cards

---

### Phase 3: Soft-Delete & Trash View
**Goal:** Users can soft-delete tasks from the board and manage them in a dedicated Trash view with restore and permanent-delete actions.
**Mode:** mvp
**Success Criteria:**
1. Delete button on a task card calls `DELETE /tasks/{id}` (soft); card disappears from board immediately
2. Trash view (accessible from main board) lists all soft-deleted tasks
3. Restore button calls `POST /tasks/{id}/restore`; task reappears in the correct column
4. Permanent delete button calls `DELETE /tasks/{id}/permanent`; task disappears from Trash
5. Trash view is empty state when no deleted tasks exist

**Plans:**
- [x] 3.1 — Delete button and soft-delete wiring on task cards
- [x] 3.2 — Trash view page/section (layout, task list, empty state)
- [x] 3.3 — Restore and permanent-delete actions in Trash view
- [x] 3.4 — Navigation between board and Trash view

---

### Phase 4: Polish & Local Dev Experience
**Goal:** The app is pleasant to use locally — startup is simple, the UI is clean and responsive, and there are no rough edges.
**Mode:** mvp
**Success Criteria:**
1. Single command starts the server (`uvicorn main:app --reload`)
2. README has exact steps to clone, install deps, and run
3. Priority badges are visually distinct (color-coded)
4. Due dates show overdue indicator if past today
5. Empty column states are handled gracefully (friendly message)
6. No JS errors in browser console during normal use

**Plans:**
- [x] 4.1 — UI polish (priority badge colors, due date overdue highlight, empty states)
- [x] 4.2 — README setup instructions and local dev notes
- [x] 4.3 — Final smoke test (full user flow from create to trash to restore to permanent delete)
