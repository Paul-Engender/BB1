# Product Boundary Objects v1

Status: IS
Owner: paul
Plan Item: P1-011
Task: TASK-11.3
Date: 2026-03-07

## Purpose

Define product boundary objects for the three-runtime chain so promotion and
loading are deterministic, tenant-safe, and evidence-bound.

This artifact establishes the contract shape for:
- `SupportOntologyRelease`
- `SCR_TBox_Release`
- `SCR_Runtime_LoadManifest`

## Canonical Source Binding

| Source | Binding Role | Boundary Object Impact |
| --- | --- | --- |
| `specs/ontoForge_03_Product-Spec_V1.1.md` | Directional runtime architecture | Defines the three-runtime promotion chain and required boundary objects |
| `specs/ontoForge_04_Decisions-Register_v1.1.md` | Approved decision contracts | Defines release packaging, tenant scope, dependency bindings, evidence prerequisites, and load discipline |
| `specs/ontoForge_02_Lifecycle-Specification_v1.1.md` | Canonical lifecycle and invariants | Requires append-only history, determinism, and no implicit defaults for binding controls |
| `specs/product_runtime_instantiation_clarification_addendum_2026-03-07.md` | Architectural clarification | Separates runtime-internal lifecycle candidates, runtime lifecycle instances, boundary objects, and Runtime 3 operational instantiation |

## Promotion Boundary Model

Only versioned boundary objects cross runtime boundaries. Nothing crosses by
file placement, naming, or prose.

## Non-Conflation Rule

The following concepts are distinct and must not be collapsed:
- internal lifecycle candidate
- runtime lifecycle instance
- boundary object
- Runtime 3 operational instantiation

Boundary-object rule:
- a boundary object is not the internal lifecycle candidate that matured inside a runtime
- a boundary object is not the runtime lifecycle instance itself
- Runtime 3 operational events are not boundary objects
- only the packaged, versioned release artifacts named below cross runtime boundaries

### Boundary Chain

1. Runtime 1 emits `SupportOntologyRelease` (global scope).
2. Runtime 2 consumes exact Runtime 1 dependency and emits `SCR_TBox_Release` (tenant scope).
3. Runtime 3 loads `SCR_TBox_Release` only via `SCR_Runtime_LoadManifest` with exact tenant match.

## Boundary Object Contracts

### 1) SupportOntologyRelease

Producer: Runtime 1 (Support Ontology Engine)
Consumer: Runtime 2 (SCR TBox Engine)
Scope: `global`

Interpretive rule:
- Runtime 1 matures support-layer semantic components internally.
- Those components may form a Runtime 1 release candidate body.
- Packaged `SupportOntologyRelease` is the only downstream boundary object.
- A single class, shape, or semantic component does not cross `Runtime 1 -> Runtime 2` by itself.

Required fields (target contract):
- `artifact_id`: `cid:<uuidv7>`
- `artifact_type`: `SupportOntologyRelease`
- `artifact_version`: SemVer
- `tenant_scope`: `global`
- `released_at`: RFC3339 timestamp
- `dependencies`: exact version-bound dependency list (may be empty for root release)
- `payload`: canonical support ontology payload references
- `file_hashes`: SHA-256 for all package files
- `evidence_hashes`: SHA-256 for validation/build evidence files

Required invariants:
- `tenant_id` MUST be absent for global scope.
- Release identity and hashes are immutable after issuance.
- Downstream consumers must reference exact `artifact_id` and `artifact_version`.

### 2) SCR_TBox_Release

Producer: Runtime 2 (SCR TBox Engine)
Consumer: Runtime 3 (SCR Customer Runtime)
Scope: `tenant`

Interpretive rule:
- Runtime 2 matures tenant workflow/process/control definitions internally.
- Those compiled definitions may form a Runtime 2 release candidate body.
- Packaged `SCR_TBox_Release` is the only downstream boundary object.
- A tenant workflow/process definition is not itself the boundary object.

Required fields (target contract):
- `artifact_id`: `cid:<uuidv7>`
- `artifact_type`: `SCR_TBox_Release`
- `artifact_version`: SemVer
- `tenant_scope`: `tenant`
- `tenant_id`: `cid:<uuidv7>`
- `released_at`: RFC3339 timestamp
- `dependencies`: MUST include exact SupportOntologyRelease bindings
- `payload`: compiled tenant control artifacts
- `file_hashes`: SHA-256 for all package files
- `evidence_hashes`: SHA-256 for compilation evidence files

