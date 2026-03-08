# Phase-0 Backlog Alignment

This file maps source backlog documents into the active plan and current ledger tasks.

## Source Documents

Original documents:
- `specs/ontoForge_90_Implementation-plane_backlog.md`
- `specs/ontoForge_91_Build-Readiness Backlog v0.1.md`

Converted archive copies:
- `bootstrap/plans/archive/ontoForge_90_Implementation-plane_backlog.v0.1.md`
- `bootstrap/plans/archive/ontoForge_91_Build-Readiness_Backlog.v0.1.md`

## Mapping

| Backlog Work Item | Plan Item | Task Ledger ID | Status |
| --- | --- | --- | --- |
| BR-00.1 Repo skeleton and CI substrate | P1-001 | BPL-00.1 | DONE |
| BR-01.1 Identity/cid spec | P1-002 | TASK-01.1 | DONE |
| BR-01.2 cid implementation and tests | P1-002 | TASK-01.2 | DONE |
| BR-02.1 Ledger API/order spec | P1-003 | TASK-02.1 | DONE |
| BR-02.2 Ledger implementation and replay | P1-003 | TASK-02.2 | DONE |
| BR-03.1 IssuerProof spec | P1-004 | TASK-03.1 | COMPLETED |
| BR-03.2 IssuerProof verifier/tests | P1-004 | TASK-03.2 | DONE |
| BR-04.1 Evaluator boundary spec | P1-005 | TASK-04.1 | COMPLETED |
| BR-04.2 Commit-boundary enforcement implementation | P1-005 | TASK-04.2 | DONE |
| BR-05.1 Manifest schemas and fixtures | P1-006 | TASK-05.1 | DONE |
| BR-05.2 Packager implementation | P1-006 | TASK-05.2 | DONE |
| BR-05.3 Loader/verifier tamper rejection | P1-006 | TASK-05.3 | DONE |
| BR-06.1 SupportOntologyRelease artifact | P1-007 | TASK-06.1 | DONE |
| BR-06.2 SCR_TBox_Release artifact | P1-007 | TASK-06.2 | DONE |
| BR-07.1 Phase-0 evidence gate report | P1-008 | BPL-07.1 | DONE |

## Notes

- This alignment preserves traceability from the original backlog docs to active plan control points.
- Any new work derived from these source docs must be entered via `bootstrap/plans/phase1_plan_items.csv` and mapped in `bootstrap/task_ledger.csv`.

