# Plan Index

This file is the single orientation point for planning artifacts.

## Canonical Source Rule

- Governance/protocol authority is maintained in `specs/` canonical markdown artifacts.
- `bootstrap/` documents are execution-plane operational mirrors and controls.
- If conflict exists, canonical docs in `specs/` prevail; bootstrap files must be updated to match.

## Planning Layers

1. Governance / contract intent (binding and directional)
- Location: `specs/`
- Role: Source specifications and backlog source docs.
- Examples:
  - `specs/ontoForge_90_Implementation-plane_backlog.md`
  - `specs/ontoForge_91_Build-Readiness Backlog v0.1.md`
  - `specs/ontoForge_03_Product-Spec_V1.1.md`

2. Active execution plan (authoritative for implementation-plane work)
- Location: `bootstrap/plans/`
- Authoritative file: `bootstrap/plans/phase1_execution_plan.md`
- Program control archive: `bootstrap/plans/archive/support_ontology_execution_program_v1.completed_2026-03-07.md`
- Plan item index: `bootstrap/plans/phase1_plan_items.csv`
- Product-spec implementation plan: `bootstrap/plans/of03_product_spec_implementation_plan.md`

3. Traceability from source backlogs to active execution
- Location: `bootstrap/plans/`
- File: `bootstrap/plans/phase0_backlog_alignment.md`
- Role: Maps source BR work items to active `TASK-*` / `BPL-*` items and current task status.

4. Archived text versions of source backlogs
- Location: `bootstrap/plans/archive/`
- Files:
  - `ontoForge_90_Implementation-plane_backlog.v0.1.md`
  - `ontoForge_91_Build-Readiness_Backlog.v0.1.md`

5. Operational execution state
- Location: `bootstrap/`
- Files:
  - `task_ledger.csv`
  - `artifact_registry.csv`
  - `evidence_register.csv`
  - `reports/daily_state_snapshot.md`

## Current Decomposition Level

Decomposition currently in use:
- Workstream level: `P1-001` ... `P1-026` in `phase1_plan_items.csv`
- Task level: `TASK-*` (implementation) and `BPL-*` (bootstrap coordination) in `task_ledger.csv`, each mapped to one `plan_item_id`
- Evidence level: `EP-*` rows in `evidence_register.csv`
- Artifact level: `ART-*` rows in `artifact_registry.csv`

This is a 4-layer decomposition stack:
- `P1` (workstream) -> `TASK/BPL` (task) -> `EP` (evidence criterion) -> `ART` (artifact proof)

## Current Status Snapshot

- Active workstreams:
  - none
- Next queued workstreams:
  - none
- Open task frontier:
  - none
- Open evidence rows:
  - none

## Enforcement Rules (active)

Enforced by `tools/bootstrap_validate.py`:
- every task must include `plan_item_id`
- `plan_item_id` must exist in `phase1_plan_items.csv`
- `DONE` requires validation evidence and existing output path(s)
- strict phase-0 closure mode requires all evidence rows `VERIFIED`

Validation commands:
- `python tools/bootstrap_validate.py`
- `python tools/bootstrap_validate.py --require-phase0-closed`
- `python tools/bootstrap_validate.py --execute-validation-methods strict`

## When You Add New Work

1. Add a new `P1-xxx` row to `phase1_plan_items.csv`.
2. Add task row(s) to `task_ledger.csv` with that `plan_item_id`.
3. Link evidence via `evidence_row_ids`.
4. Add artifact rows with SHA256 to `artifact_registry.csv`.
5. If future work introduces a new execution program, create a new `bootstrap/plans/*execution_program*.md` and archive prior program controls.
6. Run validator and regenerate snapshot.
