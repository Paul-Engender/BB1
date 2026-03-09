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
- Product-spec implementation plan: `bootstrap/plans/inactive/reference/of03_product_spec_implementation_plan.md`
- Planning target operating model: `bootstrap/plans/active/planning_target_operating_model_v1.md`
- Kernel PM v1 scope decision: `bootstrap/plans/active/kernel_pm_v1_scope_decision_full_profile_operations_v1.md`
- Cutover snapshot record: `bootstrap/plans/active/cutover_c0_snapshot_record_v1.md`
- Planning manifest: `bootstrap/plans/manifests/plans_manifest.csv`

3. Traceability from source backlogs to active execution
- Location: `bootstrap/plans/`
- File: `bootstrap/plans/inactive/reference/phase0_backlog_alignment.md`
- Role: Maps source BR work items to active `TASK-*` / `BPL-*` items and current task status.

4. Archived text versions of source backlogs
- Location: `bootstrap/plans/archive/`
- Files:
  - `ontoForge_90_Implementation-plane_backlog.v0.1.md`
  - `ontoForge_91_Build-Readiness_Backlog.v0.1.md`

5. Operational execution state
- Location: `bootstrap/bridge/`
- Files:
  - `bootstrap/bridge/task_ledger.csv`
  - `bootstrap/bridge/artifact_registry.csv`
  - `bootstrap/bridge/evidence_register.csv`
  - `bootstrap/bridge/daily_state_snapshot.md`

## Current Decomposition Level

Decomposition currently in use:
- Workstream level: `P1-001` ... `P1-026` plus successor `P2-001` ... `P2-006` in `phase1_plan_items.csv`
- Task level: `TASK-*` (implementation) and `BPL-*` (bootstrap coordination) in `bootstrap/bridge/task_ledger.csv`, each mapped to one `plan_item_id`
- Evidence level: `EP-*` rows in `bootstrap/bridge/evidence_register.csv`
- Artifact level: `ART-*` rows in `bootstrap/bridge/artifact_registry.csv`

This is a 4-layer machine-enforced stack:
- `P*` (workstream) -> `TASK/BPL` (task) -> `EP` (evidence criterion) -> `ART` (artifact proof)

Phase-2 also tracks advisory hierarchy metadata in dedicated controls:
- `Program -> Milestone -> Workstream -> Work Package -> Task -> Evidence -> Artifact`
- `bootstrap/plans/programs/post_p1_026_full_solution_program_plan_v1.md`
- `bootstrap/plans/manifests/phase2_milestones.csv`
- `bootstrap/plans/manifests/phase2_work_packages.csv`
- `bootstrap/plans/manifests/phase2_traceability_map.csv`
- `bootstrap/plans/manifests/plans_manifest.csv`

## Current Status Snapshot

- Completed successor workstreams:
  - `P2-001`
  - `P2-002`
  - `P2-003`
- Open frontier workstreams:
  - `P2-004`
  - `P2-005`
  - `P2-006`
- Open task frontier:
  - `TASK-30.1`
  - `TASK-31.1`
  - `TASK-32.1`
- Open evidence rows:
  - `EP-30`
  - `EP-31`
  - `EP-32`
- Verified milestone evidence:
  - `EP-27`
  - `EP-28`
  - `EP-29`
- Forward PM authority mode:
  - Bundle-first records under `bootstrap/kernel_pm/bundles/`
  - Deterministic projections under `bootstrap/kernel_pm/projections/`
- Kernel PM v1 scope mode:
  - Existing operations: bridge subset
  - Approved target: full profile operations (decision active 2026-03-09)

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

1. Add a new `P*-xxx` row to `phase1_plan_items.csv` (use `P2-xxx` for successor program work).
2. Add task row(s) to `bootstrap/bridge/task_ledger.csv` with that `plan_item_id`.
3. Link evidence via `evidence_row_ids`.
4. Add artifact rows with SHA256 to `bootstrap/bridge/artifact_registry.csv`.
5. If future work introduces a new execution program, create a new `bootstrap/plans/*execution_program*.md` and archive prior program controls.
6. Run validator and regenerate snapshot.

## Proposal Intake Backlog

- Location: `bootstrap/plans/inactive/proposals_backlog/`
- Role: Hold incoming descriptive implementation proposals until triage.
- Intake index: `bootstrap/plans/inactive/proposals_backlog/proposals_index.csv`
- Template: `bootstrap/plans/inactive/proposals_backlog/TEMPLATE_proposal.md`
- Current entries are non-binding and do not imply approval/scheduling.




