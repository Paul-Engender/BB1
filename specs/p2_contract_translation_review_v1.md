# P2 Contract Translation Review v1

Status: APPROVED
Owner: paul
Plan Item: P2-001
Task: TASK-27.2
Date: 2026-03-08

## Purpose

Review the existing implementation-facing contract baseline against P2 scope and
classify what remains sufficient, what is reference-only, and what gaps still
require explicit successor outputs.

This review is a baseline judgment document. It is not a new runtime, event, or
boundary contract.

## Reviewed Inputs

Primary task inputs:
- `specs/product_runtime_mapping_v1.md`
- `specs/product_event_model_v1.md`
- `specs/product_boundary_objects_v1.md`
- `specs/runtime2_compiler_contract_baseline_review_v1.md`

Additional current-state checks:
- `specs/runtime1_support_release_engine_v1.md`
- `specs/support_ontology_runtime2_readiness_review_v1.md`
- `specs/ontoForge_03_Product-Spec_V1.1.md`
- `specs/ontoForge_04_Decisions-Register_v1.1.md`
- `bootstrap/plans/programs/post_p1_026_full_solution_program_plan_v1.md`

## P2 Scope Lens

P2 starts after support-ontology uplift closure and must deliver the first
three-runtime executable slice.

For this review, a surface is sufficient only if it can be used as a current P2
execution baseline without implying a blanket rewrite or reopening already
closed support-layer scope.

## Baseline Classification

| Surface | P2 Role | Judgment | Required Follow-on |
| --- | --- | --- | --- |
| `specs/product_runtime_mapping_v1.md` | Architectural orientation and repo-state map | RETAIN AS REFERENCE ONLY | No immediate replacement required for M1; use as context, not as the executable contract baseline |
| `specs/product_event_model_v1.md` | Runtime 3 event-family and ordering baseline | RETAIN AS EXECUTION BASELINE | No M1 rewrite required |
| `specs/product_boundary_objects_v1.md` | Cross-runtime boundary object semantics baseline | RETAIN AS EXECUTION BASELINE | No M1 rewrite required; strict load-discipline deltas remain owned by `P2-005` |
| `specs/runtime2_compiler_contract_baseline_review_v1.md` | Runtime 2 baseline review and handoff judgment | RETAIN AS EXECUTION BASELINE | Use as direct baseline input to `P2-003` decomposition |
| `specs/runtime1_support_release_engine_v1.md` | Runtime 1 current service-boundary contract | RETAIN AS EXECUTION BASELINE | Any successor change belongs in `P2-002` as explicit delta work |
| `specs/support_ontology_runtime2_readiness_review_v1.md` | Runtime 2 readiness proof | RETAIN AS EXECUTION BASELINE | No M1 rewrite required |

## Findings

### 1) `product_runtime_mapping_v1.md` remains useful, but only as orientation

`product_runtime_mapping_v1.md` still provides a valid architectural map of the
three-runtime shape and repo asset distribution. It does not, however, function
as the implementation contract that M1 is meant to approve.

It mixes durable architecture with point-in-time repo-state gap statements. Some
of those gap statements have already been reduced by later P1 work. That makes
it unsuitable as a sole execution contract for P2, but still valid as a
reference map.

Judgment:
- retain as reference input
- do not treat it as the M1 contract output
- no blanket `v2` rewrite is justified from this review alone

### 2) `product_event_model_v1.md` is sufficient for the current Runtime 3 baseline

The event model already defines the Runtime 3 event families, envelope,
partitioning, ordering, reason-code use, and execution-boundary semantics
required by the product spec and decisions register.

Nothing in P2 scope currently requires this surface to be replaced before
Runtime 3 decomposition starts. The real gap is implementation, not contract
absence.

Judgment:
- retain as active baseline for Runtime 3 event semantics
- do not open a rewrite task under M1

### 3) `product_boundary_objects_v1.md` is sufficient for boundary semantics, but not the closure of strict load discipline

The boundary object document already defines:
- the runtime chain
- the distinct boundary objects
- tenant and dependency bindings
- evidence prerequisites for downstream loading

That is enough to remain the semantic baseline for P2. The remaining issue is
not missing baseline meaning; it is stricter enforcement and closure of the
cross-runtime load discipline.

That enforcement closure belongs to `P2-005`, not to `P2-001`.

Judgment:
- retain as active baseline for boundary-object semantics
- route strict load-discipline closure to `P2-005`
- do not open `product_boundary_objects_v2.md` as an M1 default

### 4) Runtime 2 already has a usable baseline from P1

`runtime2_compiler_contract_baseline_review_v1.md` and
`support_ontology_runtime2_readiness_review_v1.md` together establish that
Runtime 2 has:
- an approved compiler contract baseline
- positive and negative readiness proof
- explicit runtime-boundary discipline

This means M1 does not need to recreate Runtime 2 contract meaning. It needs
only to confirm how these approved baselines are carried into P2 work.

Judgment:
- retain both documents as direct baseline inputs to `P2-003`
- do not restate SO-W4 or SO-W7 as successor rewrites

### 5) The real successor gap is tenant-scope runtime handoff rules

The retained baseline documents describe runtime roles, event semantics, and
boundary objects, but they do not yet consolidate tenant-scope runtime handoff
rules into one narrow successor surface.

That is the main contract gap discovered by this review.

Judgment:
- `TASK-27.4` is justified
- output should be a narrow rule surface, not a broad architecture rewrite

### 6) M1 still needs a formal delta register before any replacement document is planned

This review can classify the baseline, but it should not itself authorize full
replacement surfaces. That requires an explicit delta register showing:
- what delta exists
- why the retained baseline cannot absorb it
- which downstream workstream owns it

Judgment:
- `TASK-27.3` is justified
- replacement documents, if any, must be justified there rather than assumed here

## P2 Baseline Decision

The approved P2 execution baseline at M1 review stage is:
- `specs/product_event_model_v1.md`
- `specs/product_boundary_objects_v1.md`
- `specs/runtime2_compiler_contract_baseline_review_v1.md`
- `specs/runtime1_support_release_engine_v1.md`
- `specs/support_ontology_runtime2_readiness_review_v1.md`

`specs/product_runtime_mapping_v1.md` remains an approved reference input, not
an execution contract output.

## Successor Work Implications

1. `P2-001` should produce a delta register and tenant-scope runtime-handoff
   rules, not default to `v2` rewrites.
2. `P2-002` should treat Runtime 1 changes as explicit delta work from the
   retained Runtime 1 baseline.
3. `P2-003` can start from the approved Runtime 2 compiler baseline and
   readiness proof without reopening support-ontology scope.
4. `P2-005` owns strict boundary/load-discipline closure and any narrow boundary
   addenda needed for enforcement completeness.

## Review Judgment

P2 has a sufficient implementation-facing baseline to proceed without a blanket
contract rewrite program.

The only M1 follow-ons justified by this review are:
- an explicit delta register
- a narrow tenant-scope runtime-handoff rule surface
- a closure note confirming retained baseline plus approved deltas

## Acceptance Checklist (TASK-27.2)

- reviewed baseline surfaces are explicitly identified
- each reviewed surface is classified as retained baseline, reference-only, or
  successor gap input
- overlap between M1 and `P2-005` is explicitly resolved
- Runtime 2 baseline sufficiency is explicitly stated
- no blanket `v2` rewrite is implied
