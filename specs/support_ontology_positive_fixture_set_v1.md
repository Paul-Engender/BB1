# Support Ontology Positive Fixture Set v1

Status: APPROVED
Owner: paul
Plan Item: P1-023
Task: TASK-23.2
Date: 2026-03-07

## Purpose

Define the positive semantic fixture catalogue used to prove first-pass Runtime 2
compile admissibility under released support contracts.

## Inputs

- `ontology/examples/example-target-reference.ttl`
- `ontology/examples/example-stipulation.ttl`
- `ontology/examples/example-promotion-chain.ttl`
- `specs/runtime2_tenant_workflow_input_contract_v1.md`
- `specs/runtime2_support_admissibility_matrix_v1.md`
- `specs/support_to_tbox_dependency_provenance_v1.md`

## Fixture Catalogue

| Fixture ID | Source | Semantic Family | Intended Compile Outcome |
| --- | --- | --- | --- |
| `POS-FX-001` | `ontology/examples/example-target-reference.ttl` | target identity and reference closure | admissible |
| `POS-FX-002` | `ontology/examples/example-stipulation.ttl` | explicit stipulation and action/effect linkage surface | admissible |
| `POS-FX-003` | `ontology/examples/example-promotion-chain.ttl` | evidence and promotion lineage continuity | admissible |

## Required Positive Assertions

For each positive fixture:
- required canonical fields from Runtime 2 input contract are present
- target/scope/action/effect semantics are explicit
- support dependency reference is exact and hash-bound
- no unsupported MVP constraint surface is introduced

## Expected Acceptance Evidence

Successful positive-set execution must emit:
- acceptance verdict per fixture id
- compile profile id/version
- digest for input set and compile output
- dependency provenance digest references

## Non-Permissive Rule

A fixture is not positive by naming alone. If required explicit semantics are
missing, it fails and exits the positive set.

## Done Test

This artifact is complete only if:
- at least one positive fixture exists for each major first-compile semantic family
- expected admissible outcome is explicit per fixture
- expected evidence outputs are explicit per fixture
