# Pattern Index

Lookup table for all pattern files in this directory. Check here before starting any task — if a pattern exists, follow it.

<!-- This file is populated during setup (Pass 2) and updated whenever patterns are added.
     Each row maps a pattern file (or section) to its trigger — when should the agent load it?

     Format — simple (one task per file):
     | [filename.md](filename.md) | One-line description of when to use this pattern |

     Format — anchored (multi-section file, one row per task):
     | [filename.md#task-first-task](filename.md#task-first-task) | When doing the first task |
     | [filename.md#task-second-task](filename.md#task-second-task) | When doing the second task |

     Example (from a Flask API project):
     | [add-api-client.md](add-api-client.md) | Adding a new external service integration |
     | [debug-pipeline.md](debug-pipeline.md) | Diagnosing failures in the request pipeline |
     | [crud-operations.md#task-add-endpoint](crud-operations.md#task-add-endpoint) | Adding a new API route with validation |
     | [crud-operations.md#task-add-model](crud-operations.md#task-add-model) | Adding a new database model |

     Keep this table sorted alphabetically. One row per task (not per file).
     If you create a new pattern, add it here. If you delete one, remove it. -->

| Pattern | Use when |
|---------|----------|
| [add-endpoint.md](add-endpoint.md) | Adding a new FastAPI route — full router → service → repository vertical slice |
| [add-task-field.md](add-task-field.md) | Adding a new column/field to the Task model across all layers (DB, schemas, API, frontend) |
| [debug-api.md#task-debug-http-422-unprocessable-entity](debug-api.md#task-debug-http-422-unprocessable-entity) | Getting a 422 response — Pydantic validation failure |
| [debug-api.md#task-debug-http-500-internal-server-error](debug-api.md#task-debug-http-500-internal-server-error) | Getting a 500 — Python exception in the request pipeline |
| [debug-api.md#task-debug-frontend-fetch-failures](debug-api.md#task-debug-frontend-fetch-failures) | Frontend fetch calls failing or returning unexpected results |
| [debug-api.md#task-debug-sqlalchemy--database-errors](debug-api.md#task-debug-sqlalchemy--database-errors) | SQLAlchemy / database errors (missing table, missing column, integrity) |
