# P1-024 Support Ontology Post-Review Hardening Decomposition v1

Status: APPROVED
Owner: paul
Plan Item: P1-024
Date: 2026-03-08

## Purpose

Convert the support-ontology review findings into a bounded execution wave that closes executable mismatches and normalizes approval state without conflating that work with the larger ontology/SHACL uplift backlog.

## Canonical Inputs

- `specs/ontoForge_01_Doctrine_v1.1.md`
- `specs/ontoForge_02_Lifecycle-Specification_v1.1.md`
- `specs/ontoForge_03_Product-Spec_V1.1.md`
- `specs/ontoForge_04_Decisions-Register_v1.1.md`
- `specs/support_ontology_ttl_admission_register_v1.md`
- `specs/support_ontology_release_payload_contract_v1.md`
- `specs/support_ontology_namespace_policy_v1.md`
- `specs/support_ontology_validation_uplift_v1.md`
- `specs/support_ontology_runtime2_readiness_review_v1.md`

## Scope

This workstream is limited to:
- aligning Runtime 1 candidate evaluation with the approved canonical support payload
- making release loading resistant to stale directory residue
- normalizing approval metadata on core support-ontology contract documents
- publishing a closure review and queuing the next uplift wave

## Explicitly Out of Scope

This workstream does not:
- implement the Priority-1 ontology/SHACL uplift targets
- implement Runtime 2 compiler logic
- alter the product boundary-object model or runtime-instantiation addendum
- promote legacy `dist/` artifacts by file presence alone

## Findings Being Closed

1. Runtime 1 candidate evaluation still treated `ontology/support.ttl` as a required core parse target even though the admission register and payload contract exclude it.
2. Loader extraction could leave stale residue in a reused load directory, including retired support files inside Runtime 1 promotion verification.
3. Two approved W1 contract documents still carried `DRAFT_FOR_REVIEW` status labels.
4. The larger compile-plane ontology/SHACL uplift remained real, but should be queued as separate follow-on work rather than mixed into this hardening slice.

## Task Decomposition

### TASK-24.1 Define post-review hardening controls

Output:
- `bootstrap/plans/programs/p1/p1_024_support_ontology_post_review_hardening_decomposition_v1.md`

Intent:
- register the bounded execution wave
- record what is being fixed now versus queued next

### TASK-24.2 Align Runtime 1 candidate evaluation to approved payload

Output:
- `runtime/runtime1_engine.py`

Intent:
- remove `ontology/support.ttl` from required candidate parse checks
- assert canonical payload-only evaluation in Runtime 1 tests

### TASK-24.3 Make loader extraction hermetic against stale state

Output:
- `src/loader.py`

Intent:
- clear any existing load directory before unpacking verified files
- add regression coverage proving stale files do not survive reload
- prove Runtime 1 promotion verification remains clean when `_promotion_verify` is reused

### TASK-24.4 Normalize support-ontology approval metadata

Output:
- `specs/support_ontology_release_payload_contract_v1.md`

Intent:
- set `support_ontology_release_payload_contract_v1.md` to `APPROVED`
- set `support_ontology_namespace_policy_v1.md` to `APPROVED`
- remove status drift between execution closure and canonical document state

### TASK-24.5 Publish hardening closure review

Output:
- `specs/support_ontology_post_review_hardening_review_v1.md`

Intent:
- record what was fixed, what remains open, and what the next workstream is

## Evidence Gate

`EP-24` is satisfied only if all of the following are true:
- Runtime 1 no longer requires `ontology/support.ttl` during candidate evaluation
- loader verification replaces stale load-state residue
- core support-ontology contract docs now carry `APPROVED` status
- the next workstream is queued explicitly as `P1-025`

## Exit State

When this workstream is complete:
- `P1-024` moves to `DONE`
- `EP-24` moves to `VERIFIED`
- `P1-025` is queued as the next support-ontology uplift wave

## Follow-On Workstream

`P1-025` is reserved for implementation of the approved uplift backlog in `specs/support_ontology_validation_uplift_v1.md`.

