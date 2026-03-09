# Runtime 2 Compiler Module Boundary v1

Status: APPROVED
Owner: paul
Plan Item: P2-003
Task: TASK-29.2
Date: 2026-03-08

## Purpose

Define the implementation-facing module boundary and repo placement for the
Runtime 2 compiler lane.

This document does not reopen the approved Runtime 2 semantic baseline. It
translates that baseline into a clean software structure for implementation.

## Baseline Inputs

- `bootstrap/plans/programs/p2_003_runtime2_compiler_decomposition_v1.md`
- `specs/runtime2_compiler_contract_baseline_review_v1.md`
- `specs/runtime2_tenant_workflow_input_contract_v1.md`
- `specs/runtime2_support_admissibility_matrix_v1.md`
- `specs/runtime2_compiled_control_primitives_v1.md`
- `specs/product_tenant_scope_rules_v1.md`
- `specs/product_boundary_objects_v1.md`

## Current Repo Starting Point

Current reusable substrate already exists in the repo:
- `tools/packager.py` for boundary-object package creation
- `src/cid.py` for CID minting and validation support
- `schemas/release_manifest.schema.json` for release-manifest validation target
- `src/loader.py` for downstream package verification and Runtime 3 load binding
- `runtime/runtime1_engine.py` as a reference for Runtime 1 service-boundary
  patterns only

Current gap:
- there is no dedicated Runtime 2 compiler module boundary in executable form
- Runtime 2 responsibilities must therefore be introduced without mixing with
  Runtime 1 release generation or Runtime 3 operational loading

## Boundary Rule

Runtime 2 must be implemented as a distinct compiler lane with explicit
separation between:
- tenant input ingest
- admissibility evaluation
- semantic normalization and lineage binding
- compiled primitive emission
- evidence emission
- `SCR_TBox_Release` packaging

Runtime 2 must not absorb Runtime 3 operational truth handling.

## Target Repo Placement

Runtime 2 implementation should be introduced under a dedicated package:
- `runtime/runtime2/`

Recommended file set:
- `runtime/runtime2/__init__.py`
- `runtime/runtime2/compiler_service.py`
- `runtime/runtime2/ingest.py`
- `runtime/runtime2/admissibility.py`
- `runtime/runtime2/normalize.py`
- `runtime/runtime2/primitive_emit.py`
- `runtime/runtime2/evidence.py`
- `runtime/runtime2/release.py`
- `runtime/runtime2/errors.py`

Recommended test set:
- `tests/test_runtime2_ingest.py`
- `tests/test_runtime2_admissibility.py`
- `tests/test_runtime2_primitive_emit.py`
- `tests/test_runtime2_release.py`

## Shared vs Runtime-Specific Ownership

### Shared reusable modules

The following may be reused directly because they are runtime-agnostic or
boundary-object generic:
- `tools/packager.py`
- `src/cid.py`
- `schemas/release_manifest.schema.json`

### Runtime 2-owned modules

The following must be Runtime 2-specific because they encode compile-plane
semantics:
- ingest of tenant workflow input
- admissibility gate ordering and reason-code selection
- normalization from admitted input into compile model
- compiled primitive construction
- compile evidence production
- `SCR_TBox_Release` assembly

### Explicit non-ownership

Runtime 2 must not own or emit:
- Runtime 1 support-release semantics
- Runtime 3 load-manifest enforcement
- Runtime 3 operational authority or execution events

## Compiler Module Responsibilities

### 1) `compiler_service.py`

Role:
- public Runtime 2 orchestration boundary
- accepts a compile request with tenant input and exact support-release binding
- calls the ordered internal compiler stages
- returns compile result metadata and release paths

Rules:
- may coordinate stages but must not contain stage-specific semantic logic
- remains the only external service/API entry point for first implementation

### 2) `ingest.py`

Role:
- parse and normalize incoming tenant workflow input package
- verify required envelope presence before semantic admissibility checks
- expose a typed in-memory compile candidate surface

Rules:
- no permissive defaults
- no semantic inference
- malformed or incomplete inputs fail before primitive construction

### 3) `admissibility.py`

Role:
- implement deterministic check ordering from the approved admissibility matrix
- evaluate required input, support dependency, target, scope, authority,
  eligibility, denial, and AI-operable rules
- emit primary reason codes on failure

Rules:
- fixed stage and row ordering
- first primary failure must remain stable for same input
- no Runtime 3 operational interpretation

### 4) `normalize.py`

Role:
- convert admitted input into a normalized internal compile model
- bind exact support-release references and source input lineage
- prepare explicit data for primitive emission

Rules:
- normalization may reorganize explicit semantics only
- normalization must not manufacture new meaning

### 5) `primitive_emit.py`

Role:
- build required primitive families for `SCR_TBox_Release`
- enforce complete primitive records and required lineage references
- reject incomplete or implicit output surfaces

Required first-slice primitive families:
- `TargetScopePrimitive`
- `ActionEffectPrimitive`
- `AuthorizationPrimitive`
- `EligibilityPrimitive`
- `DenialPrimitive`
- `ControlStatePrimitive`
- `TracePrimitive`

### 6) `evidence.py`

Role:
- emit deterministic compile evidence payloads
- record admissibility outcomes, compile decisions, and source/dependency
  lineage required for release admissibility

Rules:
- evidence is mandatory for downstream Runtime 3 load admissibility
- evidence emission is part of compiler success, not an optional add-on

### 7) `release.py`

Role:
- assemble the tenant-scoped `SCR_TBox_Release`
- call shared packaging substrate with exact dependency bindings
- validate output manifest expectations for tenant scope and evidence presence

Rules:
- Runtime 2 introduces tenant scope here, not earlier and not later
- output must remain a boundary object, not a Runtime 3 operational instance

### 8) `errors.py`

Role:
- define typed compiler exceptions and structured failure surfaces
- keep failure classes stable across ingest, admissibility, emission, and
  packaging stages

## Compiler Stage Order

The first implementation should preserve this fixed order:
1. ingest parse and envelope checks
2. support-release dependency binding checks
3. admissibility matrix evaluation
4. normalized compile-model creation
5. compiled primitive emission
6. compile evidence emission
7. `SCR_TBox_Release` packaging

This order preserves fail-closed behavior and keeps primitive emission dependent
on prior admission success.

## Runtime Boundary Discipline

- Runtime 2 is the first runtime that introduces tenant scope.
- Runtime 2 emits only `SCR_TBox_Release` boundary objects.
- Runtime 2 must not call Runtime 3 load-binding logic as part of compiler core.
- Runtime 2 may later use generic package verification as a test/regression
  surface, but not as a substitute for compiler semantics.

## Implementation Guidance

1. Reuse shared generic packaging and CID utilities rather than duplicating
   them inside Runtime 2.
2. Keep admissibility logic isolated from primitive emission so fail-closed
   behavior remains testable.
3. Keep release assembly isolated from admissibility logic so package-level
   changes do not silently alter compile semantics.
4. Keep Runtime 3 load-manifest and operational event handling out of the
   Runtime 2 package.

## Acceptance Checklist (TASK-29.2)

- repo placement for Runtime 2 is explicit
- module boundaries are explicit and non-overlapping
- shared vs Runtime 2-owned responsibilities are explicit
- compiler stage order is explicit
- tenant-scope introduction point is explicit
- Runtime 3 operational semantics are explicitly excluded


