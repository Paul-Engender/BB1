# Support Ontology Target-Scope-Action-Effect Model v1

Status: APPROVED
Owner: paul
Plan Item: P1-019
Task: TASK-19.4
Date: 2026-03-07

## Purpose

Define the Runtime-2 support ontology subset for target, scope, action, and
effect semantics required to compile tenant workflows into deterministic,
non-ambiguous control primitives.

This model hardens compile-time admissibility by forbidding implicit target
expansion and ambiguous action/effect semantics.

## Source Anchors

Primary canonical anchors:
- `specs/ontoForge_02_Lifecycle-Specification_v1.1.md`
- `specs/ontoForge_03_Product-Spec_V1.1.md`
- `specs/ontoForge_04_Decisions-Register_v1.1.md`
- `specs/product_runtime_instantiation_clarification_addendum_2026-03-07.md`

Companion support artifacts:
- `specs/support_ontology_csc_stage_model_v1.md`
- `specs/support_ontology_invariant_model_v1.md`
- `specs/support_ontology_machine_contract_map_v1.md`
- `specs/support_ontology_identifier_and_mvp_boundary_v1.md`
- `specs/support_ontology_authority_model_v1.md`
- `specs/support_ontology_operation_model_v1.md`

## Canonical Boundary

- Runtime 2 compiles target/scope/action/effect semantics into tenant-scoped
  release outputs.
- Runtime 2 does not instantiate Runtime 3 operational events or side effects.
- Runtime 3 enforces compiled semantics operationally after boundary-object load
  discipline is satisfied.

This artifact defines compile-plane semantic contracts only.

## Runtime 2 Target-Scope-Action-Effect Objective

Runtime 2 must be able to prove at compile time that:
- target sets are explicitly identified and bounded
- scope boundaries are explicit and non-overlapping where required
- actions are explicit, typed, and non-implicit
- effects are explicit, typed, and linked to actions
- missing or unknown semantics remain non-permissive

## Vocabulary Subset (Compile Plane)

The support layer must expose compile-consumable vocabulary for:

1. Target-set identity anchor
- explicit `target_set_id` semantics and identity boundary

2. Target-member reference anchor
- explicit target membership references and admissible selection basis

3. Scope boundary anchor
- explicit scope/domain boundary semantics attached to target/action semantics

4. Action semantic anchor
- explicit action identifiers and action kind typing required for compile

5. Effect semantic anchor
- explicit effect identifiers and effect kind typing

6. Action-effect linkage anchor
- explicit linkage semantics defining which effects are admissible for which
  actions

7. As-of and evaluation context anchor
- explicit as-of and context references where target/scope resolution depends on
  bounded temporal view

## Compile Contract for Target/Scope/Action/Effect

A compile candidate is inadmissible unless all required semantics are explicit.

Required compile surfaces:
- `target_set_ref`
- `scope_ref`
- `action_ref`
- `effect_ref`
- `action_effect_map_ref`

Required behavior rules:
- no implicit target expansion by similarity, hierarchy, or heuristic inference
- no implicit scope widening from parent/neighbor scope semantics
- no action defaults when action meaning is missing
- no effect defaults when effect semantics are missing
- action-effect mapping must be explicit and checkable

## Target Semantics (Runtime 2 Scope)

Target semantics must provide deterministic target identity and closure.

Rules:
- each target set must have explicit identity and boundary
- target selection semantics must be explicit and reproducible
- compile outputs must preserve target references in canonical form
- target references must be identifier-clean

Runtime 2 must reject candidates that rely on:
- inferred targets from class similarity
- undeclared target inheritance
- prose-only target descriptions without canonical references

## Scope Semantics (Runtime 2 Scope)

Scope semantics must bind target and action semantics to explicit domain
boundaries.

Rules:
- scope must be explicitly declared where required by action/effect semantics
- scope references must be explicit and non-ambiguous
- scope widening must be explicit and admissible; never implied

Runtime 2 must reject candidates where scope is:
- absent when required
- ambiguous across multiple boundaries
- implied by naming or folder placement

## Action and Effect Semantics (Runtime 2 Scope)

Action and effect semantics must be explicitly typed and linked.

Rules:
- action identity is explicit and stable
- effect identity is explicit and stable
- each action must map to declared admissible effect semantics
- missing effect semantics for executable actions is non-permissive

Runtime 2 must reject candidates that:
- define action without effect semantics
- define effect without action linkage where linkage is required
- use narrative-only action/effect meaning without canonical references

## Invariant and Decision Alignment

Invariant alignment:
- `I16` explicit scope and target-set semantics required
- `I17` no implicit target expansion
- `I23` explicit executable action/effect semantics required
- `I10`, `I11` unknown/missing premises remain non-permissive

Decision alignment:
- `DD-001` identifier hygiene for target/scope/action/effect references
- `DD-004` no constraint-field reintroduction through routing/effect aliases
- `DD-005` preserves downstream eligibility non-permissive behavior by ensuring
  compile outputs remain explicit and complete

## Non-Permissive Compile Rules

Runtime 2 must emit deterministic non-permissive outcomes when any are true:

1. Missing target semantics
- missing target-set identity or boundary
- outcome class: `ABORT` or `DENY` per stage contract

2. Implicit target expansion
- target inclusion depends on undeclared similarity/hierarchy expansion
- outcome class: `DENY`

3. Missing scope semantics
- required scope boundary absent or ambiguous
- outcome class: `ABORT` or `DENY` per stage contract

4. Missing action/effect semantics
- executable action has no explicit effect semantics or mapping
- outcome class: `ABORT` at admission-relevant boundary, `DENY` at operation
  boundary per stage contract

5. Hidden constraint semantics
- target/scope/action/effect fields encode unsupported MVP constraints
- outcome class: `QUARANTINE` or `ABORT` per stage contract

Reason-code format remains:
- `RC:<Stage>:<InvariantOrRule>:<Detail>`

## Machine-Form Allocation (Target-Scope-Action-Effect Subset)

1. Ontology terms
- target/scope/action/effect classes and relation semantics
- explicit action-effect linkage vocabulary
- controlled semantic categories for target/scope admissibility

2. SHACL rules
- required field presence/cardinality for target/scope/action/effect references
- structural validation of action-effect mapping presence
- controlled value constraints where enumerations are defined

3. Deterministic validators
- implicit-expansion rejection logic
- unknown/missing premise non-permissive handling
- stage-specific disposition selection and reason-code precedence
- cross-reference closure checks for target/scope/action/effect joins

## Boundary-Object Integration Rule

This model is consumed by Runtime 2 compilation to generate explicit target,
scope, action, and effect semantics in `SCR_TBox_Release`.

This model is not a Runtime 3 operational event schema.

Runtime 3 operational truth is instantiated only after valid runtime load
binding and runtime evaluation.

## Addendum Consideration

This artifact preserves non-conflation between:
- Runtime 2 internal compile candidates
- Runtime 2 boundary-object release outputs
- Runtime 3 operational instantiation of live proposals/events

## Acceptance Checklist (TASK-19.4)

- Explicit target/scope/action/effect semantic subsets are defined.
- No implicit target expansion rule is explicit and enforceable.
- Action-effect linkage requirements are explicit and non-defaulting.
- Invariant alignment to `I16`, `I17`, `I23` is explicit.
- Runtime 3 operational semantics remain out of scope.
- Machine-form allocation is explicit for ontology, SHACL, and validators.
