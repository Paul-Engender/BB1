# Runtime 2 Tenant Workflow Input Contract v1

Status: APPROVED
Owner: paul
Plan Item: P1-020
Task: TASK-20.2
Date: 2026-03-07

## Purpose

Define the minimum canonical tenant workflow input surface admitted by Runtime 2
for first compile under global doctrine and released support semantics.

This contract is fail-closed: missing, ambiguous, inferred, or default-dependent
semantics are non-permissive.

## Source Anchors

Primary canonical anchors:
- `specs/ontoForge_02_Lifecycle-Specification_v1.1.md`
- `specs/ontoForge_03_Product-Spec_V1.1.md`
- `specs/ontoForge_04_Decisions-Register_v1.1.md`
- `specs/product_runtime_instantiation_clarification_addendum_2026-03-07.md`

Support-contract anchors:
- `specs/support_ontology_target_scope_action_model_v1.md`
- `specs/support_ontology_operation_model_v1.md`
- `specs/support_ontology_authority_model_v1.md`
- `specs/support_ontology_identifier_and_mvp_boundary_v1.md`
- `specs/support_ontology_machine_contract_map_v1.md`

## Canonical Boundary

- Runtime 2 compiles tenant workflow definitions into tenant-scoped
  `SCR_TBox_Release` outputs.
- Runtime 2 input admissibility is evaluated against released global support
  semantics and global doctrine constraints.
- Runtime 2 does not instantiate Runtime 3 operational truth events.

This artifact defines input contract semantics only.

## First-Compile Input Envelope

A first-compile tenant input package is admissible only when all are present:

1. `tenant_context`
- explicit `tenant_id` and tenant-scoped identity references

2. `workflow_definition_set`
- explicit workflow/process definitions with canonical IDs

3. `domain_and_routing_declarations`
- explicit domain and routing semantics used by compile control generation

4. `target_set_declarations`
- explicit target set identities, boundaries, and selection semantics

5. `action_effect_declarations`
- explicit action semantics and effect semantics with declared linkage

6. `scope_declarations`
- explicit scope boundaries applicable to workflows/actions

7. `operation_control_declarations`
- explicit authorization/eligibility/denial/control-state semantics

8. `ai_operable_declarations`
- explicit declaration of AI-operable semantics per workflow/action boundary

## Required Input Fields

Minimum required canonical fields for first compile:

- `tenant_id`
- `workflow_id`
- `workflow_version`
- `domain_id`
- `routing_policy_id`
- `target_set_id`
- `target_selection_basis`
- `scope_id`
- `action_id`
- `effect_id`
- `action_effect_binding_id`
- `authorization_semantics_ref`
- `eligibility_semantics_ref`
- `denial_semantics_ref`
- `ai_operable`

Field rules:
- required fields must be explicit; no inferred defaults
- all identifiers must be identifier-clean under DD-001 placement rules
- unknown values at required fields are non-permissive

## Semantic Requirements

### 1) Target semantics

- target sets must be explicitly declared and bounded
- target membership or selection basis must be explicit and reproducible
- implicit target expansion is forbidden

### 2) Scope semantics

- scope boundaries must be explicit wherever action/effect requires scope
- scope widening must be explicit and admitted, never implied

### 3) Action/effect semantics

- every executable action must reference explicit effect semantics
- action/effect linkage must be explicit and checkable
- narrative-only action/effect meaning is inadmissible

### 4) Operation/control semantics

- authorization, eligibility, denial, and control-state references are required
  where runtime behavior depends on them
- `eligible` is the only permissive eligibility state
- `ineligible` and `unknown` are non-permissive

### 5) AI-operable semantics

- `ai_operable` declaration is mandatory for first compile surfaces
- omitted or ambiguous `ai_operable` semantics are non-permissive
- `ai_operable` declaration does not bypass authority, eligibility, or scope
  requirements

## Hard Exclusions (MVP)

The following input patterns are inadmissible in first compile:

- explicit `constraints` fields in binding tenant input records
- hidden constraint semantics under renamed fields
- inferred authority from labels/taxonomy/placement
- inferred target expansion from hierarchy/similarity
- permissive defaults for missing scope/action/effect/eligibility semantics

## Non-Permissive Admissibility Outcomes

Runtime 2 must reject first-compile input deterministically when any are true:

1. Missing required canonical field
- outcome class: `ABORT` or `DENY` per stage contract

2. Implicit target or scope semantics
- outcome class: `DENY`

3. Missing action/effect linkage
- outcome class: `ABORT` at admission boundary or `DENY` at operation boundary

4. Unknown required premise
- outcome class: `DENY`

5. MVP constraint boundary violation
- outcome class: `QUARANTINE` or `ABORT` per stage contract

Reason-code format:
- `RC:<Stage>:<InvariantOrRule>:<Detail>`

## Invariant and Decision Alignment

Invariant alignment:
- `I10`, `I11` premise closure and unknown non-permissive handling
- `I14` no authority implication from classification
- `I16`, `I17`, `I23` explicit scope/target/action/effect semantics

Decision alignment:
- `DD-001` identifier hygiene
- `DD-004` MVP constraint exclusion
- `DD-005` eligibility non-permissive semantics prior to execution commitment
- `DD-007` global doctrine constraints over tenant workflows

## Boundary-Object Dependencies

First compile admission requires exact upstream release dependencies:

- approved `SupportOntologyRelease` dependency binding is required input
- tenant workflow input alone is insufficient without upstream support release
- missing or ambiguous upstream dependency reference is non-permissive

## Addendum Consideration

This contract preserves non-conflation between:
- Runtime 2 tenant input candidates
- Runtime 2 compiled boundary object outputs
- Runtime 3 operational event instantiation

## Acceptance Checklist (TASK-20.2)

- minimum first-compile tenant input envelope is explicit
- required canonical fields are explicit and non-defaulting
- target/scope/action/effect and operation semantics are explicit
- `ai_operable` requirement is explicit
- MVP constraint exclusions and non-permissive outcomes are explicit
- addendum boundary discipline is preserved
