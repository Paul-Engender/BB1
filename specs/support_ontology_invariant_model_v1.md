# Support Ontology Invariant Model v1

Status: APPROVED
Owner: paul
Plan Item: P1-017
Task: TASK-17.2
Date: 2026-03-07

## Purpose

Define the support-layer invariant taxonomy for the canonical CIR set (`I1..I23`),
the non-permissive failure categories those invariants trigger, and the
reason-code alignment model required by Runtime 1 and Runtime 2.

This artifact groups invariants for support-layer use. It does not replace the
canonical invariant records in the lifecycle/control specification.

## Source Anchors

Primary canonical anchors:
- `specs/ontoForge_02_Lifecycle-Specification_v1.1.md`
- `specs/ontoForge_04_Decisions-Register_v1.1.md`
- `specs/product_runtime_instantiation_clarification_addendum_2026-03-07.md`

Companion support artifacts:
- `specs/support_ontology_csc_stage_model_v1.md`
- `specs/support_ontology_identifier_and_mvp_boundary_v1.md`
- `specs/support_ontology_governance_incorporation_model_v1.md`

## Canonical Boundary

- CIRs remain the canonical invariant records.
- This artifact defines family groupings and failure semantics for support-layer
  machine-readable use.
- UNKNOWN is an epistemic state, not a permissive outcome and not a fourth final
  disposition beside `ABORT`, `QUARANTINE`, and `DENY`.
- Runtime 3 operational enforcement is not redefined here; this model only
  defines the invariant surfaces Runtime 1 and Runtime 2 must preserve and
  reason-code consistently.

## Taxonomy Principles

1. Preserve canonical invariant IDs.
- Every grouping retains exact `I#` identity and source traceability.

2. Group by semantic role, not by file location.
- The taxonomy exists to support machine-consumable allocation later in
  `TASK-17.3`.

3. Keep non-permissive handling explicit.
- Missing required premises, identity gaps, and unsupported constraint semantics
  never become permissive by default.

4. Allow stage-local overrides where the canonical contracts require them.
- Family defaults guide modeling, but stage contracts still control the exact
  disposition at a given lifecycle boundary.

## Invariant Families

| Family ID | Family Name | Invariants | Semantic Question | Primary Stage Surface | Default Non-Permissive Outcome |
| --- | --- | --- | --- | --- | --- |
| INV-STATE | Representation and event-state integrity | I1, I2, I18, I20, I21, I22 | Has state been treated as inert where required and append-only where required? | S1, S2, S5, S6, S7 | ABORT |
| INV-CANON | Canonical-form admissibility | I6, I7, I12, I13 | Is the input admissible as binding canonical material without defaults or normative leakage? | S1, S2 | QUARANTINE |
| INV-STRUCT | Identity and kind integrity | I8, I19 | Does the primitive have explicit identity, boundaries, and correct kind/form? | S2 | ABORT |
| INV-PREMISE | Premise closure and epistemic non-defaulting | I10, I11 | Are all required premises admitted and known without permissive completion? | S2, S4, S6 | DENY |
| INV-AUTH | Authority and attribution integrity | I3, I4, I5, I14, I15 | Is authority attributable, explicit, deterministic, and never inferred from classification? | S3, S5, S6 | DENY |
| INV-SCOPE | Scope, target, and action explicitness | I16, I17, I23 | Are scope, target-set semantics, and action/effect semantics explicit and non-implicit? | S4, S6 | DENY |
| INV-COMP | Composition determinism | I9 | Are executable compositions explicit and checkable without coercion or hidden merge logic? | S6 | ABORT |

## Failure Category Model

### 1) ABORT

Use when processing cannot safely continue in the current runtime because the
candidate is structurally invalid, state-invalidating, or composition-invalid.

Typical triggers:
- identity or boundary absence (`I8`)
- kind/form mismatch (`I19`)
- append-only or recomputation break (`I20`, `I21`, `I22`)
- executable action/effect structure missing at admission (`I23` in `S2`)
- implicit coercion or merge during execution composition (`I9`)

Runtime meaning:
- Runtime 1: release candidate fails promotion/evaluation
- Runtime 2: compile candidate fails deterministically
- Runtime 3: operational proposal halts before commitment

### 2) QUARANTINE

