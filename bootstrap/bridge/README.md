# Bootstrap Execution Layer

This folder is the implementation-plane execution layer.

It now operates in **bundle-first mode** for forward project-management records, with legacy CSV controls retained as bridge/projection surfaces.

## Canonical Source Rule

- Governance/protocol authority remains in `specs/` canonical docs.
- Bootstrap surfaces are operational controls and projections.
- If conflicts exist, canonical docs prevail.

## Forward vs Legacy

Forward authority (post-`C0`):
- `bootstrap/kernel_pm/bundles/` (authoritative write surface)
- `bootstrap/kernel_pm/projections/` (deterministic CSV projections)
- Scope decision: full-profile operations target approved in
  `bootstrap/plans/active/kernel_pm_v1_scope_decision_full_profile_operations_v1.md`

Bridge controls (legacy-compatible surfaces):
- `bootstrap/plans/phase1_execution_plan.md`
- `bootstrap/plans/phase1_plan_items.csv`
- `bootstrap/bridge/task_ledger.csv`
- `bootstrap/bridge/evidence_register.csv`
- `bootstrap/bridge/artifact_registry.csv`
- `bootstrap/bridge/schemas/` (row-level schemas for bridge CSV controls)
- `bootstrap/bridge/daily_state_snapshot.md` (generated operational snapshot)

## Planning Structure

- Orientation: `bootstrap/plans/PLAN_INDEX.md`
- Active controls: `bootstrap/plans/active/`
- Programs: `bootstrap/plans/programs/`
- Manifests: `bootstrap/plans/manifests/`
- References: `bootstrap/plans/inactive/reference/`
- Proposal backlog: `bootstrap/plans/inactive/proposals_backlog/`
- Archive: `bootstrap/plans/archive/`

## Validation Commands

```bash
python tools/validate_kernel_project_bundle.py --bundle bootstrap/kernel_pm/bundles/open_frontier_kernel_project_bundle_v1.json
python tools/project_kernel_bundle_to_csv.py --bundle bootstrap/kernel_pm/bundles/open_frontier_kernel_project_bundle_v1.json --outdir bootstrap/kernel_pm/projections
python tools/bootstrap_validate.py
```

## Notes

- Pre-`C0` history remains preserved; no retroactive rewrite is required.
- Forward `P2-004+` rows are projection-locked by `tools/bootstrap_validate.py`.
- Existing execution continuity remains bridge-compatible while full-profile
  kernel PM operational surfaces are activated in phases.



