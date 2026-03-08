# Support Ontology TTL Inventory v1

Status: IS
Owner: paul
Plan Item: P1-015
Task: TASK-15.1
Date: 2026-03-07

## Purpose

Create a complete inventory of existing `.ttl` assets in current repository scope and assign a proposed role classification for downstream admission decisions.

This document is an inventory and classification artifact only. It does not approve any `.ttl` file for binding use.

## Scope Rule

Inventory scope for TASK-15.1:
- `ontology/*.ttl`
- `ontology/examples/*.ttl`
- `ontology/negative_examples/*.ttl`

Additional `.ttl` files outside the above scope are listed under triage findings for explicit treatment in `TASK-15.2`.

## Inventory Summary

- Core ontology sources in `ontology/`: 4
- Positive example fixtures in `ontology/examples/`: 3
- Negative example fixtures in `ontology/negative_examples/`: 6
- Total in-scope inventory rows: 13

## In-Scope TTL Inventory

| Row | Path | Class | Proposed Role | Binding Candidate | Notes |
| --- | --- | --- | --- | --- | --- |
| TTL-001 | `ontology/kernel.ttl` | Core source ontology | Canonical support-kernel vocabulary candidate | YES | Candidate primary semantic source for Runtime-1 and Runtime-2 upstream contract, subject to explicit approval. |
| TTL-002 | `ontology/kernel.shacl.ttl` | Core source shape contract | Canonical structural/admissibility shape contract candidate | YES | Candidate SHACL constraint layer for support-kernel contract, subject to explicit approval. |
| TTL-003 | `ontology/support.ttl` | Core source ontology (minimal) | Transitional/placeholder support payload | CONDITIONAL | Currently used as packaged payload; classification indicates placeholder risk and requires explicit approval outcome. |
| TTL-004 | `ontology/scr_tbox.ttl` | Core source ontology | SCR TBox prototype substrate | CONDITIONAL | Candidate for Runtime-2 boundary work; not admissible for binding compile path until explicitly approved. |
| TTL-005 | `ontology/examples/example-target-reference.ttl` | Positive fixture | Positive validation corpus | NO (fixture-only) | Keep as fixture-only unless explicitly promoted into binding examples set. |
| TTL-006 | `ontology/examples/example-stipulation.ttl` | Positive fixture | Positive validation corpus | NO (fixture-only) | Keep as fixture-only unless explicitly promoted into binding examples set. |
| TTL-007 | `ontology/examples/example-promotion-chain.ttl` | Positive fixture | Positive validation corpus | NO (fixture-only) | Keep as fixture-only unless explicitly promoted into binding examples set. |
| TTL-008 | `ontology/negative_examples/evaluator_missing_measurementspec.ttl` | Negative fixture | Negative validation corpus | NO (fixture-only) | Fail-case fixture for SHACL behavior checks. |
| TTL-009 | `ontology/negative_examples/promotionrecord_two_truthassertions.ttl` | Negative fixture | Negative validation corpus | NO (fixture-only) | Fail-case fixture for cardinality guardrails. |
| TTL-010 | `ontology/negative_examples/restriction_missing_ruleexpression.ttl` | Negative fixture | Negative validation corpus | NO (fixture-only) | Fail-case fixture for mandatory expression checks. |
| TTL-011 | `ontology/negative_examples/stipulation_two_stipulateson.ttl` | Negative fixture | Negative validation corpus | NO (fixture-only) | Fail-case fixture for single-target requirement. |
| TTL-012 | `ontology/negative_examples/targetref_missing_isaboutentity.ttl` | Negative fixture | Negative validation corpus | NO (fixture-only) | Fail-case fixture for target anchor completeness. |
| TTL-013 | `ontology/negative_examples/targetref_two_isaboutentity.ttl` | Negative fixture | Negative validation corpus | NO (fixture-only) | Fail-case fixture for single anchor mapping semantics. |

## Out-of-Scope Triage Findings

The following `.ttl` files exist in repository storage but are outside TASK-15.1 scope inputs. They are not treated as admissible sources by this inventory.

| Row | Path | Observed Class | Proposed Treatment |
| --- | --- | --- | --- |
| TTL-X01 | `dist/SupportOntologyRelease-v0.2.0/_promotion_verify/ontology/support.ttl` | Derived/extracted runtime artifact | Non-binding derived copy; exclude from admission decisions. |
| TTL-X02 | `dist/tmp_load_support_v020/ontology/support.ttl` | Temporary load artifact | Non-binding temporary file; exclude from admission decisions. |
| TTL-X03 | `dist/tmp_load_so/ontology/support.ttl` | Temporary load artifact | Non-binding temporary file; exclude from admission decisions. |
| TTL-X04 | `dist/tmp_load_scr/ontology/scr_tbox.ttl` | Temporary load artifact | Non-binding temporary file; exclude from admission decisions. |
| TTL-X05 | `statements.ttl` | Unclassified top-level ontology/shape content | Requires explicit triage in TASK-15.2 before any binding or fixture usage. Default state: non-binding. |

## Admission Precondition Statement

Per approved support-ontology protocol:
- no `.ttl` file in this inventory is automatically approved for binding use
- binding use requires explicit user approval in `specs/support_ontology_ttl_admission_register_v1.md`
- until then, all rows are treated as non-binding for constitutional and compile-gate purposes

## Task Closure Check

TASK-15.1 completion criteria met by this artifact:
- all in-scope `.ttl` files are enumerated exactly once
- each row has a proposed role classification
- out-of-scope `.ttl` findings are explicitly quarantined from implicit admission
