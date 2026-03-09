# Bundle-First Repository Classification 2026-03-09

Status: ACTIVE
Owner: paul
Date: 2026-03-09

## Purpose

Define what stays in active bundle-first operations, what remains as reference,
and what belongs in archive.

## Keep In Active Operations

These are forward execution controls and should remain active:

- `bootstrap/kernel_pm/bundles/`
- `bootstrap/kernel_pm/projections/`
- `bootstrap/plans/active/planning_target_operating_model_v1.md`
- `bootstrap/plans/active/kernel_pm_authority_switch_policy_v1.md`
- `bootstrap/plans/active/kernel_pm_v1_scope_decision_full_profile_operations_v1.md`
- `bootstrap/plans/phase1_execution_plan.md`
- `bootstrap/plans/phase1_plan_items.csv`
- `bootstrap/plans/programs/post_p1_026_full_solution_program_plan_v1.md`
- `bootstrap/plans/manifests/phase2_milestones.csv`
- `bootstrap/plans/manifests/phase2_work_packages.csv`
- `bootstrap/plans/manifests/phase2_traceability_map.csv`
- `bootstrap/plans/manifests/plans_manifest.csv`
- `bootstrap/bridge/task_ledger.csv`
- `bootstrap/bridge/evidence_register.csv`
- `bootstrap/bridge/artifact_registry.csv`

## Keep As Reference (Not Active Control)

These remain important for interpretation and traceability but do not authorize
forward execution on their own:

- `bootstrap/plans/inactive/reference/phase0_backlog_alignment.md`
- `bootstrap/plans/inactive/reference/of03_product_spec_implementation_plan.md`
- `bootstrap/plans/inactive/reference/proposed_support_ontology_full_layer_backlog_v1.md`
- `bootstrap/plans/inactive/reference/cutover_and_legacy_archive_proposal_v1.md`
- `bootstrap/plans/inactive/reference/kernel_aligned_project_execution_method_v1.md`
- `bootstrap/plans/inactive/proposals_backlog/`

## Archive (Completed/Superseded)

Archive rule:
- if lifecycle is closed (`SUPERSEDED` or `ARCHIVED`) and not needed as active
  control, move under `bootstrap/plans/archive/` and keep immutable.

Archive move completed on 2026-03-09:

- `bootstrap/plans/archive/p1/p1_019_so_w3_execution_decomposition_v1.md`
- `bootstrap/plans/archive/p1/p1_020_so_w4_execution_decomposition_v1.md`
- `bootstrap/plans/archive/p1/p1_021_so_w5_execution_decomposition_v1.md`
- `bootstrap/plans/archive/p1/p1_022_so_w6_execution_decomposition_v1.md`
- `bootstrap/plans/archive/p1/p1_023_so_w7_execution_decomposition_v1.md`
- `bootstrap/plans/archive/p1/p1_024_support_ontology_post_review_hardening_decomposition_v1.md`
- `bootstrap/plans/archive/p1/p1_025_support_ontology_priority1_uplift_decomposition_v1.md`
- `bootstrap/plans/archive/p1/p1_026_support_ontology_priority2_uplift_decomposition_v1.md`

## What Should Not Be In Active Control

- duplicate narrative status surfaces that disagree with validated ledgers
- completed decomposition controls that no longer drive open work
- generated projection files edited manually
- historical migration proposals treated as forward authority

## Operational Guardrails

- bundle-first for forward PM records
- projections are generated read views
- pre-`C0` history remains preserved
- archive records are immutable except metadata correction

