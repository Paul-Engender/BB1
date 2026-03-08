# Support Ontology Machine Contract Map v1

Status: APPROVED
Owner: paul
Plan Item: P1-017
Task: TASK-17.3
Date: 2026-03-07

## Purpose

Define which lifecycle and invariant semantics must be represented as:
- ontology terms
- SHACL rules
- deterministic validator/runtime logic

This artifact is the machine-form allocation map for the support layer used by
Runtime 1 and Runtime 2.

It does not redefine canonical lifecycle contracts, and it does not move Runtime 3
operational truth or execution-commitment behavior into ontology-only semantics.

## Source Anchors

Primary source artifacts:
- `specs/support_ontology_csc_stage_model_v1.md`
- `specs/support_ontology_invariant_model_v1.md`
- `specs/support_ontology_identifier_and_mvp_boundary_v1.md`
- `ontology/kernel.ttl`
- `ontology/kernel.shacl.ttl`

Canonical upstream anchors:
- `specs/ontoForge_02_Lifecycle-Specification_v1.1.md`
- `specs/ontoForge_04_Decisions-Register_v1.1.md`
- `specs/product_runtime_instantiation_clarification_addendum_2026-03-07.md`

## Allocation Principles

1. Vocabulary belongs in ontology.
- Stable semantic categories, governed kinds, and relation semantics belong in ontology terms.

2. Structure belongs in SHACL where possible.
- Required fields, cardinality, class membership, and coarse admissibility constraints belong in SHACL.

3. Time, ordering, evidence, and commitment belong in deterministic code.
- Anything that depends on event order, replay, evidence-chain verification,
  reason-code emission order, or execution commitment must not be left to ontology or SHACL alone.

4. Runtime 3 operational truth stays out of the support-only layer.
- Runtime 1 and Runtime 2 may reference Runtime 3-relevant concepts, but they do not instantiate
  `AuthorityEvent`, `ExecutionEvent`, or side effects.

5. Unknown remains non-permissive.
- If machine-form allocation would require hidden defaults, that semantic surface is validator-bound,
  not ontology-inferred.

## Machine Forms

### 1) ONTOLOGY_TERM

Use for:
- controlled semantic categories
- class/property anchors
- explicit lifecycle vocabulary references
- explicit invariant-family vocabulary references
- explicit non-operational support semantics consumed by Runtime 1 or Runtime 2

Must not carry:
- authority derivation by fold
- ordering decisions
- evidence sufficiency decisions
- final permissive/non-permissive runtime judgments

### 2) SHACL_RULE

Use for:
- required property presence
- max/min counts
- class membership
- enumerated value restrictions
- shape-level structural conditions that can be checked without temporal reasoning

Must not carry:
- replay/as-of logic
- load-manifest dependency evaluation
- reason-code precedence
- eligibility timing
- execution-commitment gating

### 3) DETERMINISTIC_VALIDATOR

Use for:
- ordering/replay/as-of semantics
- evidence and digest verification
- exact dependency binding checks
- reason-code emission and primary-cause precedence
- unknown-handling at decision boundaries
- eligibility timing and execution-commitment enforcement
- any non-SHACL-checkable semantic gate

## Stage Allocation Map

