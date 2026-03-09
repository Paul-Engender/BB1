# Support Ontology Negative Fixture Set v1

Status: APPROVED
Owner: paul
Plan Item: P1-023
Task: TASK-23.3
Date: 2026-03-07

## Purpose

Define the negative semantic fixture catalogue used to prove deterministic
non-permissive Runtime 2 behavior.

## Inputs

- `ontology/negative_examples/targetref_missing_isaboutentity.ttl`
- `ontology/negative_examples/targetref_two_isaboutentity.ttl`
- `ontology/negative_examples/stipulation_two_stipulateson.ttl`
- `ontology/negative_examples/restriction_missing_ruleexpression.ttl`
- `ontology/negative_examples/evaluator_missing_measurementspec.ttl`
- `specs/runtime2_support_admissibility_matrix_v1.md`
- `specs/support_ontology_reasoncode_evidence_contract_v1.md`

## Fixture Catalogue

| Fixture ID | Source | Failure Class | Expected Outcome | Expected Reason-Code Family |
| --- | --- | --- | --- | --- |
| `NEG-FX-001` | `ontology/negative_examples/targetref_missing_isaboutentity.ttl` | missing required target identity field | ABORT | `RC:S2:I10:*` |
| `NEG-FX-002` | `ontology/negative_examples/targetref_two_isaboutentity.ttl` | structural multiplicity violation | ABORT | `RC:S2:INV-STRUCT:*` |
| `NEG-FX-003` | `ontology/negative_examples/stipulation_two_stipulateson.ttl` | unsupported or ambiguous linkage multiplicity | DENY | `RC:S4:I16:*` |
| `NEG-FX-004` | `ontology/negative_examples/restriction_missing_ruleexpression.ttl` | missing explicit rule semantics | ABORT | `RC:S2:I23:*` |
| `NEG-FX-005` | `ontology/negative_examples/evaluator_missing_measurementspec.ttl` | missing required operation semantic surface | DENY | `RC:S6:I10:*` |

## Determinism Rules

- Failure classification and primary reason-code family must be deterministic.
- Unknown/missing required semantics are non-permissive.
- First failure determines primary cause; secondary causes may be appended.

## Evidence Requirements

Each negative fixture run must produce:
- fixture id
- non-permissive outcome (`ABORT|DENY|QUARANTINE`)
- primary reason-code
- evidence digest reference

## Done Test

This artifact is complete only if:
- negative fixtures cover structural, scope/action, and operation semantic failures
- expected non-permissive outcome is explicit per fixture
- expected reason-code family is explicit per fixture
