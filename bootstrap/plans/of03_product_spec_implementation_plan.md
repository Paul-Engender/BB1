# ontoForge_03 Product Spec Implementation Plan

Status: PLANNED
Owner: paul
Source: `specs/ontoForge_03_Product-Spec_V1.1.md`
Date: 2026-03-06

## Purpose

Translate the directional product specification in `ontoForge_03_Product-Spec_V1.1.md`
into a staged implementation program grounded in the current repository.

This plan is implementation-facing. It does not change governance authority.

## Binding Boundary

`ontoForge_03_Product-Spec_V1.1.md` is directional product and architecture intent.
Implementation must treat it as product-shape guidance, not as the sole source of binding
semantics.

Binding or semantically authoritative companions already in the repo:
- `specs/ontoForge_01_Doctrine_v1.1.md`
- `specs/ontoForge_02_Lifecycle-Specification_v1.1.md`
- `specs/ontoForge_04_Decisions-Register_v1.1.md`

Implementation rule:
- Use `ontoForge_03` to define runtime boundaries, product capabilities, tenancy model,
  and MVP scope.
- Use `ontoForge_02` and `ontoForge_04` to define lifecycle, event, authority, and control
  semantics that must be enforced in code.

## Current Repo Baseline

What already exists in the repo:
- Global semantic kernel substrate:
  - `ontology/` TBox and SHACL shapes
  - `runtime/kernel_gate.py`
  - `runtime/main.py`
- Packaging and verification substrate:
  - `tools/packager.py`
  - `src/loader.py`
  - `schemas/release_manifest.schema.json`
  - `schemas/runtime_load_manifest.schema.json`
  - release artifacts in `dist/`
- Customer-runtime primitives (bootstrap grade):
  - `src/cid.py`
  - `src/ledger.py`
  - `src/issuer_proof.py`
  - `src/evaluator.py`
- Evidence and planning substrate:
  - `bootstrap/task_ledger.csv`
  - `bootstrap/artifact_registry.csv`
  - `bootstrap/evidence_register.csv`
  - `tools/bootstrap_validate.py`

What does not yet exist as product-grade implementation:
- A real SCR TBox compiler/runtime (Runtime 2)
- A tenant-scoped SCR customer runtime service/API (Runtime 3)
- Product-level event model for AuthorityEvents, ExecutionEvents, denials, suspensions,
  and mode transitions
- Tenant-aware release/load binding with `tenant_id`
- Compilation evidence packaged and enforced as a downstream loading prerequisite
- Product-level target set, reason code, and operational control implementation
- End-to-end promotion flow across all three runtimes

## Product-Spec To Repo Mapping

1. Runtime 1: Support Ontology Engine
- Product-spec intent:
  - global semantic kernel
  - validation over support ontology
  - versioned `SupportOntologyRelease`
- Current repo status:
  - partial implementation exists
- Main gap:
  - convert current kernel validation service into a release-producing engine with explicit
    promotion evidence and product-facing interfaces

2. Runtime 2: SCR TBox Engine
- Product-spec intent:
  - tenant-scoped compiler for workflows under global doctrine/kernel constraints
- Current repo status:
  - missing
- Main gap:
  - no compiler pipeline from tenant workflow definitions to runtime-safe control primitives

3. Runtime 3: SCR Customer Runtime
- Product-spec intent:
  - tenant-scoped operational runtime with deterministic authority/execution behavior
- Current repo status:
  - only primitives exist
- Main gap:
  - no tenant service, no persistent ledger model, no product event model, no execution API

4. Boundary Objects and Promotion
- Product-spec intent:
  - versioned releases cross runtime boundaries
  - `SupportOntologyRelease`, `SCR_TBox_Release`, `SCR_Runtime_LoadManifest`
  - upstream evidence required for downstream load
- Current repo status:
  - partial packaging exists
- Main gap:
  - missing tenant-aware manifests, evidence directories, dependency binding, and promotion checks

## Implementation Workstreams

### W1. Product Contract Translation