Required invariants:
- `tenant_id` is mandatory and immutable.
- Compilation evidence is mandatory for downstream admissibility.
- Missing evidence or hash mismatch makes the release inadmissible.

### 3) SCR_Runtime_LoadManifest

Producer: Runtime 2 or deployment-control plane
Consumer: Runtime 3 loader
Scope: `tenant`

Required fields (target contract):
- `manifest_id`: `cid:<uuidv7>`
- `manifest_version`: semantic version for load-manifest schema
- `tenant_id`: `cid:<uuidv7>`
- `runtime_instance_id`: stable runtime identity
- `tbox_release_id`: exact `SCR_TBox_Release.artifact_id`
- `tbox_release_version`: exact release version
- `support_release_id`: exact dependency binding for audit/recompute
- `load_mode`: explicit mode enum (for example `active`, `safe`, `hold`)
- `declared_at`: RFC3339 timestamp
- `declared_by`: issuer identity reference

Required invariants:
- Loader must reject if load-manifest `tenant_id` does not equal release `tenant_id`.
- Loader must reject if release dependency chain is incomplete or inconsistent.
- Loader must reject if required evidence files are absent or hash-invalid.

Load-binding rule:
- `SCR_Runtime_LoadManifest` governs what Runtime 3 may load.
- It is not a substitute for `SCR_TBox_Release`.
- It is not a Runtime 3 operational event.
- Only after successful load binding may Runtime 3 instantiate live tenant proposals/transitions into authoritative operational events.

## Cross-Object Chain-of-Truth Rules

1. Each boundary object is versioned and hash-bound.
2. Runtime 2 output must carry exact Runtime 1 dependency references.
3. Runtime 3 load must be explicit through `SCR_Runtime_LoadManifest`; no implicit load.
4. Runtime 3 load requires evidence-complete `SCR_TBox_Release` package.
5. Any mismatch in tenant scope, dependency, or digest is non-permissive.

## Runtime 3 Load Admissibility Gate

Runtime 3 admission sequence for a candidate `SCR_TBox_Release`:

1. Parse and validate release manifest structure.
2. Verify package file hashes.
3. Verify required evidence directory/files exist.
4. Verify evidence hashes from manifest.
5. Verify release `tenant_id` exists and is valid.
6. Parse `SCR_Runtime_LoadManifest`.
7. Verify tenant equality (`release.tenant_id == load_manifest.tenant_id`).
8. Verify exact dependency binding to referenced `SupportOntologyRelease`.
9. Admit load only if all checks pass.

## Current Repo Mapping

| Boundary Object | Current Repo Substrate | State | Current Translation Note |
| --- | --- | --- | --- |
| `SupportOntologyRelease` | `runtime/runtime1_engine.py`, `tools/packager.py`, `schemas/release_manifest.schema.json`, `dist/SupportOntologyRelease-v0.2.0/` | Partial | Boundary packaging and evidence binding exist; Runtime 1 payload membership still needs alignment to the canonical support-release composition contract |
| `SCR_TBox_Release` | `dist/SCR_TBox_Release-v0.1.0/`, `tools/packager.py`, `src/loader.py`, `schemas/release_manifest.schema.json` | Partial | Tenant scope, dependency binding, and evidence requirements exist in the boundary contract, but Runtime 2 compiler production of the boundary object remains unimplemented |
| `SCR_Runtime_LoadManifest` | `schemas/runtime_load_manifest.schema.json`, `src/loader.py` | Partial | Schema and loader tenant/dependency checks exist; remaining gap is hard separation between generic package verification and strict Runtime 3 load binding semantics |

## Implementation Direction

To align code with this contract:
- keep schema and packager behavior anchored to explicit boundary-object fields only
- align Runtime 1 package membership to the canonical `SupportOntologyRelease` payload contract
- tighten loader behavior so Runtime 3 load binding is explicitly manifest-bound for tenant releases
- keep Runtime 2 implementation scoped to producing `SCR_TBox_Release`, not to reusing Runtime 1 or Runtime 3 internal lifecycle objects

## Acceptance Checklist for TASK-11.3

- Boundary objects are explicitly defined with scope and producer/consumer runtime.
- Tenant and dependency binding rules are explicit and non-defaulting.
- Evidence prerequisite for downstream load is explicit and testable.
- Boundary-object interpretation is explicitly separated from runtime-internal lifecycle candidates and Runtime 3 operational events.
- Current substrate state is mapped without relying on stale pre-hardening gap statements.

## Next Input

This artifact closes W1 translation outputs and is the direct input to schema
and loader hardening work under the next implementation tranche.
