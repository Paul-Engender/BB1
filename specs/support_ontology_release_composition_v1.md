# Support Ontology Release Composition v1

Status: APPROVED
Owner: paul
Plan Item: P1-016
Task: TASK-16.1
Date: 2026-03-07

## Purpose

Define the canonical composition contract for `SupportOntologyRelease` so Runtime 1 emits the real upstream semantic bundle required by Runtime 2, replacing placeholder-oriented payload assumptions.

## Inputs and Authority

Primary inputs:
- `specs/support_ontology_ttl_admission_register_v1.md`
- `specs/support_ontology_identifier_and_mvp_boundary_v1.md`
- `specs/product_boundary_objects_v1.md`
- `specs/ontoForge_03_Product-Spec_V1.1.md`
- `specs/ontoForge_04_Decisions-Register_v1.1.md`

Admission-controlled source states (from approved register):
- `ontology/kernel.ttl` -> APPROVED
- `ontology/kernel.shacl.ttl` -> APPROVED
- `ontology/support.ttl` -> NOT_APPROVED
- `ontology/scr_tbox.ttl` -> NON_BINDING

## Composition Contract

`SupportOntologyRelease` canonical payload MUST contain:
- `ontology/kernel.ttl` (primary semantic vocabulary source)
- `ontology/kernel.shacl.ttl` (structural/admissibility shape layer)

`SupportOntologyRelease` canonical payload MUST NOT contain:
- `ontology/support.ttl` (not approved)
- `ontology/scr_tbox.ttl` (non-binding for this release contract stage)
- fixture corpora (`ontology/examples/*`, `ontology/negative_examples/*`) as payload files

Evidence bundle MUST contain:
- release candidate evaluation summary
- check-level validation stream
- any promotion-decision/evidence files required by Runtime 1 hardening controls

## Manifest-Level Requirements

Manifest requirements remain aligned with boundary-object policy:
- `artifact_type = SupportOntologyRelease`
- `tenant_scope = global`
- `artifact_id` and release IDs remain `cid:<uuidv7>`-clean
- deterministic hash set over payload and evidence files
- dependencies explicit (empty for root support release unless promoted policy states otherwise)

Primary payload file for canonical release contract:
- `primary_file = ontology/kernel.ttl`

## Runtime Contract Implications

Runtime 1 implications:
- release candidate evaluation must parse/validate both canonical payload members
- package builder must include both canonical payload members
- release manifest must reflect canonical payload membership explicitly

Runtime 2 implications:
- may assume canonical support semantics are sourced from kernel+shacl package members
- must not rely on `ontology/support.ttl` placeholder semantics

Runtime 3 implications:
- unchanged under this task (consumes Runtime 2 outputs via existing boundary contracts)

## Compatibility and Transition Rule

Transition rule from current v0.2.x packaging:
- existing payload model using `ontology/support.ttl` is treated as legacy and non-canonical
- next canonical support release composition must shift primary payload to kernel-based bundle
- no implicit fallback to `support.ttl` is permitted in canonical compile path

## Addendum Consideration

Boundary-object non-conflation and runtime instantiation separation from the 2026-03-07 addendum are required for this composition contract.

## Non-Goals

Out of scope for this task:
- implementation changes to Runtime 1 code
- namespace/import policy details beyond composition membership
- Runtime 2 compiler implementation work

## Validation Checklist (TASK-16.1)

- composition explicitly names canonical payload members
- composition explicitly excludes non-approved/non-binding `.ttl` files from payload
- manifest-level boundary constraints are preserved
- transition off placeholder payload is explicit and non-defaulting
