# Support Ontology Operation-Control Model v1

Status: APPROVED
Owner: paul
Plan Item: P1-019
Task: TASK-19.3
Date: 2026-03-07

## Purpose

Define the Runtime-2 support ontology subset for operation/control semantics used
at compile time to produce deterministic, tenant-scoped control outputs.

This model provides compile-safe typing for authorization, eligibility, denial,
and control-state semantics without collapsing into Runtime 3 operational event
execution.

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
- `specs/product_event_model_v1.md`

## Canonical Boundary

- Runtime 2 is a compile runtime, not an operational event ledger runtime.
- Runtime 2 emits compile outputs and compile evidence, not Runtime 3 tenant
  truth events.
- Runtime 3 authority/eligibility/execution decisions are operationally
  instantiated only after release load binding.

This artifact defines compile-time operation/control semantics only.

## Runtime 2 Operation-Control Objective

Runtime 2 must define and validate operation/control semantics needed to compile
workflow definitions into runtime-safe primitives that are:
- explicit
- non-defaulting
- reason-code capable
- boundary-clean for Runtime 3 enforcement

Runtime 2 must fail non-permissively where operation semantics are missing,
ambiguous, or implicit.

## Operation-Control Vocabulary Subset (Compile Plane)

The support layer must expose compile-consumable vocabulary for:

1. Authorization semantic anchor
- compile-level representation of authorization requirement and expected decision
  semantics (`ALLOW`/`DENY` outcome surface)

2. Eligibility semantic anchor
- compile-level representation of pre-commit eligibility state semantics
  (`eligible`, `ineligible`, `unknown`) with explicit non-permissive treatment

3. Denial semantic anchor
- explicit denial categories for compile output typing
  (`authorization_denial`, `eligibility_denial`, `quarantine`, `abort`)

4. Control-state anchor
- explicit hard-stop/resume/mode-control concept surfaces that can be compiled
  into control primitives

5. Decision reason-code anchor
- explicit reason-code category semantics compatible with
  `RC:<Stage>:<InvariantOrRule>:<Detail>`

6. Evaluation-context anchor
- explicit references for stage, scope, target-set, action, and evidence context
  that must be carried into compiled control structures

## Compile Contract for Operation Semantics

A compile candidate is inadmissible when required operation/control semantics are
absent from the candidate definition set.

Required compile surfaces:
- `authorization_semantics_ref`
- `eligibility_semantics_ref`
- `denial_semantics_ref`
- `control_state_semantics_ref`
- `reason_code_policy_ref`

Required behavior rules:
- no permissive defaults for missing operation semantics
- unknown eligibility remains non-permissive
- denial semantics must be explicit and enumerable
- control-state semantics must be explicit where runtime behavior depends on
  stop/resume/mode transitions

## Authorization Semantics (Runtime 2 Scope)

Runtime 2 authorization semantics are compile contracts, not live decisions.

Runtime 2 must ensure compiled outputs encode:
- explicit authorization decision points
- explicit deny paths
- explicit authority-reference join points (from authority model)
- explicit reason-code emission requirement for non-permissive outcomes

Runtime 2 must not:
- issue operational authorization decisions as tenant truth events
- infer authorization permissiveness from taxonomy or labels

## Eligibility Semantics (Runtime 2 Scope)

Eligibility handling must preserve DD-005 semantics in compile output typing.

Rules:
- eligibility result domain is exactly `eligible | ineligible | unknown`
- only `eligible` is permissive
- `ineligible` and `unknown` compile to non-permissive control paths
- missing eligibility semantics is non-permissive

Runtime 2 must not:
- collapse `unknown` into permissive behavior
- defer missing eligibility semantics to runtime defaults

## Denial and Control Semantics (Runtime 2 Scope)

### Denial subset

Runtime 2 must compile explicit denial classes and preserve reason-code
requirements for each class.

Minimum denial classes:
- authorization denial
- eligibility denial
- quarantine path
- abort path

### Control-state subset

Runtime 2 must compile explicit control-state references for:
- hard-stop applicability surfaces
- resume applicability surfaces
- mode transition gating surfaces

These are semantic compile anchors only. Runtime 2 does not execute
hard-stop/resume/mode transitions as operational events.

## Invariant and Decision Alignment

Invariant alignment for operation-control surfaces:
- `I4` no execution without required authority
- `I10`, `I11` premise closure and unknown non-permissive handling
- `I16`, `I17`, `I23` explicit scope/target/action/effect semantics
- `I20`, `I21` append-only and recomputation integrity are preserved as
  downstream expectations, not executed here

Decision alignment:
- `DD-004` constraints unsupported in MVP; no hidden constraint semantics in
  operation rules
- `DD-005` eligibility boundary and non-permissive unknown semantics preserved
- `DD-001` identifier cleanliness for compile references and emitted artifacts

## Non-Permissive Compile Rules

Runtime 2 must emit deterministic non-permissive outputs when any are true:

1. Missing operation semantics
- required operation/control semantic reference absent
- outcome class: `ABORT` or `DENY` per stage contract

2. Implicit operation semantics
- action/control behavior depends on unstated defaults or prose-only semantics
- outcome class: `DENY`

3. Unknown eligibility path made permissive
- candidate treats `unknown` as executable or equivalent to `eligible`
- outcome class: `DENY`

4. Missing denial classification
- non-permissive path exists but denial class/reason-code policy is undefined
- outcome class: `ABORT`

5. Hidden constraint semantics in MVP
- operation logic uses constraint-like fields outside approved boundary
- outcome class: `QUARANTINE` or `ABORT` per stage contract

Reason-code format remains:
- `RC:<Stage>:<InvariantOrRule>:<Detail>`

## Machine-Form Allocation (Operation-Control Subset)

1. Ontology terms
- authorization/eligibility/denial/control-state vocabulary
- controlled status categories and reason-code category anchors

2. SHACL rules
- structural presence/cardinality of operation semantic references
- controlled value sets for eligibility and denial classes
- structural exclusion for unsupported MVP constraint fields

3. Deterministic validators
- unknown/non-permissive decision enforcement
- reason-code primary-cause precedence
- stage-local disposition selection (`ABORT`, `QUARANTINE`, `DENY`)
- compile admissibility closure checks across authority + operation models

## Boundary-Object Integration Rule

This model is consumed by Runtime 2 compile workflows to produce
`SCR_TBox_Release` control semantics.

This model is not an operational event model and does not itself instantiate
Runtime 3 truth products.

Runtime 3 operational outcomes are instantiated only after valid load binding
against `SCR_Runtime_LoadManifest`.

## Addendum Consideration

This artifact preserves non-conflation between:
- Runtime 2 internal compile candidates
- Runtime 2 boundary object outputs
- Runtime 3 operational event instantiation

## Acceptance Checklist (TASK-19.3)

- Runtime-2 operation/control scope is explicit and compile-bounded.
- Authorization/eligibility/denial/control semantic subsets are explicit.
- DD-005 non-permissive eligibility semantics are preserved (`unknown` non-permissive).
- Runtime 3 event instantiation remains out of scope.
- Machine-form allocation is explicit for ontology, SHACL, and validator layers.
- Addendum boundary and non-conflation rules are preserved.
