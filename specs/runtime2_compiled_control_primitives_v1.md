# Runtime 2 Compiled Control Primitives Contract v1

Status: APPROVED
Owner: paul
Plan Item: P1-020
Task: TASK-20.3
Date: 2026-03-07

## Purpose

Define the canonical output contract for Runtime 2 compiled control primitives
emitted into tenant-scoped `SCR_TBox_Release` artifacts.

This contract specifies what must be present, explicit, and hash-bound so
Runtime 3 can load and enforce semantics without inference.

## Source Anchors

Primary canonical anchors:
- `specs/ontoForge_03_Product-Spec_V1.1.md`
- `specs/ontoForge_04_Decisions-Register_v1.1.md`
- `specs/ontoForge_02_Lifecycle-Specification_v1.1.md`
- `specs/product_runtime_instantiation_clarification_addendum_2026-03-07.md`

Upstream contract anchors:
- `specs/runtime2_tenant_workflow_input_contract_v1.md`
- `specs/product_boundary_objects_v1.md`
- `specs/support_ontology_release_payload_contract_v1.md`
- `specs/support_ontology_operation_model_v1.md`
- `specs/support_ontology_target_scope_action_model_v1.md`
- `specs/support_ontology_authority_model_v1.md`

## Canonical Boundary

- Runtime 2 emits tenant-scoped boundary objects (`SCR_TBox_Release`).
- Runtime 2 does not emit Runtime 3 operational truth events.
- Runtime 3 consumes compiled primitives through load-binding discipline.

This artifact defines output contract semantics only.

## Output Object Scope

`SCR_TBox_Release` compiled output must represent only tenant-scoped, compile-
admitted control semantics produced from:
- admitted tenant workflow input
- exact `SupportOntologyRelease` dependency binding
- deterministic compile checks

No output semantics are admissible if they require implicit defaults or
unstated upstream assumptions.

## Compiled Primitive Families (Required)

Runtime 2 output must include explicit primitive families for first compile:

1. `TargetScopePrimitive`
- normalized target set and scope boundary semantics

2. `ActionEffectPrimitive`
- explicit action/effect typing and linkage semantics

3. `AuthorizationPrimitive`
- compile-time authorization evaluation surface and deny-path semantics

4. `EligibilityPrimitive`
- explicit eligibility semantics (`eligible | ineligible | unknown`) with
  non-permissive treatment of non-eligible states

5. `DenialPrimitive`
- deterministic denial classifications and reason-code obligations

6. `ControlStatePrimitive`
- hard-stop/resume/mode-control compile semantics (non-operational surface)

7. `TracePrimitive`
- provenance references linking primitive derivation to tenant input and support
  dependencies

## Primitive Record Contract

Each compiled primitive record is inadmissible unless required fields are
present and explicit:

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

Field rules:
- no required field may be inferred
- unknown required values are non-permissive
- references must be identifier-clean and dependency-resolvable

## SCR_TBox_Release Output Envelope

Compiled output package must include, at minimum:

1. Release manifest contract fields
- `artifact_type = SCR_TBox_Release`
- `tenant_scope = tenant`
- `tenant_id` present and stable
- exact `SupportOntologyRelease` dependency reference

2. Compiled primitive payload
- explicit compiled primitive set containing required primitive families
- canonical references linking primitives to source tenant inputs

3. Compile evidence payload
- deterministic compile evidence files with hash entries in manifest
- evidence required for load admissibility

4. Reason-code mapping payload
- deterministic mapping for non-permissive compile outcomes

## Dependency and Provenance Contract

Each compiled primitive must be traceable to:
- exact admitted tenant input reference(s)
- exact support release dependency reference
- compile decision/evidence references

Runtime 2 outputs are inadmissible if dependency or source lineage is missing,
ambiguous, or hash-invalid.

## Non-Permissive Output Rules

Runtime 2 must fail compilation when any are true:

1. Missing primitive family
- required primitive family absent
- outcome class: `ABORT`

2. Incomplete primitive record
- required primitive fields missing
- outcome class: `ABORT` or `DENY` per stage contract

3. Implicit semantics in output
- primitive meaning depends on unstated default or inference
- outcome class: `DENY`

4. Dependency chain ambiguity
- support-release dependency not exact or unresolved
- outcome class: `ABORT`

5. Evidence omission
- compile evidence missing from release payload/manifests
- outcome class: `ABORT`

Reason-code format:
- `RC:<Stage>:<InvariantOrRule>:<Detail>`

## Runtime 3 Load Meaning Contract

Compiled primitives must carry sufficient explicit meaning so Runtime 3 can:
- load without consulting prose/spec narrative
- enforce decisions without inferring missing semantics
- preserve tenant and dependency chain discipline

This does not imply Runtime 2 emits Runtime 3 operational events.
It only ensures compiled outputs are operationally interpretable.

## Invariant and Decision Alignment

Invariant alignment:
- `I10`, `I11` premise closure and unknown non-permissive handling
- `I14` no inferred authority from classification
- `I16`, `I17`, `I23` explicit scope/target/action/effect semantics
- `I20`, `I21` append-only and replay integrity preserved via package/evidence
  discipline

Decision alignment:
- `DD-001` identifier hygiene
- `DD-002` release packaging discipline
- `DD-004` no MVP constraint reintroduction
- `DD-005` eligibility non-permissive boundary
- `DD-007` global doctrine over tenant workflows

## Addendum Consideration

This contract preserves non-conflation between:
- Runtime 2 internal compile candidates
- Runtime 2 boundary object outputs (`SCR_TBox_Release`)
- Runtime 3 operational instantiation (`AuthorityEvent`, `ExecutionEvent`, etc.)

## Acceptance Checklist (TASK-20.3)

- required compiled primitive families are explicit
- primitive record required fields are explicit and non-defaulting
- output envelope requirements for manifest/payload/evidence are explicit
- dependency and provenance rules are explicit
- non-permissive output rules are explicit and reason-code aligned
- addendum boundary discipline is preserved
