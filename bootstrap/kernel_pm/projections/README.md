# Kernel PM Projections

Deterministic read views generated from kernel PM bundle records.

Authoritative source:
- `bootstrap/kernel_pm/bundles/`

Generator:
- `tools/project_kernel_bundle_to_csv.py`

Current projection files:
- `phase2_plan_items_projection.csv`
- `task_ledger_projection.csv`
- `evidence_register_projection.csv`
- `work_packages_projection.csv`
- `dependency_relations_projection.csv`
- `role_assignments_projection.csv`
- `checkpoint_specifications_projection.csv`
- `task_execution_records_projection.csv`
- `checkpoint_records_projection.csv`
- `risk_register_projection.csv`
- `issue_register_projection.csv`
- `mitigation_plans_projection.csv`
- `change_requests_projection.csv`
- `impact_assessments_projection.csv`

Notes:
- Projection files are read surfaces and must be regenerated from bundle input.
- Some files may be header-only until corresponding object kinds are populated
  in the forward bundle.
