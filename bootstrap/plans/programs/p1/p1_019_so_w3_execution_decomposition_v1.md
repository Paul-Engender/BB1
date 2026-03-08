# P1-019 SO-W3 Execution Decomposition Plan

Status: ACTIVE
Plan Item: P1-019
Owner: paul
Date: 2026-03-07
Scope: Support ontology compiler vocabulary expansion for Runtime 2 (SO-W3)

## Purpose

Decompose SO-W3 into executable tasks that produce the Runtime-2-relevant
semantic vocabulary subset required for compile-safe typing and admissibility.

## Binding Inputs

- `specs/ontoForge_02_Lifecycle-Specification_v1.1.md`
- `specs/ontoForge_03_Product-Spec_V1.1.md`
- `specs/ontoForge_04_Decisions-Register_v1.1.md`
- `specs/product_runtime_instantiation_clarification_addendum_2026-03-07.md`
- `specs/product_event_model_v1.md`
- `specs/support_ontology_machine_contract_map_v1.md`
- `bootstrap/plans/reference/proposed_support_ontology_full_layer_backlog_v1.md`


## Support-Ontology Input Coverage

The following `specs/support_ontology_*` artifacts are explicitly considered in
SO-W3 scope and decomposition:

- `specs/support_ontology_machine_contract_map_v1.md` (primary allocation anchor)
- `specs/support_ontology_csc_stage_model_v1.md` (stage boundary semantics)
- `specs/support_ontology_invariant_model_v1.md` (failure/invariant semantics)
- `specs/support_ontology_identifier_and_mvp_boundary_v1.md` (DD boundary placement)
- `specs/support_ontology_governance_incorporation_model_v1.md` (governance translation boundary)
- `specs/support_ontology_release_composition_v1.md` (upstream support release semantics)
- `specs/support_ontology_release_payload_contract_v1.md` (Runtime 1 release contract alignment)
- `specs/support_ontology_namespace_policy_v1.md` (namespace/import constraints)

Considered but out-of-scope for SO-W3 execution outputs:
- `specs/support_ontology_external_ontology_policy_v1.md`
- `specs/support_ontology_external_mapping_candidates_v1.csv`
- `specs/support_ontology_ttl_inventory_v1.md`
- `specs/support_ontology_ttl_admission_register_v1.md`

Rationale:
- SO-W3 is compiler-vocabulary expansion for Runtime 2.
- Asset-admission and external-ontology intake controls remain governing inputs
  but are not expanded as primary deliverables in this workstream.

## Scope Boundary

In scope:
- Runtime-2-relevant authority and issuance vocabulary subset
- Runtime-2-relevant operation/control vocabulary subset
- Explicit target/scope/action/effect vocabulary subset
- Cross-model consistency and handoff readiness for SO-W4

Out of scope:
- full Runtime 3 operational event-system design
- runtime service/API implementation
- compiler code implementation

## Decomposition

1. `TASK-19.1` Define SO-W3 execution decomposition and controls
- Output: this document

2. `TASK-19.2` Define authority/issuance subset model
- Output: `specs/support_ontology_authority_model_v1.md`

3. `TASK-19.3` Define operation/control subset model
- Output: `specs/support_ontology_operation_model_v1.md`

4. `TASK-19.4` Define target/scope/action/effect model
- Output: `specs/support_ontology_target_scope_action_model_v1.md`

5. `TASK-19.5` Produce SO-W3 integration review and closure note
- Output: `specs/support_ontology_w3_compiler_vocabulary_review_v1.md`

## Execution Rules

- No implicit authority inference from taxonomy, labels, placement, or metadata.
- No relocation of constitutional meaning from doctrine/lifecycle/decisions sources.
- No permissive defaults for missing semantics.
- Boundary-object and runtime-instantiation non-conflation from the addendum is mandatory for all SO-W3 outputs.
- DD-004 MVP constraint boundary remains enforced.

## EP-19 Gate Intent

`EP-19` is verified only when all three model documents are complete,
cross-consistent, and explicitly bounded to Runtime-2 compile semantics.

## Next Frontier

- Execute `TASK-19.2`
- Execute `TASK-19.3`
- Execute `TASK-19.4`
- Execute `TASK-19.5`

