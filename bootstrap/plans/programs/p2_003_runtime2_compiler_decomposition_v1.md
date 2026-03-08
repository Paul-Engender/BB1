# P2-003 Runtime 2 Compiler Decomposition v1

Status: APPROVED
Owner: paul
Plan Item: P2-003
Task: TASK-29.1
Date: 2026-03-08
Operational role: ACTIVE_CONTROL

## Purpose

Define the executable decomposition controls for Runtime 2 compiler work using
only the retained approved baseline and the verified M1 successor outputs.

## Baseline Inputs

- `specs/runtime2_tenant_workflow_input_contract_v1.md`
- `specs/runtime2_compiled_control_primitives_v1.md`
- `specs/runtime2_support_admissibility_matrix_v1.md`
- `specs/runtime2_compiler_contract_baseline_review_v1.md`
- `specs/support_ontology_runtime2_readiness_review_v1.md`
- `specs/p2_contract_translation_review_v1.md`
- `specs/p2_contract_delta_register_v1.md`
- `specs/product_tenant_scope_rules_v1.md`

## Decomposition Rule

This decomposition opens Runtime 2 implementation planning without reopening the
approved Runtime 2 semantic baseline.

Rules:
- Runtime 2 remains fail-closed
- Runtime 2 must not infer missing semantics
- Runtime 2 must not emit Runtime 3 operational truth events
- Runtime 2 implementation work must remain traceable to the retained SO-W4 and
  SO-W7 baseline

## Immediate Task Set

### TASK-29.2 Define Runtime 2 compiler module boundary
- Purpose: define module boundaries and repo placement for the compiler lane
- Output: `specs/runtime2_compiler_module_boundary_v1.md`

### TASK-29.3 Define Runtime 2 ingest-admissibility contract
- Purpose: translate the approved input contract and admissibility matrix into
  implementation-facing ingest/gate controls
- Output: `specs/runtime2_ingest_admissibility_contract_v1.md`

### TASK-29.4 Define Runtime 2 compiled-primitive emission contract
- Purpose: translate the approved compiled primitive output contract into
  implementation-facing emission/evidence controls
- Output: `specs/runtime2_compiled_primitive_emission_contract_v1.md`

### TASK-29.5 Publish Runtime 2 decomposition closure note
- Purpose: confirm the decomposition package and hand off to implementation
  tasks/code work
- Output: `specs/runtime2_compiler_decomposition_closure_v1.md`

## Gating Note

Completion of this decomposition package does not by itself close `EP-29`.

`EP-29` remains the executable compiler-baseline gate and will require
implementation outputs plus evidence beyond this decomposition tranche.

## Acceptance Checklist (TASK-29.1)

- retained Runtime 2 baseline inputs are explicit
- immediate follow-on task set is explicit
- decomposition does not reopen baseline semantics
- compiler implementation remains separated from Runtime 3 operational truth
- `EP-29` is explicitly left open for implementation closure
