# Support Ontology Identifier and MVP Boundary v1

Status: APPROVED
Owner: paul
Plan Item: P1-015
Task: TASK-15.5
Date: 2026-03-07

## Purpose

Define the support-layer admissibility boundary for identifiers, ordering-sensitive semantics, MVP constraint exclusion, and eligibility placement.

This artifact operationalizes decision anchors:
- DD-001 (identifier and versioning discipline)
- DD-003 (event ordering authority and deterministic ordering)
- DD-004 (MVP constraint exclusion and reason codes)
- DD-005 (eligibility boundary enforcement)

## Source Anchors

Primary canonical anchors:
- `specs/ontoForge_04_Decisions-Register_v1.1.md`
- `specs/ontoForge_02_Lifecycle-Specification_v1.1.md`

Runtime boundary alignment:
- `specs/ontoForge_03_Product-Spec_V1.1.md`
- `specs/support_ontology_governance_incorporation_model_v1.md`
- `specs/product_runtime_instantiation_clarification_addendum_2026-03-07.md`

## Boundary Rule

The support layer may define machine-readable semantics required by Runtime 1 and Runtime 2, but it must not absorb full Runtime 3 operational event behavior.

Where behavior depends on temporal fold, ordering authority assignment, eligibility evaluation timing, or execution commitment state, implementation belongs in deterministic validators/runtime code, not ontology-only semantics.

## Decision Anchor Translation Matrix

| Anchor | Binding Requirement | Support-Layer Rule | Implementation Placement |
| --- | --- | --- | --- |
| DD-001 | Locally minted identifiers use `cid:<uuidv7>`; identifiers are opaque and non-semantic | All support-layer binding identifiers, artifact references, and dependency references must be identifier-clean and schema-checkable | Ontology terms may declare identifier roles; strict format validation in deterministic validators/schemas |
| DD-003 | Stable ordering by `(event_time, event_id)` with single ordering authority per partition | Support layer may reference ordering concepts, but must not perform authoritative fold/order derivation in ontology alone | Deterministic validator/runtime logic for fold/replay/order; ontology/SHACL for structural declarations only |
| DD-004 | Constraints unsupported in MVP; constraint fields forbidden; reason codes required for non-permissive outcomes | Any constraint-like field in MVP binding records is inadmissible; unknown/missing semantics remain non-permissive | Deterministic validator enforces no-constraint boundary and reason-code obligations; SHACL may enforce structural absence where feasible |
| DD-005 | Eligibility evaluated before execution commitment; `eligible` only permissive result; `ineligible/unknown` non-permissive | Support layer can type eligibility concepts but must not collapse Runtime 3 execution commitment semantics into Runtime 2 support contracts | Ontology defines vocabulary; deterministic validator/runtime code enforces timing, result semantics, and commit gate |

## Admissibility Placement Rules

### 1) Ontology Layer (allowed)

Allowed:
- semantic term definitions for identity references, authority concepts, eligibility concepts, and reason-code categories
- explicit relation semantics that are non-temporal and non-execution-committing

Disallowed:
- event fold computation
- authoritative ordering resolution
- execution commitment decisions

### 2) SHACL Layer (allowed with limits)

Allowed:
- structural/cardinality checks
- mandatory field presence checks
- coarse boundary checks (for example, disallowing explicit MVP constraint fields when represented structurally)

Disallowed:
- temporal as-of recomputation
- ordering authority simulation
- final permissive/non-permissive execution decisioning

### 3) Deterministic Validator Layer (required)

Required for:
- `cid:<uuidv7>` format and identity discipline enforcement where canonical
- `(event_time, event_id)` ordering semantics and tie-break behavior
- eligibility timing and execution-commitment gating
- unknown-handling and non-permissive defaults
- reason-code emission requirements for ABORT/QUARANTINE/DENY outcomes
- no-constraint-in-MVP enforcement beyond structural shape checks

## Runtime Boundary Allocation

1. Runtime 1
- validates support release candidate semantics and evidence
- enforces identifier and packaging boundary rules for support release artifacts

2. Runtime 2
- consumes support-layer contracts for compile-time admissibility and typed output generation
- must fail non-permissively when semantics are missing/unknown/invalid

3. Runtime 3
- remains authority for tenant operational event ordering, eligibility record evaluation, and execution commitment gating
- these operational behaviors are referenced but not reimplemented as ontology-only support-layer contracts

## Hard Exclusions (MVP)

The following are out of scope for MVP binding support contracts and must be rejected or quarantined per canonical policy:
- explicit `constraints` fields in binding canonical records
- hidden constraint semantics under renamed fields (for example: guard_policy, implied_condition, routing constraint aliases)
- compile-permissive defaults for missing identity, eligibility, or authority semantics
- inferred authority/eligibility from taxonomy, labels, structure, or metadata

## Failure and Reason-Code Boundary

When a support-layer admissibility check fails:
- structural invalidity class -> ABORT
- inadmissible binding input class -> QUARANTINE (or DENY at execution-commitment boundary)
- authorization/unknown premise class -> DENY

All non-permissive outcomes require reason-code support aligned to:
- `RC:<Stage>:<InvariantOrRule>:<Detail>`

## Compliance Checklist for Downstream Artifacts

Any downstream support-layer or compiler-bound artifact is non-compliant unless all are true:
- identifiers remain `cid:<uuidv7>`-clean for locally minted references
- ordering-dependent semantics are implemented in deterministic validators/runtime code
- MVP constraint exclusion is explicit and enforceable
- eligibility semantics are anchored to DD-005 timing and non-permissive outcomes
- Runtime 3 operational behavior is not silently absorbed into Runtime 2 support contracts

## Addendum Consideration

DD anchor placement here is interpreted with strict runtime separation: Runtime 2 support contracts are not Runtime 3 operational instantiation semantics.

## Validation Checklist (TASK-15.5)

- DD-001/DD-003/DD-004/DD-005 implications are explicit and actionable.
- ontology vs SHACL vs deterministic validator placement is explicit.
- DD-005 eligibility boundary is explicitly anchored.
- Runtime 3 operational semantics are explicitly prevented from accidental migration into Runtime 2 support contracts.
- MVP constraint exclusion boundary is explicit and testable.
