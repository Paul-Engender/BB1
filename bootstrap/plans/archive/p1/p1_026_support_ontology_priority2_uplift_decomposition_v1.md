# P1-026 Support Ontology Priority-2 Uplift Decomposition v1

Status: APPROVED
Owner: paul
Plan Item: P1-026
Date: 2026-03-08

## Purpose

Execute the approved Priority-2 support-ontology uplift backlog so Runtime 2 output semantics, provenance linkage, and MVP no-constraint boundaries are machine-consumable before compiler implementation begins.

## Canonical Inputs

- `specs/ontoForge_01_Doctrine_v1.1.md`
- `specs/ontoForge_02_Lifecycle-Specification_v1.1.md`
- `specs/ontoForge_03_Product-Spec_V1.1.md`
- `specs/ontoForge_04_Decisions-Register_v1.1.md`
- `specs/support_ontology_validation_uplift_v1.md`
- `specs/runtime2_compiled_control_primitives_v1.md`
- `specs/runtime2_support_admissibility_matrix_v1.md`
- `specs/support_ontology_reasoncode_evidence_contract_v1.md`
- `specs/support_ontology_identifier_and_mvp_boundary_v1.md`
- `specs/product_runtime_instantiation_clarification_addendum_2026-03-07.md`

## Scope

This workstream is limited to:
- implementing Priority-2 ontology uplift targets `O-UP-10..12`
- implementing Priority-2 SHACL uplift targets `S-UP-11..12`
- adding positive and negative fixture proof for compiled Runtime 2 output semantics
- publishing a closure review and handing the repo forward to Runtime 2 compiler implementation planning

## Explicitly Out of Scope

This workstream does not:
- implement Runtime 2 compiler logic
- implement validator-only temporal ordering, evidence sufficiency, or primary-cause selection logic
- redefine Runtime 3 operational events or execution commitment semantics
- reopen already-closed Priority-1 uplift scope except where shared files must be extended

## Target Closure Intent

P1-026 closes the remaining support-ontology uplift backlog by defining the compiler output surface, explicit provenance anchors, reason-code category anchors, and coarse structural exclusion of unsupported MVP constraints.

## Task Decomposition

### TASK-26.1 Define Priority-2 uplift execution decomposition controls

Output:
- `bootstrap/plans/programs/p1/p1_026_support_ontology_priority2_uplift_decomposition_v1.md`

Intent:
- register the Priority-2 uplift wave explicitly
- bind the implementation scope to the approved backlog and output-side contract surfaces

### TASK-26.2 Implement Priority-2 ontology uplift targets

Output:
- `ontology/kernel.ttl`

Intent:
- add compiled control primitive hierarchy
- add compile trace and dependency reference vocabulary
- add reason-code category anchors required by Runtime 2 output contracts

### TASK-26.3 Implement Priority-2 SHACL uplift targets

Output:
- `ontology/kernel.shacl.ttl`

Intent:
- enforce compiled output structural completeness
- enforce coarse MVP no-constraint exclusion for binding input/output records where structurally representable

### TASK-26.4 Prove Priority-2 uplift with compiled-output fixture coverage

Output:
- `tests/test_runtime2_output_shacl.py`

Intent:
- prove the compiled-output positive fixture conforms
- prove missing lineage or forbidden `constraints` fields fail deterministically

### TASK-26.5 Publish Priority-2 uplift closure review

Output:
- `specs/support_ontology_priority2_uplift_review_v1.md`

Intent:
- record completed Priority-2 coverage
- mark the support-ontology uplift backlog as closed
- identify Runtime 2 compiler implementation as the next execution lane

## Evidence Gate

`EP-26` is satisfied only if all of the following are true:
- `ontology/kernel.ttl` contains the approved Priority-2 ontology uplift targets
- `ontology/kernel.shacl.ttl` contains the approved Priority-2 SHACL uplift targets
- compiled Runtime 2 output fixture(s) conform to the uplifted SHACL layer
- negative compiled-output and MVP-constraint fixtures fail deterministically
- the closure review records support-ontology uplift closure and identifies the next workstream clearly

## Exit State

When this workstream is complete:
- `P1-026` moves to `DONE`
- `EP-26` moves to `VERIFIED`
- the support-ontology uplift backlog is fully closed
- the repo is ready for a dedicated Runtime 2 compiler implementation workstream

