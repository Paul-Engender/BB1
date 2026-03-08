# Runtime 2 Compiled Primitive Emission Contract v1

Status: APPROVED
Owner: paul
Plan Item: P2-003
Task: TASK-29.4
Date: 2026-03-08

## Purpose

Translate the approved Runtime 2 compiled-output baseline into
implementation-facing primitive emission, lineage, evidence, and release
assembly controls.

This artifact defines the compiler back-door contract. It does not define
Runtime 3 operational instantiation.

## Baseline Inputs

- `specs/runtime2_compiled_control_primitives_v1.md`
- `specs/runtime2_compiler_module_boundary_v1.md`
- `specs/product_boundary_objects_v1.md`
- `specs/product_tenant_scope_rules_v1.md`

## Compiler Back-Door Boundary

Runtime 2 primitive emission begins only after a compile request has passed the
front-door ingest/admissibility contract.

The emission boundary therefore accepts only an admitted normalized compile
model containing:
- exact tenant identity
- exact support-release dependency identity and version
- explicit target, scope, action, effect, authorization, eligibility, denial,
  control-state, and AI-operable references
- source input lineage references
- deterministic compile configuration

If any required field is missing at this stage, compilation must fail rather
than infer missing output semantics.

## Required Emission Stages

Runtime 2 back-door processing must follow this fixed order:
1. normalized compile model intake
2. required primitive-family construction
3. primitive-record completeness enforcement
4. lineage and dependency binding
5. compile evidence emission
6. `SCR_TBox_Release` package assembly

No later stage may repair semantic omissions from an earlier stage.

## Required Primitive Families

The first implementation must emit all required primitive families from the
approved baseline:
- `TargetScopePrimitive`
- `ActionEffectPrimitive`
- `AuthorizationPrimitive`
- `EligibilityPrimitive`
- `DenialPrimitive`
- `ControlStatePrimitive`
- `TracePrimitive`

Rules:
- all families are mandatory for a successful first-slice compile
- family omission is an `ABORT`
- placeholder or narrative-only primitives are inadmissible

## Primitive Record Contract

Each emitted primitive record must include the required fields from the approved
baseline:
- `primitive_id`
- `primitive_type`
- `tenant_id`
- `workflow_id`
- `scope_ref`
- `target_set_ref`
- `action_ref`
- `effect_ref`
- `authorization_ref`
- `eligibility_ref`
- `denial_ref`
- `support_release_ref`
- `source_input_ref`
- `compile_reason_code_policy_ref`

Optional but governed fields:
- `supersedes_primitive_id`
- `valid_from`
- `valid_to`

Rules:
- no required field may be inferred or backfilled from prose
- all references must be identifier-clean and dependency-resolvable
- incomplete primitive records are non-permissive

## Lineage and Dependency Binding

Before release assembly, Runtime 2 must bind each primitive to:
- exact admitted tenant input reference(s)
- exact `SupportOntologyRelease` dependency reference
- compile decision/evidence reference(s)

Rules:
- primitive emission without exact support-release lineage is inadmissible
- primitive emission without source-input lineage is inadmissible
- ambiguous or many-to-many lineage that cannot be traced deterministically is
  non-permissive

## Compile Evidence Contract

A successful compile must emit deterministic evidence payloads sufficient for
later release admissibility and audit.

The evidence payload must include, at minimum:
- compile request metadata
- admitted/dependency-bound input summary
- matrix/gate evaluation outcome summary
- primitive-family completeness summary
- compile decision status
- reason-code policy mapping reference

Rules:
- evidence emission is mandatory for successful compile
- evidence omission is an `ABORT`
- evidence must be hash-bindable into the release manifest

## SCR_TBox_Release Assembly Contract

`release.py` must assemble a tenant-scoped `SCR_TBox_Release` with all of the
following explicit properties:
- `artifact_type = SCR_TBox_Release`
- `tenant_scope = tenant`
- exact `tenant_id`
- exact dependency reference to `SupportOntologyRelease`
- compiled primitive payload
- compile evidence payload
- release-manifest file hashes and evidence hashes

Rules:
- Runtime 2 introduces tenant scope at release assembly time
- release packaging must reuse shared boundary-object packaging substrate where
  possible
- package assembly must not emit or imply a Runtime 3 load manifest
- package assembly must not emit Runtime 3 authority or execution events

## Non-Permissive Output Rules

Compilation must fail when any of the following are true:
1. a required primitive family is missing
2. a primitive record is incomplete
3. output meaning depends on implicit defaults or inference
4. support-release dependency binding is missing or ambiguous
5. source-input lineage is missing or ambiguous
6. compile evidence is absent from the release package

Outcome classes:
- `ABORT` for structural omission or dependency/evidence failure
- `DENY` where output would otherwise depend on implicit semantics

## Implementation Guidance

1. `primitive_emit.py` should build primitives only from the normalized admitted
   compile model.
2. `evidence.py` should remain separate so evidence obligations stay testable.
3. `release.py` should remain a packaging boundary, not a semantic decision
   engine.
4. Runtime 3 load-binding and operational event creation remain outside the
   Runtime 2 emission contract.

## Acceptance Checklist (TASK-29.4)

- required primitive families are explicit
- primitive record completeness rules are explicit
- lineage and dependency binding rules are explicit
- evidence obligations are explicit
- `SCR_TBox_Release` assembly rules are explicit
- Runtime 3 outputs are explicitly excluded