Goal:
- Translate directional product sections into implementation-facing contracts and module boundaries.

Outputs:
- `specs/product_runtime_mapping_v1.md`
- `specs/product_event_model_v1.md`
- `specs/product_boundary_objects_v1.md`

Validation:
- Cross-reference every runtime and boundary object back to `ontoForge_03` plus governing
  companion docs.

### W2. Runtime 1 Hardening

Goal:
- Turn the current kernel/SHACL substrate into a product-grade Support Ontology Engine.

Scope:
- promote `runtime/main.py` from thin validation API to runtime-1 service boundary
- define release-candidate evaluation outputs
- package compilation/validation evidence alongside `SupportOntologyRelease`

Likely repo targets:
- `runtime/`
- `ontology/`
- `tools/`
- `dist/`

Validation:
- release package contains ontology payload plus evidence payload
- loader verifies the package and evidence hashes

### W3. Runtime 2 Compiler

Goal:
- Implement the SCR TBox Engine described in `ontoForge_03`.

Scope:
- define tenant input model
- compile workflow definitions into runtime-safe control structures
- fail closed when tenant input violates doctrine/kernel constraints
- emit tenant-scoped `SCR_TBox_Release`

Likely repo targets:
- new compiler module under `src/` or `runtime/`
- new schemas under `schemas/`
- new fixtures/tests under `fixtures/` and `tests/`

Validation:
- deterministic compile output
- explicit invariant-violation failures
- evidence bundle packaged with release

### W4. Runtime 3 Customer Runtime

Goal:
- Build the tenant-scoped customer runtime as defined by the product spec.

Scope:
- tenant-aware append-only ledger
- AuthorityEvent and ExecutionEvent model
- deterministic authorization and eligibility evaluation
- execution-commit boundary
- operational control events

Likely repo targets:
- `src/ledger.py`
- `src/evaluator.py`
- new service layer under `runtime/`
- new test suites

Validation:
- per-tenant total ordering
- deterministic as-of recomputation
- side effects only after committed execution event

### W5. Boundary Objects and Load Discipline

Goal:
- Close the gap between current packaging and the product-spec boundary model.

Scope:
- add `tenant_id` semantics where required
- add `SCR_Runtime_LoadManifest`
- encode release dependencies explicitly
- require evidence bundle presence and digest verification on load

Likely repo targets:
- `schemas/`
- `tools/packager.py`
- `src/loader.py`
- `fixtures/`

Validation:
- loader rejects missing evidence, mismatched tenant scope, or broken dependency chain

### W6. Vertical Slice

Goal:
- Prove one end-to-end path across the three runtimes.

Slice:
- global support ontology release
- tenant compile to SCR TBox release
- tenant runtime load and process one deterministic operational flow

Validation:
- end-to-end release lineage is hash-bound
- customer runtime can recompute authority/execution state as-of
- audit artifacts exist for the full chain

## Recommended Decomposition Order

1. W1 Product contract translation
2. W5 Boundary object/schema uplift
3. W2 Runtime 1 hardening
4. W3 Runtime 2 compiler
5. W4 Runtime 3 customer runtime
6. W6 Vertical slice and audit closure

Reason:
- The current repo already has substrate for Runtime 1 and packaging.
- Runtime 2 and Runtime 3 depend on stable boundary object definitions.
- The product spec makes the three-runtime chain the architecture; it should be implemented
  as a chain, not as isolated code islands.

## First Executable Step

Do not begin by coding runtime services directly.

Begin with W1:
- derive a concrete runtime/module map from `ontoForge_03`
- define event objects, boundary objects, and tenant scope rules
- then decompose W2-W6 into atomic ledger tasks

This is the minimum step that avoids building the wrong runtime boundaries.

## Exit Criteria

This plan is considered complete when:
- the three-runtime architecture exists in code and tests
- boundary objects are tenant-aware and evidence-bound
- downstream loading requires upstream evidence
- one end-to-end tenant slice is reproducible and auditable
