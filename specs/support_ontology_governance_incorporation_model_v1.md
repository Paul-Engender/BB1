# Support Ontology Governance Incorporation Model v1

Status: APPROVED
Owner: paul
Plan Item: P1-015
Task: TASK-15.3
Date: 2026-03-07

## Purpose

Define how governance semantics (belief, risk, objective) are incorporated into the support ontology layer as machine-usable contracts without relocating constitutional authority.

This model is the binding translation boundary between:
- constitutional sources (doctrine, lifecycle, decisions), and
- executable support-layer contracts consumed by Runtime 1 and Runtime 2.

## Canonical Authority Boundary

Constitutional authority remains in:
- `specs/ontoForge_01_Doctrine_v1.1.md`
- `specs/ontoForge_02_Lifecycle-Specification_v1.1.md`
- `specs/ontoForge_04_Decisions-Register_v1.1.md`

Runtime behavior alignment comes from:
- `specs/ontoForge_03_Product-Spec_V1.1.md`
- `specs/product_runtime_instantiation_clarification_addendum_2026-03-07.md`

Binding rule:
- doctrine text is non-operational by default
- doctrine content influences runtime only after explicit operationalization into canonical contracts with traceability
- prose never becomes executable control by presence, placement, label, or metadata

## Binding Design Principles

1. Constitutional source first.
- No support-layer semantic term, shape, or validator rule exists without source anchor(s).

2. Translation is explicit.
- Governance content is transformed into typed machine forms, never interpreted ad hoc.

3. Non-permissive unknowns.
- Missing required governance semantics yield non-permissive outcomes.

4. No defaulted constraints in MVP.
- DD-004 boundary applies: constraints are unsupported in MVP and must not be reintroduced under renamed constructs.

5. Runtime boundary integrity.
- Runtime 2 receives only the subset needed for compile-safe semantics.
- Full Runtime 3 operational event semantics are not pulled into support-layer scope under this task.

## Governance Translation Contract

### A) Belief incorporation

Beliefs become binding only through explicit canonicalized support-layer contracts.

Belief translation outputs may include:
- ontology vocabulary terms (typed governance concepts)
- SHACL structural admissibility rules
- deterministic validator requirements (when ordering/as-of semantics are required)

Belief translation constraints:
- no free-text doctrine execution
- no implicit authority or eligibility inference
- no identity/classification to mandate entailment

### B) Risk incorporation

Risks are represented as explicit failure surfaces, not commentary.

Risk translation outputs may include:
- invariant/failure classes
- gate failure conditions
- reason-code families and required emission rules

Failure handling aligns with decisions/lifecycle policy:
- structural invalidity -> ABORT
- inadmissible binding input -> QUARANTINE (or DENY at execution boundary)
- authorization/unknown premises -> DENY

### C) Objective incorporation

Objectives are represented as explicit, checkable semantic contract requirements.

Objective translation outputs may include:
- target semantics
- action/effect semantics
- scope semantics
- measurement/verification linkage

Objective translation constraints:
- no implicit target expansion
- no permissive defaults for missing objective inputs
- no objective text as execution authorization

## Required Traceability Fields

Each support-layer governance contract unit MUST carry:
- `governance_unit_id`: stable internal ID
- `source_doc_id`: one of ontoForge_01/02/03/04
- `source_clause_ref`: source section/record reference
- `source_belief_ids`: zero or more B# anchors (required where applicable)
- `decision_anchor_ids`: zero or more DD-00# anchors (required where applicable)
- `csc_stage_scope`: relevant lifecycle stages (S1..S7) or `N/A`
- `binding_mode`: `NON_BINDING` | `BINDING_CANDIDATE` | `BINDING_APPROVED`
- `machine_form`: `ONTOLOGY_TERM` | `SHACL_RULE` | `DETERMINISTIC_VALIDATOR`
- `failure_mode`: `ABORT` | `QUARANTINE` | `DENY` | `N/A`
- `reason_code_family`: `RC:<Stage>:<InvariantOrRule>:<Detail>` or `N/A`

No governance unit is binding if traceability fields are incomplete.

## Machine-Form Allocation Rules

Use this allocation to prevent semantic bleed between ontology and runtime logic.

1. ONTOLOGY_TERM
- use for stable vocabulary and relation semantics
- avoid temporal fold logic and ordering-sensitive derivations

2. SHACL_RULE
- use for structural admissibility and cardinality/shape constraints
- avoid as-of replay, authority derivation, and event-order dependent evaluation

3. DETERMINISTIC_VALIDATOR
- use for ordering-dependent, replay/as-of, authority derivation, eligibility timing, and evidence-chain checks
- use where DD-003/DD-005 semantics require explicit sequence behavior

## Runtime Boundary Allocation

1. Runtime 1 (Support Ontology Engine)
- evaluates support release candidates against approved semantic contracts
- emits evidence-bound release artifacts
- does not create tenant authority or execution records

2. Runtime 2 (SCR TBox Engine)
- compiles tenant inputs under global doctrine/invariant semantics
- consumes support-layer contracts for compile-time admissibility and typing
- fails non-permissively when semantics are missing, unknown, or violating invariants

3. Runtime 3 (SCR Customer Runtime)
- remains operational event authority layer (authority/execution/control events)
- full Runtime 3 event semantics are out of scope for this task and are not absorbed into support-layer governance modeling

## Prohibited Patterns

The following are explicitly forbidden in support-layer governance incorporation:
- prose-by-default binding
- metadata/placement/namespace implying authority, admissibility, or eligibility
- implicit authority inference from classification, labels, or structure
- reintroduction of MVP constraints via renamed fields (for example: hidden guards, implicit conditions)
- compile-permissive defaults for unknown or missing governance semantics
- importing full Runtime 3 operational model into Runtime 2 support contracts without explicit scope approval

## Governance Incorporation Workflow

G0 Source capture
- identify source clauses in doctrine/lifecycle/decisions/product runtime boundary docs

G1 Canonical intent extraction
- classify content as belief/risk/objective and determine intended governance effect

G2 Machine-form assignment
- assign ONTOLOGY_TERM, SHACL_RULE, or DETERMINISTIC_VALIDATOR per allocation rules

G3 Failure semantics assignment
- define failure mode and reason-code family where non-permissive outcomes apply

G4 Traceability binding
- populate required traceability fields

G5 Admission to binding path
- move from BINDING_CANDIDATE to BINDING_APPROVED only through explicit approval and evidence recording

## Output Contract for Downstream Tasks

This artifact provides mandatory input constraints for:
- `TASK-15.4` external ontology adoption policy (must respect this governance boundary)
- `TASK-15.5` identifier and MVP admissibility boundary (must align DD-001/DD-003/DD-004/DD-005 placement)

## Addendum Consideration

Governance translation in this model maintains explicit separation between runtime-internal lifecycle candidates, packaged boundary objects, and Runtime 3 operational instantiation.

## Validation Checklist (TASK-15.3)

- Governance source authority is explicitly separated from executable support contracts.
- Belief/risk/objective translation rules are explicit and machine-form mapped.
- Runtime boundary placement is explicit (Runtime 1/2 vs Runtime 3 separation).
- Non-permissive behavior and reason-code alignment are defined.
- Prose-by-default binding is explicitly forbidden.