Use when material is inadmissible as binding input but may still be retained as
non-binding commentary or descriptive residue.

Typical triggers:
- canonical record would require defaults (`I6`)
- descriptive surface restates or carries normative content (`I12`, `I13`)
- reference/version/deictic material is not fit for binding use (`I7`), unless a
  stage contract escalates the case to `ABORT`
- unsupported constraint-like expressions appear at `S1` or `S2` under `DD-004`

Runtime meaning:
- Runtime 1: semantic candidate excluded from release-binding path
- Runtime 2: tenant input fragment excluded from compile-binding path
- Runtime 3: not generally the primary outcome; by then inadmissible commentary
  should already have been kept out of binding runtime inputs

### 3) DENY

Use when a proposal or candidate is non-permissive because authority,
eligibility, admitted-premise closure, or scope/target explicitness is not
satisfied.

Typical triggers:
- authority missing or non-derivable (`I3`, `I4`, `I5`, `I15`)
- classification used to imply authority or eligibility (`I14`)
- required premises are unadmitted or unknown (`I10`, `I11`)
- scope or target semantics are implicit (`I16`, `I17`)
- executable action semantics are missing at the execution boundary (`I23` in `S6`)
- eligibility result is `ineligible` or `unknown` under `DD-005`

Runtime meaning:
- Runtime 1: candidate is non-promotable where a binding decision would require
  premises/authority not canonically satisfied
- Runtime 2: compile fails non-permissively with explicit reason codes
- Runtime 3: request/proposal is refused before execution commitment

### 4) UNKNOWN

UNKNOWN is not a final permissive result.

Rules:
- UNKNOWN must remain explicit until it is resolved or mapped to a non-permissive
  disposition.
- Under `I10`, `I11`, and `DD-005`, UNKNOWN premises and UNKNOWN eligibility are
  non-permissive.
- If UNKNOWN exists because the input is not admissible as binding material, the
  result typically resolves to `QUARANTINE`.
- If UNKNOWN exists at an operational or compile decision boundary, the result
  resolves to `DENY`.

## Stage-Local Override Rules

These are required because family defaults alone are not precise enough.

1. `I7` reference/version failures
- Family default: `INV-CANON -> QUARANTINE`
- Stage-local note: where admission cannot establish explicit identity/version
  boundaries without defaulting, stage contracts may terminate with `ABORT`.
- Support-layer rule: classify `I7` as admissibility contamination first, but do
  not suppress stage-level hard-fail behavior.

2. `I14` classification non-entailment
- Family default: `INV-AUTH -> DENY`
- Stage-local note: `I14` matters only when classification is being used to imply
  mandate/authority/eligibility. Pure descriptive classification remains
  descriptive and should not itself emit a binding denial unless misuse is
  attempted.

3. `I23` executable action semantics
- Stage-local rule is explicit in the lifecycle spec: `ABORT` at `S2`, `DENY` at
  `S6`.
- Support-layer rule: keep `I23` in the scope/target/action family but preserve
  the stage-specific split exactly.

4. Constraint handling (`DD-004`)
- Constraint-like expressions at `S1-S2` -> `QUARANTINE`
- Constraints present during `S5` issuance -> `ABORT`
- Runtime 3 execution remains bound by non-permissive handling if unsupported
  constraint semantics would otherwise be required

## Reason-Code Alignment Model

Canonical format:
- `RC:<Stage>:<InvariantOrRule>:<Detail>`

Support-layer rule:
- the first reason code must identify the primary invariant or rule family that
  caused the non-permissive result
- additional reason codes may add dependent causes but must not replace the
  primary cause

### Primary-cause alignment

| Outcome | Primary code source | Example |
| --- | --- | --- |
| ABORT | invariant ID or rule causing structural halt | `RC:S2:I8:MISSING_BOUNDARY` |
| QUARANTINE | invariant ID or `DD-004` where inadmissible binding material is isolated | `RC:S1:I12:NORMATIVE_SURFACE` |
| DENY | invariant ID or `DD-005` rule causing non-permissive refusal | `RC:S6:I11:UNKNOWN_PREMISE` |

### Detail token guidance

