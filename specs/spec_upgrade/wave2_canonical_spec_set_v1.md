# Wave-2 Canonical Spec Set Baseline v1

Status: IS
Owner: paul
Plan Item: P1-010
Task: TASK-10.1
Date: 2026-03-06

## Purpose

Define the wave-2 canonical authority baseline by extending wave-1 with explicit residual-control focus.

## Inputs

- `specs/spec_upgrade/canonical_spec_set_v1.md`
- `specs/ontoForge_00_Canonical-Document-Set_Map_v1.0.md`

## Wave-2 Canonical Focus

Wave-2 keeps the same canonical authority boundary as wave-1 and adds focus on:
- recurring migration execution controls,
- phase-scoped evidence extension,
- validator rule stability under iterative backlog growth.

## Canonical Set (Wave-2)

The canonical set remains the wave-1 authoritative set:
- OF-00, OF-01, OF-02, OF-03, OF-04
- OF-80, OF-81
- OF-90, OF-91, OF-92
- CID-SPEC, LEDGER-SPEC, ISSUERPROOF-SPEC, EVALUATOR-SPEC
- RUNTIME-INST-ADD-20260307 (`specs/product_runtime_instantiation_clarification_addendum_2026-03-07.md`)

## Wave-2 Baseline Rules

1. Governance semantics remain authoritative only in `specs/ontoForge_*.md`.
2. Wave-2 controls must preserve strict executable validation for all `DONE TASK-*` rows.
3. Any new evidence row must not alter phase-0 closure semantics.
4. Wave-2 outputs must be hash-bound in artifact registry before evidence closure.
