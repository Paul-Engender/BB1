# Spec Contract Validation Matrix v1

Status: IS
Owner: paul
Plan Item: P1-009
Task: TASK-09.3
Date: 2026-03-06

## Purpose

Provide machine-executable validation mappings from spec contract clauses/deltas to enforcement commands and evidence artifacts.
This matrix operationalizes the migration controls defined in the canonical baseline and delta register.

## Source Inputs

- `specs/spec_upgrade/canonical_spec_set_v1.md`
- `specs/spec_upgrade/migration_delta_register_v1.md`
- `bootstrap/task_ledger.csv`
- `bootstrap/artifact_registry.csv`
- `bootstrap/evidence_register.csv`
- `tools/bootstrap_validate.py`
- `tools/bootstrap_snapshot.py`

## Validation Matrix

| Matrix ID | Contract / Delta | Verification Command | Expected Result | Evidence Artifact(s) | Evidence Row |
| --- | --- | --- | --- | --- | --- |
| M-001 | D-001 ID mapping BR -> TASK/BPL maintained | `python tools/bootstrap_validate.py --execute-validation-methods dry-run` | Validator passes; mapped IDs remain valid in ledgers | `bootstrap/plans/phase0_backlog_alignment.md`, `bootstrap/task_ledger.csv` | EP-09 |
| M-002 | D-002 Canonical refs/evidence links present for TASK rows | `python tools/bootstrap_validate.py` | No missing/invalid `evidence_row_ids` for `TASK-*` rows | `bootstrap/task_ledger.csv` | EP-09 |
| M-003 | D-003 IS vs OUGHT closeout discipline | `python tools/bootstrap_validate.py` | No `DONE` task marked with OUGHT note state | `bootstrap/task_ledger.csv` | EP-09 |
| M-004 | D-004 Executable validation methods required | `python tools/bootstrap_validate.py --execute-validation-methods strict` | All `DONE TASK-*` validation methods execute successfully | `bootstrap/task_ledger.csv`, validator run output | EP-09 |
| M-005 | D-005 Decomposition hardening (atomic naming/deps/output count) | `python tools/bootstrap_validate.py` | No mixed-intent task-name error; dependency and output rules pass | `bootstrap/task_ledger.csv` | EP-09 |
| M-006 | D-006 Phase gate scoping preserved | `python tools/bootstrap_validate.py --require-phase0-closed --execute-validation-methods strict` | Phase-0 remains CLOSED with EP-01..EP-05 VERIFIED even while EP-09 is TO_DO | `bootstrap/evidence_register.csv`, validator run output | EP-09 |
| M-007 | D-007 Hash-bound artifacts for DONE tasks | `python tools/bootstrap_validate.py` | Every DONE task has hash-valid artifact rows (or explicitly justified warnings eliminated) | `bootstrap/artifact_registry.csv` | EP-09 |
| M-008 | D-008 Multi-phase evidence support (new rows without phase-0 regression) | `python tools/bootstrap_snapshot.py` | Snapshot reflects EP-09 as TO_DO while phase-0 gate remains CLOSED | `bootstrap/reports/daily_state_snapshot.md` | EP-09 |

## Execution Rule Set

1. Commands in this matrix are normative for migration-wave validation.
2. Any new migration task must declare at least one matrix row it satisfies.
3. A matrix row is considered proven only when command output and artifact hash are recorded.

## Hand-off to TASK-09.4

Inputs provided:
- This matrix.
- Canonical baseline and delta register.

Expected output from TASK-09.4:
- `specs/spec_upgrade/pilot_migration_report_v1.md` demonstrating one migration slice executed against matrix controls.
