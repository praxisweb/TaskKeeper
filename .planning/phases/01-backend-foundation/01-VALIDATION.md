---
phase: 1
slug: backend-foundation
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-06-07
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.x |
| **Config file** | none |
| **Quick run command** | `cmd.exe /c "set PYTHONPATH=c:\Users\jason\Documents\Code\TaskKeeper && python -m pytest c:\Users\jason\Documents\Code\TaskKeeper\tests\test_main.py -v -p no:cacheprovider"` |
| **Full suite command** | `cmd.exe /c "set PYTHONPATH=c:\Users\jason\Documents\Code\TaskKeeper && python -m pytest c:\Users\jason\Documents\Code\TaskKeeper\tests\test_main.py -v -p no:cacheprovider"` |
| **Estimated runtime** | ~1 second |

---

## Sampling Rate

- **After every task commit:** Run the quick run command
- **After every plan wave:** Run the full suite command
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 2 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 01-01-01 | 01 | 1 | PERSIST-02 | — | Schema updates tables automatically on start | unit | `cmd.exe /c "set PYTHONPATH=c:\Users\jason\Documents\Code\TaskKeeper && python -m pytest c:\Users\jason\Documents\Code\TaskKeeper\tests\test_main.py -k test_db_migration -v -p no:cacheprovider"` | ✅ | ⬜ pending |
| 01-01-02 | 01 | 1 | TASK-01, API-03 | — | Validation rejects invalid due_date formats and invalid priorities | unit | `cmd.exe /c "set PYTHONPATH=c:\Users\jason\Documents\Code\TaskKeeper && python -m pytest c:\Users\jason\Documents\Code\TaskKeeper\tests\test_main.py -k test_pydantic_validation -v -p no:cacheprovider"` | ✅ | ⬜ pending |
| 01-01-03 | 01 | 1 | TASK-02, API-01 | — | PUT /tasks/{id} updates title, status, description, priority, due_date | integration | `cmd.exe /c "set PYTHONPATH=c:\Users\jason\Documents\Code\TaskKeeper && python -m pytest c:\Users\jason\Documents\Code\TaskKeeper\tests\test_main.py -k test_put_task -v -p no:cacheprovider"` | ✅ | ⬜ pending |
| 01-02-01 | 02 | 2 | TASK-05, TASK-07 | — | DELETE /tasks/{id} soft-deletes and POST /tasks/{id}/restore restores task | integration | `cmd.exe /c "set PYTHONPATH=c:\Users\jason\Documents\Code\TaskKeeper && python -m pytest c:\Users\jason\Documents\Code\TaskKeeper\tests\test_main.py -k test_soft_delete -v -p no:cacheprovider"` | ✅ | ⬜ pending |
| 01-02-02 | 02 | 2 | TASK-08 | — | DELETE /tasks/{id}/permanent removes record from DB | integration | `cmd.exe /c "set PYTHONPATH=c:\Users\jason\Documents\Code\TaskKeeper && python -m pytest c:\Users\jason\Documents\Code\TaskKeeper\tests\test_main.py -k test_permanent_delete -v -p no:cacheprovider"` | ✅ | ⬜ pending |
| 01-02-03 | 02 | 2 | API-02 | — | GET /tasks handles deleted and status query parameters correctly | integration | `cmd.exe /c "set PYTHONPATH=c:\Users\jason\Documents\Code\TaskKeeper && python -m pytest c:\Users\jason\Documents\Code\TaskKeeper\tests\test_main.py -k test_get_tasks_filters -v -p no:cacheprovider"` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- Existing infrastructure covers all phase requirements.

---

## Manual-Only Verifications

All phase behaviors have automated verification.

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 2s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
