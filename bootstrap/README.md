# Bootstrap Execution (Phase-0)

This folder contains the temporary Bootstrap Project Ledger (BPL) used to coordinate Phase-0 build-readiness execution.

The bootstrap layer is operational tooling only. It is not part of the product runtime architecture.

## Canonical Bootstrap Protocols

- `bootstrap/protocols/project_operating_protocol_v0.1.md`
- `bootstrap/protocols/work_decomposition_protocol_v0.1.md`

These are the repo-native protocol sources for implementation-plane operating behavior during bootstrap.

## Plans

- Authoritative active plan: `bootstrap/plans/phase1_execution_plan.md`
- Plan index for validator enforcement: `bootstrap/plans/phase1_plan_items.csv`
- Superseded plans: `bootstrap/plans/archive/`

Every task row must include `plan_item_id` mapped to the active plan index.

## Files

- `task_ledger.csv`: task-level execution status, dependencies, outputs, and evidence links.
- `artifact_registry.csv`: produced artifacts, integrity hashes, and validation state.
- `evidence_register.csv`: Evidence Pack rows and gate verification status.
- `reports/daily_state_snapshot.md`: generated daily status report.
- `schemas/*.schema.json`: row schemas for ledger/register structure.

## Status Semantics

Task ledger `status` values:
- `TO_DO`, `IN_PROGRESS`, `BLOCKED`, `COMPLETED`, `DONE`, `DID_NOT_DO`

Artifact and evidence status values:
- `TO_DO`, `COMPLETED`, `DONE`, `VERIFIED`, `BLOCKED`

Gate rule:
- Phase-0 closes only when all evidence rows are `VERIFIED`.

## Commands

Run baseline integrity checks:

```bash
python tools/bootstrap_validate.py
```

Regenerate daily snapshot from ledgers:

```bash
python tools/bootstrap_snapshot.py
```

Enforce strict Phase-0 closure criteria:

```bash
python tools/bootstrap_validate.py --require-phase0-closed
```

Preview per-task validation command execution without running commands:

```bash
python tools/bootstrap_validate.py --execute-validation-methods dry-run
```

Execute each `DONE` `TASK-*` `validation_method` command and fail on any non-zero exit:

```bash
python tools/bootstrap_validate.py --execute-validation-methods strict
```

## CI Workflows

- `.github/workflows/bootstrap-integrity.yml`
  - validates ledgers
  - regenerates snapshot
  - fails if snapshot diff is uncommitted

- `.github/workflows/phase0-gate-check.yml`
  - enforces `--require-phase0-closed`

## Orientation

- Planning map: `bootstrap/plans/PLAN_INDEX.md`
