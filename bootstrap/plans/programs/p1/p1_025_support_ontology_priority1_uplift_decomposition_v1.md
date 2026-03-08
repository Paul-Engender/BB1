# P1-025 Support Ontology Priority-1 Uplift Decomposition v1

Status: APPROVED
Owner: paul
Plan Item: P1-025
Date: 2026-03-08

## Purpose

Execute the approved Priority-1 support-ontology uplift backlog so the canonical kernel and SHACL layer carry the minimum machine-consumable Runtime 2 compile-plane semantics required by the approved contracts.

## Canonical Inputs

- `specs/ontoForge_01_Doctrine_v1.1.md`
- `specs/ontoForge_02_Lifecycle-Specification_v1.1.md`
- `specs/ontoForge_03_Product-Spec_V1.1.md`
- `specs/ontoForge_04_Decisions-Register_v1.1.md`
- `specs/support_ontology_validation_uplift_v1.md`
- `specs/support_ontology_target_scope_action_model_v1.md`
- `specs/support_ontology_operation_model_v1.md`
- `specs/support_ontology_authority_model_v1.md`
- `specs/runtime2_tenant_workflow_input_contract_v1.md`
- `specs/runtime2_compiled_control_primitives_v1.md`
- `specs/runtime2_support_admissibility_matrix_v1.md`
- `specs/product_runtime_instantiation_clarification_addendum_2026-03-07.md`

## Scope

This workstream is limited to:
- implementing Priority-1 ontology uplift targets `O-UP-01..09`
- implementing Priority-1 SHACL uplift targets `S-UP-01..10`
- adding positive and negative fixture proof for the new Runtime 2 compile-plane support surface
- publishing a closure review that records what changed and what remains open

## Explicitly Out of Scope

This workstream does not:
- implement Priority-2 uplift targets `O-UP-10..12` or `S-UP-11..12`
- implement Runtime 2 compiler logic or validator-only temporal reasoning
- import Runtime 3 operational event semantics into the support ontology
- alter doctrine, lifecycle control ownership, or runtime-boundary rules

## Target Closure Intent

P1-025 closes the approved minimum uplift required to move the support ontology from a foundational Runtime 1 release substrate to a machine-consumable compile-plane baseline for Runtime 2 input semantics.

## Task Decomposition

### TASK-25.1 Define Priority-1 uplift execution decomposition controls

Output:
- `bootstrap/plans/programs/p1/p1_025_support_ontology_priority1_uplift_decomposition_v1.md`

Intent:
- register the implementation wave explicitly
- bind the execution scope to the approved uplift backlog and addendum boundaries

### TASK-25.2 Implement Priority-1 ontology uplift targets

Output:
- `ontology/kernel.ttl`

Intent:
- add explicit target, scope, action, effect, authorization, eligibility, denial, and control-state semantic anchors
- keep compile-plane semantics explicit without importing Runtime 3 operational event truth

### TASK-25.3 Implement Priority-1 SHACL uplift targets

Output:
- `ontology/kernel.shacl.ttl`

Intent:
- enforce required compile-plane fields and controlled enumerations for first-compile admissibility
- preserve fail-closed structural behavior at the ontology gate

### TASK-25.4 Prove uplift with Runtime 2 fixture coverage

Output:
- `ontology/examples/example-runtime2-input.ttl`
- `ontology/negative_examples/targetset_missing_selection_basis.ttl`
- `ontology/negative_examples/actioneffectbinding_missing_effect_ref.ttl`
- `ontology/negative_examples/eligibilitysemantic_missing_status.ttl`
- `ontology/negative_examples/tenantworkflow_missing_aioperable.ttl`
- `tests/test_negative_shacl.py`

Intent:
- prove the positive envelope conforms to the new shapes
- prove missing required compile-plane fields are rejected deterministically

### TASK-25.5 Publish Priority-1 uplift closure review

Output:
- `specs/support_ontology_priority1_uplift_review_v1.md`

Intent:
- record completed Priority-1 uplift coverage
- record remaining Priority-2 uplift and implementation follow-on scope

## Evidence Gate

`EP-25` is satisfied only if all of the following are true:
- `ontology/kernel.ttl` contains the approved Priority-1 ontology uplift targets
- `ontology/kernel.shacl.ttl` contains the approved Priority-1 SHACL uplift targets
- the positive Runtime 2 example conforms to SHACL validation
- the negative Runtime 2 fixtures fail deterministically for the intended missing fields
- the closure review records residual Priority-2 uplift scope explicitly

## Exit State

When this workstream is complete:
- `P1-025` moves to `DONE`
- `EP-25` moves to `VERIFIED`
- the support ontology carries the approved minimum Runtime 2 compile-plane baseline
- the next workstream can be defined against the now-hardened uplift baseline

