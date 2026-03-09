# Support Ontology Validation Uplift v1

Status: APPROVED
Owner: paul
Plan Item: P1-021
Task: TASK-21.2
Date: 2026-03-07

## Purpose

Define the explicit ontology and SHACL uplift targets required to close machine-
consumable validation gaps for Runtime 2 fail-closed admissibility.

This artifact is an implementation-target backlog, not code changes.

## Source Anchors

Primary canonical anchors:
- `specs/ontoForge_02_Lifecycle-Specification_v1.1.md`
- `specs/ontoForge_03_Product-Spec_V1.1.md`
- `specs/ontoForge_04_Decisions-Register_v1.1.md`
- `specs/product_runtime_instantiation_clarification_addendum_2026-03-07.md`

Support anchors:
- `specs/support_ontology_machine_contract_map_v1.md`
- `specs/support_ontology_invariant_model_v1.md`
- `specs/runtime2_support_admissibility_matrix_v1.md`
- `ontology/kernel.ttl`
- `ontology/kernel.shacl.ttl`

## Current-State Summary

Existing kernel and SHACL provide solid base coverage for:
- target references and external identifiers
- stipulation structure and selected nature constraints
- promotion and truth assertion structural relations

Gaps remain for Runtime 2 contract surfaces introduced in SO-W3/SO-W4,
especially:
- explicit compile-plane target/scope/action/effect contracts
- explicit authorization/eligibility/denial/control semantic classes
- explicit compile provenance and dependency reference structures
- explicit SHACL coverage for first-compile required fields

## Uplift Principles

1. Ontology adds stable semantic categories and relation anchors.
2. SHACL adds structural/canonical-field presence and controlled enumerations.
3. Temporal/order/primary-cause logic remains validator-bound.
4. Runtime 3 operational event semantics remain out of scope.

## Ontology Uplift Targets

| Target ID | Required Ontology Addition | Why | Source Driver |
| --- | --- | --- | --- |
| O-UP-01 | `kern:TargetSet` class + identity properties | explicit target-set semantics for Runtime 2 compile | `I16`, `I17`, SO-W3 target model |
| O-UP-02 | `kern:ScopeBoundary` class | explicit scope semantics for compile admissibility | `I16`, SO-W3 target model |
| O-UP-03 | `kern:ActionSpecification` class | explicit action typing for compile surfaces | `I23`, SO-W3 target model |
| O-UP-04 | `kern:EffectSpecification` class | explicit effect typing and linkage | `I23`, SO-W3 target model |
| O-UP-05 | `kern:ActionEffectBinding` class + relation properties | enforce explicit action/effect mapping semantics | `I23`, SO-W4 input/output contracts |
| O-UP-06 | `kern:AuthorizationSemantic` class | compile-plane authorization semantics anchor | `I4`, SO-W3 operation model |
| O-UP-07 | `kern:EligibilitySemantic` class + status vocabulary | explicit eligibility typing (`eligible/ineligible/unknown`) | `DD-005`, SO-W3 operation model |
| O-UP-08 | `kern:DenialSemantic` class + denial kind vocabulary | deterministic denial-class references | SO-W3 operation model |
| O-UP-09 | `kern:ControlStateSemantic` class | hard-stop/resume/mode semantic anchors | SO-W3 operation model |
| O-UP-10 | `kern:CompiledControlPrimitive` class hierarchy | typed Runtime 2 output primitive families | SO-W4 output contract |
| O-UP-11 | `kern:CompileTraceReference` / provenance links | explicit source/dependency lineage anchors | SO-W4 output contract |
| O-UP-12 | `kern:ReasonCodeCategory` controlled vocabulary anchors | reason-code family typing in support layer | invariant model + DD-004 |

## SHACL Uplift Targets

| Target ID | Required SHACL Addition | Why | Source Driver |
| --- | --- | --- | --- |
| S-UP-01 | `TargetSetShape` required id + selection-basis | first-compile target semantics must be explicit | SO-W4 input contract |
| S-UP-02 | `ScopeBoundaryShape` required scope refs | required scope presence where needed | `I16`, matrix rows |
| S-UP-03 | `ActionSpecificationShape` required action id/type | no implicit action semantics | `I23` |
| S-UP-04 | `EffectSpecificationShape` required effect id/type | no implicit effect semantics | `I23` |
| S-UP-05 | `ActionEffectBindingShape` with minCount constraints | action-effect linkage required | `I23`, matrix |
| S-UP-06 | `AuthorizationSemanticShape` required refs | explicit authorization surface required | matrix |
| S-UP-07 | `EligibilitySemanticShape` with allowed status enum | enforce explicit eligibility semantics | `DD-005` |
| S-UP-08 | `DenialSemanticShape` with denial kind enum | deterministic denial class presence | matrix |
| S-UP-09 | `ControlStateSemanticShape` required refs | explicit control-state compile semantics | matrix |
| S-UP-10 | `TenantWorkflowInputShape` covering SO-W4 required fields | first-compile envelope structural gate | SO-W4 input contract |
| S-UP-11 | `CompiledControlPrimitiveShape` required lineage refs | output primitive structural completeness | SO-W4 output contract |
| S-UP-12 | MVP no-constraint shape exclusions for input/output records | DD-004 structural exclusion in shapes | `DD-004` |

## Uplift Coverage Mapping to Admissibility Matrix

- Matrix target/scope/action/effect rows -> `O-UP-01..05`, `S-UP-01..05`
- Matrix auth/eligibility/denial/control rows -> `O-UP-06..09`, `S-UP-06..09`
- Matrix evidence/dependency rows -> `O-UP-10..12`, `S-UP-10..11`
- Matrix constraint boundary row -> `S-UP-12`

## Priority Sequence

Priority-1 (needed before validator specification finalization):
- `O-UP-01..09`, `S-UP-01..10`

Priority-2 (needed for full provenance and contract hardening):
- `O-UP-10..12`, `S-UP-11..12`

## Explicit Non-Goals

Not covered by ontology/SHACL uplift:
- `(event_time, event_id)` ordering logic
- evidence sufficiency decisioning
- reason-code primary-cause precedence logic
- execution-commitment boundary logic

These remain validator/runtime requirements for `TASK-21.3`.

## Addendum Consideration

Uplift targets preserve Runtime 2 compile semantics as support contracts and do
not import Runtime 3 operational event instantiation into ontology/SHACL scope.

## Acceptance Checklist (TASK-21.2)

- ontology uplift targets are explicit and traceable
- SHACL uplift targets are explicit and traceable
- mapping from SO-W4 admissibility matrix to uplift targets is explicit
- validator-only surfaces are explicitly excluded from ontology/SHACL uplift
- addendum non-conflation boundary is preserved
