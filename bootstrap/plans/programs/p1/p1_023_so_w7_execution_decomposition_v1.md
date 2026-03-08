# P1-023 SO-W7 Execution Decomposition Plan

Status: ACTIVE
Plan Item: P1-023
Owner: paul
Date: 2026-03-07
Scope: Runtime 2 readiness proof (SO-W7)

## Purpose

Decompose SO-W7 into executable tasks that prove Runtime 2 can compile using
released support artifacts with deterministic positive, negative, and lineage
readiness evidence.

## Binding Inputs

- `specs/ontoForge_02_Lifecycle-Specification_v1.1.md`
- `specs/ontoForge_03_Product-Spec_V1.1.md`
- `specs/ontoForge_04_Decisions-Register_v1.1.md`
- `specs/product_runtime_instantiation_clarification_addendum_2026-03-07.md`
- `specs/runtime2_tenant_workflow_input_contract_v1.md`
- `specs/runtime2_compiled_control_primitives_v1.md`
- `specs/runtime2_support_admissibility_matrix_v1.md`
- `specs/support_ontology_reasoncode_evidence_contract_v1.md`
- `specs/support_to_tbox_dependency_provenance_v1.md`
- `specs/support_ontology_provenance_traceability_review_v1.md`
- `bootstrap/plans/reference/proposed_support_ontology_full_layer_backlog_v1.md`

## Scope Boundary

In scope:
- positive semantic fixture set for first compile path
- negative semantic fixture set for deterministic non-permissive rejection
- minimum Runtime 2 readiness gate with dependency/evidence lineage proof
- integration review and SO-W7 closure note

Out of scope:
- Runtime 2 compiler implementation
- Runtime 3 operational runtime implementation
- runtime service/API implementation

## Decomposition

1. `TASK-23.1` Define SO-W7 execution decomposition and controls
- Output: this document

2. `TASK-23.2` Define positive semantic fixture set
- Output: `specs/support_ontology_positive_fixture_set_v1.md`

3. `TASK-23.3` Define negative semantic fixture set
- Output: `specs/support_ontology_negative_fixture_set_v1.md`

4. `TASK-23.4` Define minimum Runtime 2 readiness gate
- Output: `specs/support_ontology_runtime2_readiness_gate_v1.md`

5. `TASK-23.5` Publish SO-W7 integration review closure note
- Output: `specs/support_ontology_runtime2_readiness_review_v1.md`

## Execution Rules

- Positive fixtures must prove at least one valid compile path per major semantic
  family required for first compile.
- Negative fixtures must define deterministic expected reason-code families.
- Readiness gate must require exact support dependency and evidence lineage.
- Unknown required semantics are non-permissive; no defaults.
- DD-004 MVP constraint exclusion and DD-005 eligibility non-permissive
  boundary remain enforced.
- Runtime boundary non-conflation per addendum remains enforced.

## EP-23 Gate Intent

`EP-23` is verified only when positive, negative, and lineage readiness proofs
are complete, cross-consistent, and executable via strict validation methods.

## Next Frontier

- Execute `TASK-23.2`
- Execute `TASK-23.3`
- Execute `TASK-23.4`
- Execute `TASK-23.5`