Use uppercase, deterministic detail tokens such as:
- `MISSING_IDENTITY`
- `MISSING_BOUNDARY`
- `UNBOUND_REFERENCE`
- `NORMATIVE_SURFACE`
- `UNSUPPORTED_CONSTRAINT`
- `UNKNOWN_PREMISE`
- `IMPLICIT_TARGET`
- `MISSING_EFFECT_SEMANTICS`
- `INELIGIBLE`

## Compact Invariant Map

| Invariant | Family | Default Outcome | Support-Layer Note |
| --- | --- | --- | --- |
| I1 | INV-STATE | ABORT | Representation changes cannot alter binding truth. |
| I2 | INV-STATE | ABORT | Observation/ingest must not commit state or side effects. |
| I3 | INV-AUTH | DENY | Authority state must be recomputable deterministically. |
| I4 | INV-AUTH | DENY | No execution without required authority at evaluation time. |
| I5 | INV-AUTH | ABORT | Authority issuance must trace to a root of trust. |
| I6 | INV-CANON | QUARANTINE | Binding forms must compile without defaults. |
| I7 | INV-CANON | QUARANTINE | Binding references must be version-clean; stage-local abort remains possible. |
| I8 | INV-STRUCT | ABORT | Identity and boundaries must be explicit. |
| I9 | INV-COMP | ABORT | Composition/coercion rules must be explicit and checkable. |
| I10 | INV-PREMISE | DENY | Unadmitted premises remain non-binding and non-permissive. |
| I11 | INV-PREMISE | DENY | Missing facts remain unknown and non-permissive. |
| I12 | INV-CANON | QUARANTINE | Descriptive surfaces must not restate policy. |
| I13 | INV-CANON | QUARANTINE | Normativity stays quarantined into governance constructs. |
| I14 | INV-AUTH | DENY | Classification never implies mandate or eligibility. |
| I15 | INV-AUTH | ABORT | Identity-to-mandate bindings require explicit join constructs/events. |
| I16 | INV-SCOPE | DENY | Scope and target sets must be explicitly named. |
| I17 | INV-SCOPE | DENY | No implicit target expansion through similarity/default inheritance. |
| I18 | INV-STATE | ABORT | Governance-relevant state change must be evented. |
| I19 | INV-STRUCT | ABORT | Form must match kind without overloading. |
| I20 | INV-STATE | ABORT | Event history remains append-only. |
| I21 | INV-STATE | ABORT | As-of recomputation must remain possible from event history. |
| I22 | INV-STATE | ABORT | AdmittedPrimitive records are append-only and versioned. |
| I23 | INV-SCOPE | DENY | Actions require explicit target/effect semantics; `S2` keeps the canonical abort override. |

## Runtime Application Notes

1. Runtime 1
- applies the taxonomy to support release candidate admissibility and promotion
  evidence
- emits rejection/quarantine outcomes as release-evaluation evidence, not as
  customer operational events

2. Runtime 2
- applies the taxonomy to tenant compile candidates under global support
  semantics
- emits deterministic compile failures with reason codes; missing semantics are
  never completed by helpful inference

3. Runtime 3
- remains the operational runtime where deny and execution-commitment semantics
  become authoritative tenant truth
- this artifact only constrains the invariant and reason-code vocabulary that
  upstream runtimes must preserve

## Output Contract For TASK-17.3

`TASK-17.3` must use this invariant model to allocate each family or invariant
surface to the correct machine form:
- ontology term
- SHACL rule
- deterministic validator/runtime logic

This document defines the semantic classes and non-permissive outcomes. It does
not yet decide the final implementation form.

## Addendum Consideration

Invariant family definitions preserve non-conflation between boundary objects and runtime-internal lifecycle candidates, with Runtime 3 operational truth explicitly out of support-only scope.

## Validation Checklist (TASK-17.2)

- `I1..I23` are grouped into explicit support-layer invariant families.
- `ABORT`, `QUARANTINE`, `DENY`, and `UNKNOWN` handling are distinguished without
  making UNKNOWN permissive.
- reason-code alignment is explicit and uses the canonical `RC:<Stage>:<InvariantOrRule>:<Detail>` format.
- stage-local overrides for `I7`, `I14`, `I23`, and `DD-004` are explicit.
- Runtime 1/2 support use is defined without collapsing into full Runtime 3
  operational behavior.