| Stage | Semantic Surface | Primary Machine Form | Secondary Form | Why |
| --- | --- | --- | --- | --- |
| `S1` Origination | candidate classification as descriptive/non-binding/governance-fragment | ONTOLOGY_TERM | DETERMINISTIC_VALIDATOR | ontology provides categories; validator decides when content must be quarantined rather than interpreted |
| `S1` Origination | normative-fragment detection and quarantine trigger | DETERMINISTIC_VALIDATOR | SHACL_RULE | requires rule-based detection and non-permissive outcome handling |
| `S2` Admission | primitive identity, boundary, kind, reference-closure fields | SHACL_RULE | ONTOLOGY_TERM | structural admission conditions are shape-driven over explicit classes/properties |
| `S2` Admission | identity generation, version-binding sufficiency, unknown/default checks | DETERMINISTIC_VALIDATOR | none | depends on no-default policy and identifier discipline |
| `S3` Classification | controlled subject/kind vocabulary | ONTOLOGY_TERM | SHACL_RULE | stable typing surface belongs in ontology; SHACL can constrain allowed assignments |
| `S3` Classification | anti-entailment of authority from classification (`I14`) | DETERMINISTIC_VALIDATOR | ONTOLOGY_TERM | ontology can name the categories, but preventing inferred authority is a semantic gate |
| `S4` Alignment | explicit mapping/target/scope relation vocabulary | ONTOLOGY_TERM | SHACL_RULE | mapping and scope concepts are semantic anchors with structural checks |
| `S4` Alignment | no implicit target expansion / no unadmitted premise use | DETERMINISTIC_VALIDATOR | none | requires non-defaulting and premise-closure enforcement |
| `S5` Attribution | support-layer authority vocabulary subset | ONTOLOGY_TERM | SHACL_RULE | Runtime 2 needs typed authority-related concepts without creating authority events |
| `S5` Attribution | issuance-chain verification / unsupported-constraint abort | DETERMINISTIC_VALIDATOR | none | root-of-trust and constraint boundary checks are procedural and evidence-bound |
| `S6` Operation | operation/eligibility/action/effect vocabulary subset | ONTOLOGY_TERM | SHACL_RULE | Runtime 2 needs explicit compile-safe semantics for these concepts |
| `S6` Operation | authorization, eligibility timing, unknown->deny, commit-boundary enforcement | DETERMINISTIC_VALIDATOR | none | these are temporal and runtime-bound, not ontology-computable |
| `S7` Deprecation | supersession/deprecation vocabulary | ONTOLOGY_TERM | SHACL_RULE | append-only supersession terms and shape constraints are declarable |
| `S7` Deprecation | append-only history verification / as-of replay sufficiency | DETERMINISTIC_VALIDATOR | none | requires historical integrity checks and replay guarantees |

## Invariant Family Allocation Map

| Family | Primary Machine Form | Secondary Form | Allocation Rule |
| --- | --- | --- | --- |
| `INV-STATE` | DETERMINISTIC_VALIDATOR | ONTOLOGY_TERM | ontology may name state/history concepts, but append-only, replay, and event-state integrity require procedural verification |
| `INV-CANON` | DETERMINISTIC_VALIDATOR | ONTOLOGY_TERM | ontology may name admissibility/non-binding categories; validator decides quarantine and no-default failures |
| `INV-STRUCT` | SHACL_RULE | ONTOLOGY_TERM | identity/boundary/kind requirements are primarily structural over explicit classes/properties |
| `INV-PREMISE` | DETERMINISTIC_VALIDATOR | ONTOLOGY_TERM | premise admission and unknown/non-permissive handling require explicit decision logic |
| `INV-AUTH` | DETERMINISTIC_VALIDATOR | ONTOLOGY_TERM | ontology defines authority-related vocabulary subset; derivation and denial remain validator/runtime concerns |
| `INV-SCOPE` | SHACL_RULE | DETERMINISTIC_VALIDATOR | explicit scope/target/action/effect presence can be shaped, but implicit-expansion and stage-local deny logic require validators |
| `INV-COMP` | DETERMINISTIC_VALIDATOR | SHACL_RULE | some composition prerequisites can be shaped, but final composition admissibility is semantic and non-defaulting |

## Concrete Allocation By Canonical Surface

### Ontology-Term Targets

These should exist as classes/properties/controlled individuals in the support layer:
- lifecycle stage vocabulary references for `S1..S7`
- invariant-family vocabulary (`INV-STATE`, `INV-CANON`, `INV-STRUCT`, `INV-PREMISE`, `INV-AUTH`, `INV-SCOPE`, `INV-COMP`)
- non-binding vs binding-candidate semantic categories
- subject/kind taxonomy anchors used by Runtime 1 and Runtime 2
- explicit target-set, scope, action, effect, authority-subset, eligibility-subset, and supersession vocabulary
- reason-code category vocabulary where useful as typed reference classes, but not final reason-code generation logic

