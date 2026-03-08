# Support Ontology CSC Stage Model v1

Status: APPROVED
Owner: paul
Plan Item: P1-017
Task: TASK-17.1
Date: 2026-03-07

## Canonical Reading

There is one canonical lifecycle state machine: CSC `S1..S7`.

This is not three different lifecycle models. It is one lifecycle pattern instantiated three times in three runtimes. What differs by runtime is:
- truth product
- permitted side effects
- scope of state and inputs

## Governance Boundary

Doctrine is governance-plane and non-operational by itself. Doctrine does not execute lifecycle transitions by prose.

Executable lifecycle control comes from canonical lifecycle/control contracts.

## Sources

Primary anchors:
- `specs/ontoForge_02_Lifecycle-Specification_v1.1.md`
- `specs/ontoForge_03_Product-Spec_V1.1.md`
- `specs/support_ontology_governance_incorporation_model_v1.md`

Companion clarification:
- `specs/product_runtime_instantiation_clarification_addendum_2026-03-07.md`

## Canonical Stage Vocabulary

- `S1` Origination
- `S2` Admission
- `S3` Classification
- `S4` Alignment
- `S5` Attribution
- `S6` Operation
- `S7` Deprecation

Normative stage rule:
- The lifecycle has exactly seven canonical stages (`S1` through `S7`).
- Stage identifiers and stage order are binding and must not be collapsed, merged, renumbered, or replaced.

## Instantiation Rule

Each runtime executes its own CSC `S1..S7` over its own bounded state.

This does not mean:
- one shared mutable state machine across all runtimes
- three unrelated lifecycle models
- execution by doctrine prose

This does mean:
- same CSC gate logic reused three times
- different artifacts/events processed per runtime
- different truth produced per runtime

## Runtime 1 Instantiation (Global Semantic Truth)

Scope:
- global, platform-owned, immutable per release

Primary concern:
- is the global semantic contract admissible and releasable

Stage application summary:
- `S1-S4`: descriptive/admission/classification/alignment checks over support ontology artifacts
- `S5-S6`: validate authority/operation semantics as support contract surfaces
- `S7`: deprecation/supersession of support semantics in append-only release history

Value created:
- `SupportOntologyRelease`
- append-only release evidence linked to that release

Must not do:
- customer execution
- tenant operational authority state
- customer operational side effects

## Runtime 2 Instantiation (Tenant Control Truth)

Scope:
- tenant-scoped compilation, platform-enforced

Primary concern:
- can tenant workflow compile canonically under global doctrine + global support semantics

Runtime-2 `S1` required inputs:
1. Upstream support semantic contract input via approved `SupportOntologyRelease` dependency binding
2. Standalone tenant custom workflow input (domains/rules/TargetSets/routing)

Admission rule:
- if either input is missing, ambiguous, non-deterministic, or default-dependent, remain non-permissive

Stage application summary:
- `S1-S4`: intake/admission/classification/alignment of tenant definitions under global constraints
- `S5-S6`: compile safe authority/operation control semantics; no customer `AuthorityEvent`/`ExecutionEvent` generation
- `S7`: supersession/deprecation handling for tenant-scoped compiled control artifacts

Value created:
- `SCR_TBox_Release`
- append-only compilation evidence linked to that release

Must not do:
- customer side effects
- customer authority/execution event generation
- permissive completion of missing semantics

## Runtime 3 Instantiation (Tenant Operational Truth)

Scope:
- strictly tenant-scoped, customer-facing enforcement runtime

Primary concern:
- what is admissible/authorized/eligible now, and what operational truth must be committed

Stage application summary:
- `S1-S4`: runtime admission/alignment gates for proposals/inputs
- `S5`: only stage where binding authority is generated (`AuthorityEvent` append)
- `S6`: execution-commitment boundary (`ExecutionEvent` append first, side effects only after append)
- `S7`: append-only deprecation/supersession; no historical rewrite

Value created:
- authoritative operational tenant record (authority, execution, denials, suspensions, transitions)
- as-of recomputation and audit views

## Cross-Runtime Connection Model

Runtimes are not connected by shared state, folder placement, naming, or prose interpretation.

Only versioned boundary artifacts cross runtime boundaries:
1. Runtime 1 -> Runtime 2 via `SupportOntologyRelease`
2. Runtime 2 -> Runtime 3 via `SCR_TBox_Release`
3. Runtime 3 load control via `SCR_Runtime_LoadManifest`

Boundary-object discipline:
- `SCR_TBox_Release` references exact `SupportOntologyRelease` dependencies
- downstream loading requires upstream evidence presence and digest integrity
- Runtime 3 rejects load on missing/invalid evidence
- Runtime 3 rejects load when release `tenant_id` and load-manifest `tenant_id` do not match

## Truth Domains

There are three separate state domains:
1. Global release state (Runtime 1)
2. Tenant compile state (Runtime 2)
3. Tenant operational state (Runtime 3)

These are separate instantiations because each runtime owns a different truth domain.

## Program Invariant

Global Doctrine, Tenanted Workflows:
- tenants do not override global doctrine
- Runtime 2 is the collision point of tenant workflow vs global constraints
- Runtime 3 is the enforcement point of compiled tenant control vs live operations

## Non-Permissive Rule

Across all three runtime instantiations:
- unknown required premises remain non-permissive
- default completion of missing binding semantics is forbidden
- failure classes map to `ABORT` / `QUARANTINE` / `DENY` under canonical policy

## Dependency and Downstream Role

This artifact is required input for:
- `TASK-17.2` invariant taxonomy and non-permissive outcome model
- `TASK-17.3` machine-readable support contract target map

## Caveat

This artifact states the instantiation model and boundary discipline.

Exact executable transition semantics and stage data contracts are canonically defined in the lifecycle/control specification, not in doctrine prose or this summary artifact.

## Validation Checklist (TASK-17.1)

- Seven canonical stages are explicit and unchanged.
- One lifecycle pattern instantiated three times is explicit.
- Runtime 1, Runtime 2, and Runtime 3 are separate in scope/state/inputs/outputs.
- Boundary-object chain is explicit and artifact-only.
- Runtime 2 dual-input requirement is explicit.
- Runtime 3 commit boundaries (`S5` authority, `S6` execution) are explicit.