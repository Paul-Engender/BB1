# Kernel PM Authority Switch Policy v1

Status: ACTIVE
Owner: paul
Date: 2026-03-08
Plane: implementation
Operational role: ACTIVE_CONTROL

## Purpose

Activate bundle-first authority for forward project-management records after
`C0`, while keeping CSV ledgers as read-only projection surfaces.

## Boundary Notice

This is an implementation-plane control policy.

It does not create governance authority, runtime permission, or execution truth
by prose. Execution truth remains evidence-bound.

## Effective Scope

This policy applies to forward work created after `C0`, starting with the open
frontier represented in:
- `bootstrap/kernel_pm/bundles/open_frontier_kernel_project_bundle_v1.json`

## Authority Rule

Bundle-first rule:
- authoritative write surface: kernel PM bundles under `bootstrap/kernel_pm/bundles/`
- projection-only surfaces: CSV ledgers under `bootstrap/`

No forward PM change is valid unless recorded in the kernel bundle first.

## Projection Rule

Projection tool:
- `tools/project_kernel_bundle_to_csv.py`

Current projection target:
- `bootstrap/kernel_pm/projections/phase2_plan_items_projection.csv`
- `bootstrap/kernel_pm/projections/task_ledger_projection.csv`
- `bootstrap/kernel_pm/projections/evidence_register_projection.csv`

Projection is deterministic for the same bundle input.

## Required Validation

For every bundle update, run:
1. `python tools/validate_kernel_project_bundle.py --bundle <bundle-path>`
2. `python tools/project_kernel_bundle_to_csv.py --bundle <bundle-path> --outdir bootstrap/kernel_pm/projections`
3. `python tools/bootstrap_validate.py`

## Initial Activated Bundle

Activated forward bundle:
- `bootstrap/kernel_pm/bundles/open_frontier_kernel_project_bundle_v1.json`

This bundle captures `P2-004`, `P2-005`, `P2-006` and `EP-30`, `EP-31`, `EP-32`
with explicit dependencies and validation bindings.

## Non-Goals

This policy does not retroactively rewrite historical pre-`C0` records.
Historical records remain preserved under legacy control surfaces.