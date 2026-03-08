# Support Ontology Runtime2 Readiness Gate v1

Status: APPROVED
Owner: paul
Plan Item: P1-023
Task: TASK-23.4
Date: 2026-03-07

## Purpose

Define the minimum readiness gate proving the support layer is sufficient to
start Runtime 2 implementation.

## Inputs

- `specs/support_ontology_positive_fixture_set_v1.md`
- `specs/support_ontology_negative_fixture_set_v1.md`
- `specs/support_to_tbox_dependency_provenance_v1.md`
- `specs/runtime2_compiled_control_primitives_v1.md`

## Gate Definition

SO-W7 readiness passes only when all three proofs are satisfied.

### Proof A: Positive compile proof

At least one positive tenant fixture compiles to a valid tenant-scoped
`SCR_TBox_Release` using only released support artifacts plus tenant input.

### Proof B: Negative fail-closed proof

At least one negative tenant fixture is rejected with deterministic,
reason-coded non-permissive output.

### Proof C: Lineage proof

Produced `SCR_TBox_Release` records exact support dependency and evidence linkage
sufficient for Runtime 3 load verification.

## Readiness Checks

1. `RG-01` Positive compile acceptance
- requires pass for at least one `POS-FX-*`

2. `RG-02` Negative compile rejection
- requires deterministic fail outcome and primary reason-code for at least one `NEG-FX-*`

3. `RG-03` Dependency provenance completeness
- requires exact `support_release_id`, manifest digest, evidence digest, and tenant binding

4. `RG-04` Non-permissive unknown handling
- requires unknown required semantics to reject, not default

## Pass/Fail Rule

- Gate status is `PASS` only when `RG-01..RG-04` all pass.
- Any failed check yields gate status `FAIL`.

## Evidence Output Contract

Gate execution must emit:
- gate run id and timestamp
- fixture ids executed
- outcome per fixture
- primary reason-code for rejected fixtures
- compile output digest(s)
- dependency provenance digest(s)
- final gate verdict

## Runtime Boundary Note

This gate proves Runtime 2 readiness only.
It does not implement Runtime 2 compiler runtime behavior or Runtime 3
operational event semantics.

## Done Test

This artifact is complete only if:
- positive proof, negative proof, and lineage proof are all explicit
- pass/fail criteria are deterministic
- evidence output requirements are explicit
