# P2 Contract Delta Register v1

Status: APPROVED
Owner: paul
Plan Item: P2-001
Task: TASK-27.3
Date: 2026-03-08

## Purpose

Record only the approved P2 deltas that remain after the baseline review in
`specs/p2_contract_translation_review_v1.md`.

This register does not restate retained baseline contracts. It identifies the
specific successor gaps, the owning workstream, and whether the required output
should be a narrow addendum/new surface or a later replacement document.

## Baseline Rule

The following surfaces remain the approved execution baseline unless a delta
below explicitly requires a downstream change:
- `specs/product_event_model_v1.md`
- `specs/product_boundary_objects_v1.md`
- `specs/runtime2_compiler_contract_baseline_review_v1.md`
- `specs/runtime1_support_release_engine_v1.md`
- `specs/support_ontology_runtime2_readiness_review_v1.md`

`specs/product_runtime_mapping_v1.md` remains an approved reference input only.

## Approved P2 Deltas

| Delta ID | Gap | Current Baseline Surface | Required Output | Owner | Resolution Form | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| P2-D01 | Tenant-scope runtime handoff rules are not yet consolidated into one successor control surface | `specs/product_event_model_v1.md`; `specs/product_boundary_objects_v1.md` | `specs/product_tenant_scope_rules_v1.md` | `P2-001` via `TASK-27.4` | Narrow new surface | This is the only M1-era contract gap that must be closed before M1 can finish |
| P2-D02 | Runtime 1 successor closure criteria are not yet translated from retained baseline into P2-specific delivery criteria | `specs/runtime1_support_release_engine_v1.md` | `specs/runtime1_support_release_engine_v2.md` | `P2-002` | Downstream delta contract | `P2-002` must prove whether a full v2 replacement is required or whether a narrower addendum can satisfy the workstream intent |
| P2-D03 | Strict cross-runtime load-discipline closure remains incomplete even though boundary semantics are already defined | `specs/product_boundary_objects_v1.md`; `schemas/runtime_load_manifest.schema.json` | `specs/runtime_boundary_load_discipline_closure_v1.md`; `schemas/runtime_load_manifest.schema.json` | `P2-005` | Narrow enforcement closure | This is explicitly not a default trigger for `product_boundary_objects_v2.md` |

## Non-Deltas Confirmed By Review

The following items were reviewed and do not require an M1 replacement surface:

1. Runtime 3 event-family semantics remain sufficiently defined by `specs/product_event_model_v1.md`.
2. Boundary-object semantics remain sufficiently defined by `specs/product_boundary_objects_v1.md`.
3. Runtime 2 already has a usable baseline via `specs/runtime2_compiler_contract_baseline_review_v1.md` and `specs/support_ontology_runtime2_readiness_review_v1.md`.
4. `specs/product_runtime_mapping_v1.md` remains useful as orientation, but it is not an implementation contract output for M1.

## Replacement Rule

A replacement document is allowed only when:
- the approved delta cannot be safely absorbed by a narrow addendum or a new
  focused rule surface, and
- the owning downstream workstream records that justification explicitly.

Absent that proof, the retained baseline remains active.

## Workstream Allocation

- `P2-001` owns `P2-D01` and the M1 closure note.
- `P2-002` owns `P2-D02`.
- `P2-005` owns `P2-D03`.
- `P2-003` proceeds from the retained Runtime 2 baseline and therefore has no
  M1 contract delta recorded here.

## Register Judgment

P2 does not require a broad successor rewrite of runtime, event, or boundary
contracts.

The approved successor delta set is intentionally small:
- one M1 rule-surface gap
- one Runtime 1 downstream translation delta
- one boundary/load enforcement closure delta

## Acceptance Checklist (TASK-27.3)

- only real successor deltas are recorded
- each delta has explicit downstream ownership
- resolution form is stated for each delta
- M1/P2-005 overlap is explicitly resolved
- no blanket `v2` rewrite is implied
