# Support Ontology TTL Admission Register v1

Status: APPROVED
Owner: paul
Plan Item: P1-015
Task: TASK-15.2
Date: 2026-03-07

## Purpose

Record explicit per-file admission decisions for all known `.ttl` assets so no file enters a binding path without user approval.

This register is the sole approval control for `.ttl` admission in support-layer binding flows.

## Decision States

Allowed `admission_state` values:
- `APPROVED`: allowed for binding use in the declared scope
- `NOT_APPROVED`: explicitly rejected for binding use
- `NON_BINDING`: allowed only as non-binding reference or fixture
- `RETIRE`: remove from active use and phase out

## Binding Scope Classes

- `CORE_BINDING`: canonical support contract and shape artifacts
- `FIXTURE_POSITIVE`: positive test/example fixture only
- `FIXTURE_NEGATIVE`: negative test fixture only
- `DERIVED_RUNTIME`: generated/extracted runtime artifact copy
- `UNCLASSIFIED`: requires triage before any use

## Admission Matrix (Approved)

| Row | Path | Binding Scope Class | Approved State | Effective State | Decision Record | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| TTL-001 | `ontology/kernel.ttl` | CORE_BINDING | APPROVED | APPROVED | PAUL_APPROVED_2026-03-07 | Canonical support-kernel vocabulary source candidate admitted for binding use. |
| TTL-002 | `ontology/kernel.shacl.ttl` | CORE_BINDING | APPROVED | APPROVED | PAUL_APPROVED_2026-03-07 | Canonical structural/admissibility shape contract admitted for binding use. |
| TTL-003 | `ontology/support.ttl` | CORE_BINDING | NOT_APPROVED | NOT_APPROVED | PAUL_APPROVED_2026-03-07 | Transitional placeholder payload not admitted for binding use. |
| TTL-004 | `ontology/scr_tbox.ttl` | CORE_BINDING | NON_BINDING | NON_BINDING | PAUL_APPROVED_2026-03-07 | Runtime-2 prototype substrate remains non-binding for now. |
| TTL-005 | `ontology/examples/example-target-reference.ttl` | FIXTURE_POSITIVE | NON_BINDING | NON_BINDING | PAUL_APPROVED_2026-03-07 | Fixture-only; explicitly not release payload. |
| TTL-006 | `ontology/examples/example-stipulation.ttl` | FIXTURE_POSITIVE | NON_BINDING | NON_BINDING | PAUL_APPROVED_2026-03-07 | Fixture-only; explicitly not release payload. |
| TTL-007 | `ontology/examples/example-promotion-chain.ttl` | FIXTURE_POSITIVE | NON_BINDING | NON_BINDING | PAUL_APPROVED_2026-03-07 | Fixture-only; explicitly not release payload. |
| TTL-008 | `ontology/negative_examples/evaluator_missing_measurementspec.ttl` | FIXTURE_NEGATIVE | NON_BINDING | NON_BINDING | PAUL_APPROVED_2026-03-07 | Negative fixture-only; explicitly not release payload. |
| TTL-009 | `ontology/negative_examples/promotionrecord_two_truthassertions.ttl` | FIXTURE_NEGATIVE | NON_BINDING | NON_BINDING | PAUL_APPROVED_2026-03-07 | Negative fixture-only; explicitly not release payload. |
| TTL-010 | `ontology/negative_examples/restriction_missing_ruleexpression.ttl` | FIXTURE_NEGATIVE | NON_BINDING | NON_BINDING | PAUL_APPROVED_2026-03-07 | Negative fixture-only; explicitly not release payload. |
| TTL-011 | `ontology/negative_examples/stipulation_two_stipulateson.ttl` | FIXTURE_NEGATIVE | NON_BINDING | NON_BINDING | PAUL_APPROVED_2026-03-07 | Negative fixture-only; explicitly not release payload. |
| TTL-012 | `ontology/negative_examples/targetref_missing_isaboutentity.ttl` | FIXTURE_NEGATIVE | NON_BINDING | NON_BINDING | PAUL_APPROVED_2026-03-07 | Negative fixture-only; explicitly not release payload. |
| TTL-013 | `ontology/negative_examples/targetref_two_isaboutentity.ttl` | FIXTURE_NEGATIVE | NON_BINDING | NON_BINDING | PAUL_APPROVED_2026-03-07 | Negative fixture-only; explicitly not release payload. |
| TTL-X01 | `dist/SupportOntologyRelease-v0.2.0/_promotion_verify/ontology/support.ttl` | DERIVED_RUNTIME | RETIRE | RETIRE | PAUL_APPROVED_2026-03-07 | Derived copy; permanently retired from admission scope. |
| TTL-X02 | `dist/tmp_load_support_v020/ontology/support.ttl` | DERIVED_RUNTIME | RETIRE | RETIRE | PAUL_APPROVED_2026-03-07 | Temporary artifact; permanently retired from admission scope. |
| TTL-X03 | `dist/tmp_load_so/ontology/support.ttl` | DERIVED_RUNTIME | RETIRE | RETIRE | PAUL_APPROVED_2026-03-07 | Temporary artifact; permanently retired from admission scope. |
| TTL-X04 | `dist/tmp_load_scr/ontology/scr_tbox.ttl` | DERIVED_RUNTIME | RETIRE | RETIRE | PAUL_APPROVED_2026-03-07 | Temporary artifact; permanently retired from admission scope. |
| TTL-X05 | `statements.ttl` | UNCLASSIFIED | NOT_APPROVED | NOT_APPROVED | PAUL_APPROVED_2026-03-07 | Not approved until dedicated triage/provenance review. |

## Approval Log

| Date | Approver | Decision Scope | Decision Summary | Register Updated By |
| --- | --- | --- | --- | --- |
| 2026-03-07 | paul | TTL-001..004, TTL-005..013, TTL-X01..X05 | CORE: approve TTL-001/002, TTL-003 not approved, TTL-004 non-binding; FIXTURES non-binding fixture-only and excluded from release payload; DERIVED retired; UNCLASSIFIED not approved pending triage. | codex |

## Enforcement Rules

- Only `APPROVED` rows are admissible for binding support-layer use.
- `NON_BINDING` rows may be used for controlled evaluation/fixture roles only.
- `FIXTURE_POSITIVE` and `FIXTURE_NEGATIVE` rows are explicitly excluded from release payload composition.
- `RETIRE` rows are not admissible as semantic sources.
- `NOT_APPROVED` rows are blocked until explicit future decision supersedes this register.
