# Runtime 2 Semantic Gate Requirements v1

Status: APPROVED
Owner: paul
Plan Item: P1-021
Task: TASK-21.3
Date: 2026-03-07

## Purpose

Define deterministic non-SHACL validator requirements for Runtime 2 admissibility
and compile gate behavior.

This artifact specifies validator inputs, checks, outputs, and fail modes for
semantics that cannot be safely enforced by ontology/SHACL alone.

## Source Anchors

Primary canonical anchors:
- `specs/ontoForge_02_Lifecycle-Specification_v1.1.md`
- `specs/ontoForge_03_Product-Spec_V1.1.md`
- `specs/ontoForge_04_Decisions-Register_v1.1.md`
- `specs/product_runtime_instantiation_clarification_addendum_2026-03-07.md`

Support anchors:
- `specs/runtime2_support_admissibility_matrix_v1.md`
- `specs/support_ontology_invariant_model_v1.md`
- `specs/support_ontology_identifier_and_mvp_boundary_v1.md`
- `specs/support_ontology_validation_uplift_v1.md`

## Canonical Boundary

- Validators in this artifact are Runtime 2 compile-gate validators.
- They do not emit Runtime 3 operational events.
- They enforce non-permissive compile behavior where ontology/SHACL is
  insufficient.

## Validator Set

### V-GATE-01 Identity and reference closure

Input:
- admitted tenant compile candidate
- support release reference set

Checks:
- required identity fields present and identifier-clean
- all required cross-references resolve to admitted records

Pass output:
- `PASS` with resolved reference map

Fail output:
- `ABORT`
- reason-code examples: `RC:S2:I8:MISSING_IDENTITY`,
  `RC:S2:I7:UNBOUND_REFERENCE`

### V-GATE-02 Dependency binding validator

Input:
- compile candidate dependency declarations
- referenced support release metadata

Checks:
- exact `SupportOntologyRelease` dependency binding present
- dependency id/version mismatch detection

Pass output:
- `PASS` with exact dependency bind proof

Fail output:
- `ABORT`
- reason-code example: `RC:S2:I7:UNBOUND_REFERENCE`

### V-GATE-03 Implicit expansion guard

Input:
- target/scope/action/effect declarations
- compile candidate semantic links

Checks:
- no implicit target expansion
- no implied scope widening
- no inferred action/effect semantics

Pass output:
- `PASS` with explicit-link closure proof

Fail output:
- `DENY`
- reason-code examples: `RC:S4:I17:IMPLICIT_TARGET`,
  `RC:S4:I16:MISSING_SCOPE`

### V-GATE-04 Eligibility non-permissive gate

Input:
- eligibility semantic references
- compile decision context

Checks:
- eligibility states restricted to `eligible|ineligible|unknown`
- `unknown` and `ineligible` remain non-permissive

Pass output:
- `PASS` with eligibility gate policy confirmation

Fail output:
- `DENY`
- reason-code example: `RC:S6:DD-005:UNKNOWN_ELIGIBILITY`

### V-GATE-05 Constraint boundary gate

Input:
- compile candidate field set
- MVP boundary rules

Checks:
- detect explicit or aliased constraint-like semantics in binding records
- enforce DD-004 exclusion

Pass output:
- `PASS` with no-constraint attestation

Fail output:
- `QUARANTINE` (admission contamination) or `ABORT` (hard invalidity)
- reason-code example: `RC:S2:DD-004:UNSUPPORTED_CONSTRAINT`

### V-GATE-06 Reason-code precedence gate

Input:
- validator failure set
- stage and invariant mapping

Checks:
- first emitted reason-code identifies primary cause
- deterministic ordering of secondary causes

Pass output:
- `PASS` with ordered reason-code list

Fail output:
- `ABORT`
- reason-code example: `RC:S6:I10:MISSING_REASON_POLICY`

### V-GATE-07 Evidence sufficiency gate

Input:
- compile result package candidate
- evidence payload and hash map

Checks:
- mandatory evidence records present
- evidence hash entries complete
- evidence links to source checks

Pass output:
- `PASS` with evidence completeness proof

Fail output:
- `ABORT`
- reason-code example: `RC:S6:I20:MISSING_EVIDENCE_LINK`

## Gate Execution Order

Runtime 2 validator execution order:
1. `V-GATE-01`
2. `V-GATE-02`
3. `V-GATE-03`
4. `V-GATE-04`
5. `V-GATE-05`
6. `V-GATE-06`
7. `V-GATE-07`

Order is fixed and deterministic.

## Validator Output Contract

Each gate must emit:
- `gate_id`
- `gate_result` (`PASS|FAIL`)
- `stage_id`
- `primary_reason_code` (if fail)
- `secondary_reason_codes` (optional)
- `evidence_refs`
- `timestamp`

Runtime 2 compile result is admissible only when all required gates pass.

## Addendum Consideration

Semantic gate requirements remain compile-runtime concerns and do not define
Runtime 3 operational event instantiation behavior.

## Acceptance Checklist (TASK-21.3)

- validator set is explicit and deterministic
- each gate defines input/check/pass/fail contract
- non-permissive fail classes are explicit
- reason-code and evidence expectations are explicit
- boundary non-conflation is preserved