### SHACL Targets

These should be enforced structurally in shape form where feasible:
- identity/boundary/kind presence for admitted primitives
- required target/scope/action/effect property presence
- mandatory support-release payload membership structure
- required fields for support-layer artifacts and compile-input examples
- coarse exclusion of unsupported structural constraint fields in MVP
- class and cardinality restrictions for support-layer semantic bundles

### Deterministic Validator Targets

These must remain code-level checks:
- `cid:<uuidv7>` and version-binding validation
- `(event_time, event_id)` ordering and replay rules
- evidence presence and digest verification
- exact dependency binding between releases
- unknown/non-permissive decision handling
- `ABORT` / `QUARANTINE` / `DENY` reason-code emission with primary-cause precedence
- `DD-004` constraint handling beyond structural absence checks
- `DD-005` eligibility timing and `unknown -> DENY` behavior
- Runtime 3 load-binding checks and execution-commitment semantics

## Current Kernel / SHACL Fit Assessment

### Already present in `ontology/kernel.ttl`

The current kernel already provides useful anchors for:
- information-bearing artefacts
- target references and external identifiers
- stipulations and stipulation natures
- evidence records and promotion records
- role and role-assignment vocabulary

These support:
- ontology-term allocation for semantic categories
- some SHACL structural checks already present in `kernel.shacl.ttl`

### Already present in `ontology/kernel.shacl.ttl`

Current shapes already cover:
- `TargetReference`
- `ExternalIdentifier`
- `Stipulation`
- `PromotionRecord`
- `TruthAssertion`

This means the repo already supports some `INV-STRUCT` and support-payload structural enforcement.

### Still validator-bound despite ontology/SHACL presence

The following remain explicitly outside ontology-only or SHACL-only sufficiency:
- exact admission/no-default judgments
- evidence completeness
- dependency-chain admissibility
- reason-code generation
- authority/eligibility timing semantics
- append-only/replay verification

## Addendum Consideration

Machine-form allocation keeps Runtime 2 compile semantics separate from Runtime 3 operational instantiation per the runtime-instantiation addendum.

## Non-Goals and Hard Exclusions

This map does not allocate the following to ontology-only semantics:
- Runtime 3 `AuthorityEvent` production
- Runtime 3 `ExecutionEvent` production
- side-effect commitment
- fold-based authority derivation
- as-of operational recomputation as a pure ontology function
- permissive completion of missing target, authority, identity, or eligibility semantics

## Implementation Guidance For Downstream Work

1. Runtime 1
- use ontology plus SHACL to declare and structurally validate support-release payloads
- use validators for promotion evidence, payload admissibility, and non-permissive closure

2. Runtime 2
- consume ontology terms and SHACL shapes as compile-time semantic contract surfaces
- use validators for ambiguity rejection, premise closure, dependency binding, and deterministic failure outputs

3. Runtime 3
- consume compiled outputs and load manifests through validator/runtime gates
- do not treat support ontology terms as a substitute for operational event logic

## Done Test For This Artifact

This artifact is complete only if all are true:
- every lifecycle stage surface is allocated to a declared machine form
- every invariant family has a primary machine form
- the ontology/SHACL/validator split is explicit and non-overlapping enough to implement
- Runtime 3 operational semantics are not silently migrated into Runtime 2 support contracts
- the map is consistent with `DD-004`, `DD-005`, and the runtime-instantiation addendum

## Validation Checklist (TASK-17.3)

- every mapped semantic has a declared implementation form
- lifecycle stage surfaces and invariant families are both covered
- current kernel and SHACL assets are assessed against the allocation map
- validator-only surfaces are explicit where temporal, evidentiary, or commitment logic is involved
