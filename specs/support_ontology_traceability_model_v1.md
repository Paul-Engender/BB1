# Support Ontology Traceability Model v1

Status: APPROVED
Owner: paul
Plan Item: P1-022
Task: TASK-22.2
Date: 2026-03-07

## Purpose

Define deterministic traceability semantics from support-layer machine contracts
back to doctrine, lifecycle, product, and decision anchors.

This artifact governs traceability only. It does not create executable runtime
behavior.

## Canonical Anchors

- `specs/ontoForge_01_Doctrine_v1.1.md`
- `specs/ontoForge_02_Lifecycle-Specification_v1.1.md`
- `specs/ontoForge_03_Product-Spec_V1.1.md`
- `specs/ontoForge_04_Decisions-Register_v1.1.md`
- `specs/product_runtime_instantiation_clarification_addendum_2026-03-07.md`

## Scope

Covered trace units:
- ontology terms
- SHACL shapes
- deterministic validators
- release-evidence records

Out of scope:
- runtime implementation code
- authority derivation logic
- eligibility execution logic

## Traceability Record Contract

Every governed support-layer unit MUST declare a `TraceabilityRecord` with:

- `trace_id`: stable identifier for the trace record
- `subject_id`: identifier of traced unit (term/shape/validator/evidence)
- `subject_kind`: one of `ONTOLOGY_TERM|SHACL_SHAPE|VALIDATOR_RULE|EVIDENCE_RECORD`
- `runtime_scope`: one of `R1|R2|R1_R2`
- `belief_anchors`: doctrinal `B#` references where applicable
- `lifecycle_anchors`: applicable CSC stage/invariant anchors (`S#`, `I#`)
- `decision_anchors`: approved decision ids (`DD-*`)
- `product_anchor`: product-spec section reference
- `source_artifacts`: canonical source file path list
- `non_conflation_assertion`: explicit statement of runtime boundary discipline
- `version`: record version
- `status`: `DRAFT|APPROVED|DEPRECATED`

## Mandatory Rules

1. No trace record, no governed meaning.
- A support-layer unit is not admissible for release if required trace fields are missing.

2. Exact source anchoring only.
- Anchors must reference exact canonical artifacts; prose summaries are insufficient.

3. Runtime non-conflation is explicit.
- Trace records must state whether semantics apply to R1 release maturation, R2 compile semantics, or both.
- R3 operational instantiation is never implied by support-layer trace records.

4. Decision boundary is preserved.
- `DD-001`, `DD-004`, and `DD-005` impacts must be declared where relevant.

5. Unknown is non-permissive.
- Missing anchor values at required fields force non-admission.

## Minimum Coverage Matrix

| Subject Kind | Required Anchors |
| --- | --- |
| `ONTOLOGY_TERM` | `product_anchor`, `lifecycle_anchors`, optional `belief_anchors`, relevant `decision_anchors` |
| `SHACL_SHAPE` | `lifecycle_anchors`, `decision_anchors` when constraining MVP boundaries |
| `VALIDATOR_RULE` | `lifecycle_anchors`, `decision_anchors`, `non_conflation_assertion` |
| `EVIDENCE_RECORD` | `product_anchor`, `decision_anchors`, `source_artifacts` |

## Validation Requirements

Traceability validation must reject if:
- `subject_kind` is missing or invalid
- any required anchor set is empty
- `non_conflation_assertion` is missing for validator/evidence units
- decision anchors are omitted where known boundary decisions apply

## Runtime Boundary Note

This model supports:
- Runtime 1 release contract traceability
- Runtime 2 compile contract traceability

This model does not operationalize Runtime 3 event truth.

## Done Test

This artifact is complete only if all are true:
- terms, shapes, validators, and evidence units are all covered by one trace model
- required anchor fields are explicit and machine-checkable
- non-conflation with Runtime 3 is explicit
- unknown/missing anchor handling is non-permissive
