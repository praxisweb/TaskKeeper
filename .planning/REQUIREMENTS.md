# Requirements — TaskKeeper v1

## v1 Requirements

### Tasks — Core CRUD
- [ ] **TASK-01**: User can create a task with a title (required), optional description, optional due date, and priority (low / medium / high, default low)
- [ ] **TASK-02**: User can edit the title, description, due date, and priority of an existing task
- [ ] **TASK-03**: User can mark a task complete (status transitions to Done)
- [ ] **TASK-04**: User can move a task between To Do, In Progress, and Done via drag-and-drop or status change

### Tasks — Soft Delete & Trash
- [ ] **TASK-05**: User can soft-delete a task from the main board (it disappears from the Kanban view but is not destroyed)
- [ ] **TASK-06**: User can navigate to a Trash view that lists all soft-deleted tasks
- [ ] **TASK-07**: User can restore a soft-deleted task back to its pre-deletion status column
- [ ] **TASK-08**: User can permanently delete a task from the Trash view (irreversible)

### API
- [ ] **API-01**: REST API exposes endpoints: `POST /tasks`, `GET /tasks`, `GET /tasks/{id}`, `PUT /tasks/{id}`, `DELETE /tasks/{id}` (soft), `POST /tasks/{id}/restore`, `DELETE /tasks/{id}/permanent`
- [ ] **API-02**: `GET /tasks` supports query params: `status` filter (todo / in_progress / done) and `deleted` flag (true/false)
- [ ] **API-03**: API returns well-formed JSON with consistent error responses (4xx with `detail` field via FastAPI defaults)
- [ ] **API-04**: FastAPI auto-generates OpenAPI docs at `/docs`

### Frontend — Kanban Board
- [ ] **UI-01**: Kanban board renders three columns: To Do, In Progress, Done
- [ ] **UI-02**: Task cards display title, priority badge, and due date
- [ ] **UI-03**: User can add a new task from an inline form or floating button — choosing the initial column
- [ ] **UI-04**: User can open a task detail modal/panel to view and edit all fields
- [ ] **UI-05**: Trash view is accessible from the main board (e.g., nav link or button)
- [ ] **UI-06**: Frontend communicates with the API via `fetch` — no page reloads

### Persistence
- [ ] **PERSIST-01**: All task data is persisted in an SQLite file on disk and survives server restarts
- [ ] **PERSIST-02**: Database schema is created automatically on first run (no manual migration step required)

---

## v2 Requirements (Deferred)

- Tags / category labels on tasks
- Sorting and filtering on the Kanban board (by priority, due date)
- Drag-and-drop reordering within a column
- Due-date overdue highlighting
- Keyboard shortcuts

---

## Out of Scope

- Authentication or user accounts — single user, no login
- Multi-user or real-time collaboration — not needed
- Cloud sync or hosted database — intentionally local-only
- Email or push notifications — out of scope for v1
- Recurring tasks or task dependencies — complexity not warranted yet
- Mobile-native app — web only
- Tags / labels — deferred to v2

---

## Traceability

| Requirement | Phase |
|-------------|-------|
| TASK-01 – TASK-04, API-01 – API-04, PERSIST-01 – PERSIST-02 | Phase 1 |
| UI-01 – UI-06 | Phase 2 |
| TASK-05 – TASK-08, UI-05 | Phase 3 |
