# P1-021 SO-W5 Execution Decomposition Plan

Status: ACTIVE
Plan Item: P1-021
Owner: paul
Date: 2026-03-07
Scope: Support ontology validation gate design (SO-W5)

## Purpose

Decompose SO-W5 into executable tasks that define fail-closed validation gates
for Runtime 2 support-contract admissibility and evidence discipline.

## Binding Inputs

- `specs/ontoForge_02_Lifecycle-Specification_v1.1.md`
- `specs/ontoForge_03_Product-Spec_V1.1.md`
- `specs/ontoForge_04_Decisions-Register_v1.1.md`
- `specs/product_runtime_instantiation_clarification_addendum_2026-03-07.md`
- `specs/support_ontology_machine_contract_map_v1.md`
- `specs/support_ontology_invariant_model_v1.md`
- `specs/support_ontology_identifier_and_mvp_boundary_v1.md`
- `specs/runtime2_tenant_workflow_input_contract_v1.md`
- `specs/runtime2_compiled_control_primitives_v1.md`
- `specs/runtime2_support_admissibility_matrix_v1.md`
- `specs/runtime2_compiler_contract_baseline_review_v1.md`
- `bootstrap/plans/proposed_support_ontology_full_layer_backlog_v1.md`

## Scope Boundary

In scope:
- ontology/SHACL uplift targets for missing machine-consumable semantics
- non-SHACL validator requirements for deterministic gates
- reason-code and evidence output contract for non-permissive outcomes
- integration review and SO-W5 closure handoff to SO-W6

Out of scope:
- Runtime 2 compiler code implementation
- Runtime 3 operational event-system implementation
- runtime service/API implementation

## Decomposition

1. `TASK-21.1` Define SO-W5 execution decomposition and controls
- Output: this document

2. `TASK-21.2` Define ontology/SHACL validation uplift targets
- Output: `specs/support_ontology_validation_uplift_v1.md`

3. `TASK-21.3` Define non-SHACL semantic gate requirements
- Output: `specs/runtime2_semantic_gate_requirements_v1.md`

4. `TASK-21.4` Define reason-code and evidence output contract
- Output: `specs/support_ontology_reasoncode_evidence_contract_v1.md`

5. `TASK-21.5` Publish SO-W5 integration review closure note
- Output: `specs/support_ontology_validation_gate_review_v1.md`

## Execution Rules

- Unknown required premises are non-permissive.
- No permissive defaults in validator behavior.
- DD-004 MVP constraint exclusion remains enforced.
- DD-005 eligibility non-permissive boundary remains enforced.
- Runtime 2 validation gates and Runtime 3 operational instantiation remain
  non-conflated per addendum boundary.

## EP-21 Gate Intent

`EP-21` is verified only when SO-W5 uplift targets, semantic gate
requirements, and reason-code/evidence contract are complete and
cross-consistent.

## Next Frontier

- Execute `TASK-21.2`
- Execute `TASK-21.3`
- Execute `TASK-21.4`
- Execute `TASK-21.5`
