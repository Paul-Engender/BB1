# Product Tenant-Scope Runtime-Handoff Rules v1

Status: APPROVED
Owner: paul
Plan Item: P2-001
Task: TASK-27.4
Date: 2026-03-08

## Purpose

Define the narrow successor rules that govern how tenant scope is introduced,
carried, and enforced across the Runtime 1 -> Runtime 2 -> Runtime 3 chain.

This document does not replace the retained event or boundary-object baseline.
It fills the specific tenant-scope runtime-handoff gap identified in
`specs/p2_contract_translation_review_v1.md` and recorded as `P2-D01` in
`specs/p2_contract_delta_register_v1.md`.

## Governing Baseline

These rules operate on top of the retained baseline:
- `specs/product_event_model_v1.md`
- `specs/product_boundary_objects_v1.md`
- `specs/runtime1_support_release_engine_v1.md`
- `specs/ontoForge_03_Product-Spec_V1.1.md`
- `specs/ontoForge_04_Decisions-Register_v1.1.md`

## Core Scope Rules

### 1) Runtime 1 is global only

Runtime 1 emits only global boundary objects.

Rules:
- `SupportOntologyRelease` MUST use `tenant_scope = global`.
- `SupportOntologyRelease` MUST NOT carry `tenant_id`.
- Runtime 1 internal candidate state MUST NOT be treated as tenant-scoped input.
- Runtime 1 output may be referenced by many tenants, but tenant scope is not
  created at Runtime 1.

### 2) Tenant scope is introduced at Runtime 2

Tenant scope begins only when Runtime 2 compiles tenant-specific input into a
packaged tenant boundary object.

Rules:
- `SCR_TBox_Release` MUST use `tenant_scope = tenant`.
- `SCR_TBox_Release` MUST carry exactly one explicit `tenant_id`.
- That `tenant_id` MUST be treated as the tenant partition anchor for all
  downstream loading and Runtime 3 operation.
- Tenant scope MUST NOT be inferred from file location, namespace, operator, or
  deployment path.

### 3) Runtime 2 must carry exact upstream dependency lineage

Runtime 2 introduces tenant scope, but it does so against an exact global
upstream dependency.

Rules:
- Every `SCR_TBox_Release` MUST record the exact upstream
  `SupportOntologyRelease` dependency binding.
- The tenant-scoped output is valid only against that exact dependency chain.
- Runtime 2 MUST NOT copy Runtime 1 internal lifecycle candidates into tenant
  scope by interpretation; only the packaged `SupportOntologyRelease` crosses
  the boundary.

### 4) Runtime 3 load is explicit and tenant-bound

Runtime 3 may load only a tenant-scoped release that is explicitly declared for
that tenant.

Rules:
- `SCR_Runtime_LoadManifest.tenant_id` MUST exactly equal
  `SCR_TBox_Release.tenant_id`.
- Runtime 3 MUST reject the load on any tenant mismatch.
- Runtime 3 MUST reject the load if the referenced support-release dependency is
  incomplete, missing, or inconsistent.
- Runtime 3 MUST reject the load if required evidence is absent or hash-invalid.

### 5) Runtime instance identity is not tenant scope

`runtime_instance_id` identifies the target runtime instance. It does not define
or widen tenant scope.

Rules:
- `runtime_instance_id` MUST be treated as deployment/runtime identity only.
- Tenant admissibility MUST still be determined by explicit `tenant_id` equality
  and dependency validity.
- A runtime instance MUST NOT infer authority to load a tenant release from its
  own name, placement, or configuration label alone.

### 6) Runtime 3 operational events remain separate from load/boundary objects

Load admission is not operational truth.

Rules:
- `SCR_TBox_Release` and `SCR_Runtime_LoadManifest` are boundary objects only.
- They are not Runtime 3 operational events.
- Runtime 3 operational truth begins only when tenant-partitioned events are
  committed under the retained Runtime 3 event model.
- Load success MUST NOT be misread as authority grant, execution commitment, or
  live operational truth.

## Runtime-Handoff Matrix

| Handoff | Scope State | Required Explicit Fields | Rejection Condition |
| --- | --- | --- | --- |
| Runtime 1 -> Runtime 2 via `SupportOntologyRelease` | global only | `artifact_id`, `artifact_version`, `tenant_scope = global`, exact dependency identity | reject any attempt to treat Runtime 1 output as tenant-scoped or to infer tenant from context |
| Runtime 2 internal -> `SCR_TBox_Release` | tenant scope introduced | `tenant_scope = tenant`, `tenant_id`, exact support-release dependency, evidence bindings | reject missing `tenant_id`, ambiguous tenant ownership, or incomplete dependency lineage |
| `SCR_TBox_Release` -> Runtime 3 via `SCR_Runtime_LoadManifest` | tenant scope enforced | `tenant_id` equality, exact release reference, exact support dependency reference, evidence completeness | reject tenant mismatch, broken dependency chain, or missing/invalid evidence |
| Runtime 3 load -> Runtime 3 operational events | tenant scope preserved | loaded release identity, tenant partition key, Runtime 3 event envelope fields | reject any attempt to treat load/boundary objects as operational events |

## Non-Entailment Rules

The following are explicitly forbidden in tenant-scope determination:
- inferring tenant from namespace
- inferring tenant from file path
- inferring tenant from runtime instance label
- inferring tenant from class membership or ontology placement
- inferring operational authority from successful load admission

If tenant scope is not explicit where required, the handoff is non-permissive.

## Acceptance Checklist (TASK-27.4)

- Runtime 1 global-only rule is explicit
- Runtime 2 tenant-scope introduction rule is explicit
- Runtime 3 tenant-bound load rule is explicit
- runtime instance identity is separated from tenant scope
- load/boundary objects are separated from operational truth
- no tenant scope is inferred from descriptive context
