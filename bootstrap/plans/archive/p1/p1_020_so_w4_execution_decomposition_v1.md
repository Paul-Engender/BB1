# P1-020 SO-W4 Execution Decomposition Plan

Status: ACTIVE
Plan Item: P1-020
Owner: paul
Date: 2026-03-07
Scope: Runtime 2 compiler contract baseline (SO-W4)

## Purpose

Decompose SO-W4 into executable tasks that define the semantic handshake between
released support ontology contracts and Runtime-2 tenant compiler inputs and
outputs.

## Binding Inputs

- `specs/ontoForge_02_Lifecycle-Specification_v1.1.md`
- `specs/ontoForge_03_Product-Spec_V1.1.md`
- `specs/ontoForge_04_Decisions-Register_v1.1.md`
- `specs/product_runtime_instantiation_clarification_addendum_2026-03-07.md`
- `specs/support_ontology_authority_model_v1.md`
- `specs/support_ontology_operation_model_v1.md`
- `specs/support_ontology_target_scope_action_model_v1.md`
- `specs/support_ontology_machine_contract_map_v1.md`
- `specs/support_ontology_release_payload_contract_v1.md`
- `specs/support_ontology_w3_compiler_vocabulary_review_v1.md`
- `bootstrap/plans/reference/proposed_support_ontology_full_layer_backlog_v1.md`

## Scope Boundary

In scope:
- minimum tenant workflow input contract for first compile
- compiled control primitive output contract for `SCR_TBox_Release`
- support-to-compiler admissibility matrix for deterministic accept/reject
- integration review and SO-W4 closure handoff to SO-W5

Out of scope:
- Runtime 2 compiler code implementation
- Runtime 3 operational event-system implementation
- Runtime service/API implementation

## Decomposition

1. `TASK-20.1` Define SO-W4 execution decomposition and controls
- Output: this document

2. `TASK-20.2` Define minimum tenant workflow input contract
- Output: `specs/runtime2_tenant_workflow_input_contract_v1.md`

3. `TASK-20.3` Define compiled control primitive output contract
- Output: `specs/runtime2_compiled_control_primitives_v1.md`

4. `TASK-20.4` Define support-to-compiler admissibility matrix
- Output: `specs/runtime2_support_admissibility_matrix_v1.md`

5. `TASK-20.5` Publish SO-W4 integration review closure note
- Output: `specs/runtime2_compiler_contract_baseline_review_v1.md`

## Execution Rules

- No permissive defaults for missing tenant workflow semantics.
- No inferred authority, scope, target, action, or effect semantics.
- DD-004 MVP constraint exclusion remains enforced.
- DD-005 eligibility non-permissive boundary remains enforced.
- Runtime 2 compile semantics and Runtime 3 operational instantiation remain
  non-conflated per addendum boundary.

## EP-20 Gate Intent

`EP-20` is verified only when all SO-W4 contracts are complete, cross-consistent,
and explicit on admissibility and output semantics for Runtime-2 compilation.

## Next Frontier

- Execute `TASK-20.2`
- Execute `TASK-20.3`
- Execute `TASK-20.4`
- Execute `TASK-20.5`

