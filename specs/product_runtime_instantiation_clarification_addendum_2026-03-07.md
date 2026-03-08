# Patch Addendum - Runtime Instantiation, Internal Lifecycle Candidate, Boundary Object, and Operational Instantiation Clarification

Status: Directional clarification addendum
Date: 2026-03-07
Canonical location intent: AI-Semantic Control OS Product Specification (addendum section)
Cross-reference location intent: Canonical Document Set Map

## Binding Boundary

This addendum is an architectural clarification only. It does not create, amend, or supersede executable controls, CSC/CIR contracts, authority logic, or approved decisions.

Doctrine remains non-operational by design. Binding lifecycle semantics remain solely in the canonical lifecycle/control specification.

## 1. Purpose

Remove ambiguity between:
- internal lifecycle candidate
- runtime lifecycle instance
- boundary object
- Runtime 3 operational instantiation

This clarification is architectural only.

## 2. Non-Conflation Rule

The following four concepts are distinct and must remain distinct:

1. Internal lifecycle candidate
- The candidate object evaluated and matured inside a runtime through CSC.

2. Runtime lifecycle instance
- The execution of canonical CSC `S1..S7` inside that runtime over that runtime's candidate object.

3. Boundary object
- The packaged, versioned artifact permitted to cross runtime boundaries.

4. Runtime 3 operational instantiation
- Tenant-scoped instantiation of live proposals, transitions, and requested actions into authoritative operational events.

Invalid interpretation:
- collapsing these four concepts into one object, one package, or one step.

Canonical interpretation:
- CSC `S1..S7` is one canonical lifecycle state machine instantiated independently in each runtime.
- Runtimes do not share a single mutable lifecycle state.
- Same lifecycle form, different candidate objects, different scopes, different truth products, different side-effect permissions.
- Only approved boundary objects cross runtime boundaries.
- Nothing crosses by presence, placement, naming, commentary, or prose.

## 3. Runtime 1 - Support Ontology Engine

### 3.1 Internal lifecycle candidate

A support-layer semantic component or coherent support-layer semantic change set (classes, relations, shapes, rules, and related support semantics).

### 3.2 What CSC evaluates in Runtime 1

CSC evaluates a Support Ontology release candidate assembled from one or more mature support-layer semantic components.

### 3.3 Boundary object emitted by Runtime 1

`SupportOntologyRelease` (packaged, versioned) plus append-only release evidence cryptographically bound to the package.

### 3.4 Interpretive rule for Runtime 1

- A class is not a release.
- A single semantic component does not cross `Runtime 1 -> Runtime 2` by itself.
- Support semantic components mature inside Runtime 1.
- A set of mature Runtime 1 components forms the Runtime 1 release candidate body.
- Packaged `SupportOntologyRelease` is the downstream boundary object.

## 4. Runtime 2 - SCR TBox Engine / Logical Compiler

### 4.1 Internal lifecycle candidate

Tenant workflow/process definition together with compile-time control semantics.

### 4.2 What CSC evaluates in Runtime 2

CSC evaluates a tenant compile candidate.

It does not:
- evaluate a Runtime 1 release as though that were the Runtime 2 candidate,
- evaluate live tenant operational events.

Runtime 2 compiles tenant workflow definitions into runtime-safe control primitives under global doctrine, global invariants, and support-ontology semantics.

Compilation is canonical or non-permissive. Missing semantics are not completed by inference.

### 4.3 Boundary object emitted by Runtime 2

`SCR_TBox_Release` (packaged, versioned, tenant-scoped) plus append-only compilation evidence cryptographically bound to the package.

`SCR_TBox_Release` must:
- reference exact `SupportOntologyRelease` dependencies,
- carry `tenant_id`.

### 4.4 Interpretive rule for Runtime 2

- A tenant workflow/process definition is not a release.
- Tenant workflow/process definitions mature inside Runtime 2.
- A set of mature compiled tenant workflow/control definitions forms the Runtime 2 release candidate body.
- Packaged `SCR_TBox_Release` is the boundary object consumed by Runtime 3.

## 5. Runtime 3 - SCR Customer Runtime

### 5.1 Internal lifecycle candidate

Live tenant proposal, transition, or requested action in tenant operational context.

### 5.2 What CSC evaluates in Runtime 3

CSC governs runtime admission/alignment of runtime-plane inputs and proposals.

Runtime 3 then performs deterministic:
- authority derivation,
- authorization,
- eligibility evaluation,
- execution commitment,

according to loaded canonical controls.

Runtime 3 is not where support semantic components mature and not where tenant workflow definitions are compiled into release artifacts.

### 5.3 Truth product emitted by Runtime 3

Authoritative tenant operational records:
- `AuthorityEvents`
- `ExecutionEvents`
- denials
- suspensions
- mode transitions
- as-of recomputation proof and audit views

### 5.4 Load binding versus operational instantiation

- Runtime 3 does not consume raw Runtime 1 semantic components.
- Runtime 3 does not consume raw Runtime 2 process definitions.
- Runtime 3 loads tenant-scoped `SCR_TBox_Release` via `SCR_Runtime_LoadManifest`.
- Only after valid load binding does Runtime 3 instantiate live tenant proposals/transitions into authoritative operational events.

## 6. Cross-Runtime Progression Model

1. Runtime 1 matures support-layer semantic components and emits `SupportOntologyRelease`.
2. Runtime 2 consumes `SupportOntologyRelease`, matures tenant workflow/process/control definitions, and emits `SCR_TBox_Release`.
3. Runtime 3 loads `SCR_TBox_Release` through `SCR_Runtime_LoadManifest` and instantiates live tenant proposals/transitions into authoritative operational events.

No other artifact crosses runtime boundaries as architectural meaning.

Nothing is promoted by file presence, naming, placement, commentary, or informal interpretation.

## 7. Rejected Interpretations

Invalid:
- "A class goes through `S1..S7` and becomes a release."
- "A single support ontology class crosses directly into Runtime 2."
- "A tenant process flow crosses directly from prose into Runtime 3."
- "Runtime 3 instantiates `SupportOntologyRelease` directly."
- "Release creation and internal lifecycle maturation are the same step."
- "Because CSC is one lifecycle, the internal lifecycle candidate is the same object in all three runtimes."

Correct:
- Runtime 1 matures support semantics, then packages `SupportOntologyRelease`.
- Runtime 2 matures tenant workflow/control definitions, then packages `SCR_TBox_Release`.
- Runtime 3 matures live tenant proposals/transitions into authoritative operational events.

## 8. Canonical Summary Statement

Runtime 1 matures support-layer semantic components into a releasable global support bundle.

Runtime 2 matures tenant workflow and control definitions into a releasable tenant TBox bundle.

Runtime 3 matures live tenant proposals and transitions into operational truth.

## 9. Canonical Document Map Cross-Reference Note

Cross-reference entry to add in document-map artifacts:
- Patch Addendum - 2026-03-07 - Runtime Instantiation Clarification (Architectural Direction)
- Clarifies distinction between internal lifecycle candidates, runtime CSC instantiation, packaged boundary objects, and Runtime 3 operational instantiation.
- Canonical location intent: AI-Semantic Control OS Product Specification (addendum section).
- This addendum does not alter doctrine, canonical lifecycle contracts, or approved decisions.