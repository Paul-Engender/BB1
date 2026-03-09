# Support Ontology Authority Model v1

Status: APPROVED
Owner: paul
Plan Item: P1-019
Task: TASK-19.2
Date: 2026-03-07

## Purpose

Define the support-ontology authority and issuance vocabulary subset required for
Runtime 2 compile-safe semantics.

This model gives Runtime 2 explicit typed surfaces for authority-related compile
checks without importing Runtime 3 operational event behavior.

## Source Anchors

Primary canonical anchors:
- `specs/ontoForge_02_Lifecycle-Specification_v1.1.md`
- `specs/ontoForge_03_Product-Spec_V1.1.md`
- `specs/ontoForge_04_Decisions-Register_v1.1.md`
- `specs/product_runtime_instantiation_clarification_addendum_2026-03-07.md`

Companion support artifacts:
- `specs/support_ontology_csc_stage_model_v1.md`
- `specs/support_ontology_invariant_model_v1.md`
- `specs/support_ontology_machine_contract_map_v1.md`
- `specs/support_ontology_identifier_and_mvp_boundary_v1.md`
- `specs/product_event_model_v1.md`

## Canonical Boundary

- CSC is one canonical lifecycle instantiated per runtime.
- Runtime 2 compiles tenant definitions into tenant-scoped control releases.
- Runtime 2 does not emit Runtime 3 `AuthorityEvent` records.
- Runtime 3 operational truth remains out of scope for this artifact.

This document defines compile-time authority semantics only.

## Runtime 2 Authority Objective

Runtime 2 must be able to answer, at compile time:
- what authority-bearing concepts are explicitly declared
- what issuance proof semantics are required
- what authority references are admissible in compiled outputs
- which conditions force deterministic non-permissive failure

Runtime 2 must not infer authority from:
- taxonomy
- labels
- placement
- metadata
- descriptive prose

## Authority Subset Vocabulary (Compile Plane)

The support layer must expose compile-consumable authority vocabulary for:

1. Authority subject anchor
- explicit identity for the actor/principal to whom authority applies

2. Authority domain boundary
- explicit scope/domain boundary object for where authority is valid

3. Target-set anchor
- explicit target-set identity and boundary reference

4. Action anchor
- explicit action semantic anchor; action identity must be named, not implied

5. Issuance provenance anchor
- explicit issuer, issuance basis/proof reference, and issuance chain reference

6. Effect type anchor
- explicit issuance effect semantics (`GRANT`, `REVOKE`, `DELEGATE`) as typed
  compile-time values

7. Validity boundary anchor
- explicit validity interval or boundary reference where required by canonical
  contract

## Compile-Safe Authority Record Contract

Any authority-bearing compile input intended for Runtime 2 control derivation is
inadmissible unless all required fields are explicit:

- `authority_subject_id`
- `authority_scope_id`
- `authority_target_set_id`
- `authority_action_id`
- `issuer_proof_ref`
- `authority_effect`

Optional but governed when present:
- `authority_valid_from`
- `authority_valid_to`
- `authority_supersedes_ref`

Non-goal:
- This is a compile admissibility contract, not an operational authority-state
  fold algorithm.

## Issuance Semantics for Runtime 2

Runtime 2 issuance semantics are representational and admissibility-oriented:

- issuance references must be explicit and identifier-clean
- missing issuance basis is non-permissive
- unresolved issuance references are non-permissive
- issuance effect semantics must be explicit and enumerated

Runtime 2 does not perform:
- operational authority event append
- runtime as-of authority recomputation as tenant truth
- execution-time authority revocation adjudication

## Invariant and Decision Alignment

Authority model alignment:
- `I3`, `I4`, `I5`, `I14`, `I15` (authority family)
- `I10`, `I11` (premise closure and unknown non-permissive handling)

Decision anchor alignment:
- `DD-001` identifier discipline for authority references
- `DD-004` no hidden constraint semantics in compile authority records
- `DD-005` compile outputs must preserve eligibility boundary preconditions;
  authority presence alone is not execution permissiveness

## Non-Permissive Compile Rules

Runtime 2 must return deterministic non-permissive output when any are true:

1. Missing authority primitive
- any required authority field absent
- outcome class: `ABORT` or `DENY` per stage contract

2. Implicit authority attempt
- authority claimed via classification, taxonomy, alias, or metadata
- outcome class: `DENY` (primary invariant `I14`)

3. Broken issuance chain reference
- issuer proof reference absent, unbound, or non-admitted
- outcome class: `ABORT` or `DENY` per stage contract

4. Ambiguous effect semantics
- effect not in controlled set (`GRANT`, `REVOKE`, `DELEGATE`)
- outcome class: `ABORT`

5. Unknown required authority premise
- required premise unresolved at compile boundary
- outcome class: `DENY` (unknown is non-permissive)

Reason code format remains:
- `RC:<Stage>:<InvariantOrRule>:<Detail>`

## Machine-Form Allocation (Authority Subset)

1. Ontology terms
- authority subject/scope/target/action/effect vocabulary
- issuance and proof-reference role vocabulary

2. SHACL rules
- required field presence and cardinality
- controlled value restriction for effect type
- structural exclusion of unsupported MVP constraint fields

3. Deterministic validators
- reference resolution and admission closure
- identifier correctness and dependency binding checks
- unknown/non-permissive decisioning and reason-code precedence
- stage-appropriate disposition selection (`ABORT`, `QUARANTINE`, `DENY`)

## Boundary-Object Integration Rule

This authority model is consumed by Runtime 2 to produce tenant-scoped
`SCR_TBox_Release` semantics.

This model is not itself a boundary object and does not cross runtime boundaries
as tenant operational truth.

Runtime 3 consumes Runtime 2 release outputs through load-manifest gates and
instantiates operational authority outcomes separately.

## Addendum Consideration

This model enforces non-conflation between:
- Runtime 2 internal lifecycle candidates (tenant compile candidates)
- Runtime 2 boundary object outputs (`SCR_TBox_Release`)
- Runtime 3 operational authority-event instantiation

## Acceptance Checklist (TASK-19.2)

- Runtime-2 authority scope is explicit and bounded.
- Authority vocabulary subset is defined without Runtime-3 event execution scope.
- Issuance semantics and required compile fields are explicit.
- Non-permissive rules and reason-code alignment are explicit.
- Machine-form allocation is defined for ontology, SHACL, and validators.
- Addendum non-conflation and boundary-object discipline are preserved.
