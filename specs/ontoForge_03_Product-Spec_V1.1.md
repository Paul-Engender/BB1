AI–Semantic Control OS Product Specification

Version: Draft 0.7 (Refactored)

Status: Directional (architecture and product scope)

Date: 2026-03-04

Audience: Platform operators, tenant operators, and AI agents

# AI–Semantic Control OS Product Specification

Version: Draft 0.7 (Refactored; canonical locations and shorter purpose-driven structure)

Date: 2026-03-04

Status: Directional product and architecture specification (non-binding unless separately canonized)

## 0. Document intent and binding boundary

This document describes the product intent, tenancy model, three-runtime architecture, promotion discipline, and MVP scope. It is directional.

Binding governance outcomes (admission decisions, authority derivation, policy evaluation, and execution commitment) MUST be governed only by canonical contracts in the companion control specification:

- AI–Ontological Governance & Lifecycle Specification (Canonical Contracts)

Doctrine (beliefs, objectives, risks) is canonical in the companion doctrine document and is non-operational by design:

- Beliefs and Governance Framework

## 1. Executive intent

The product is ontology- and belief-driven end-to-end, including the work performed by AI agents. The system structurally prevents agents from creating operational truth by interpretation, placement, or prose. Authority, admissibility, eligibility, and execution must be computable and auditable.

## 2. Core architecture, tenancy model, and the three-runtime lifecycle

### 2.0 Tenancy model (hard boundary)

We operate on a Global Doctrine, Tenanted Workflows model.

- Bring Your Own Doctrine is not permitted. Tenants cannot override, replace, or extend the platform’s global doctrine or CIRs in any way that would affect binding outcomes.

- The platform defines global “physics” (beliefs, invariants, identity rules, and kernel semantics).

- Tenants customize workflows and operational rules only within the bounds proven compliant by the compiler.

### 2.1 One lifecycle state machine, instantiated three times

CSC S1–S7 is the canonical lifecycle state machine and is executed in all three engines (the same state machine, instantiated three times). Only the truth product and the permitted side effects differ.

### 2.2 Runtime 1 — Support Ontology Engine (“Semantic Kernel”) (global, internal)

Scope: Global (platform/vendor owned). Immutable per release.

Role: Governance-language kernel runtime.

What it runs:

- Validation and consistency checking over the Support Ontology.

- Enforcement of semantic integrity requirements (identity/boundary determinacy; form-to-kind alignment; versioning discipline).

- Release candidate evaluation via CSC S1–S7.

What it produces:

- SupportOntologyRelease (global; versioned; packaged per DD-002).

- Append-only release evidence (validation outputs, traceability, build results), cryptographically linked to the release package.

What it must not do:

- No customer execution.

- No tenant operational authority state.

- No operational side effects beyond internal build/test.

Audience: Platform operators and internal AI agents.

### 2.3 Runtime 2 — SCR TBox Engine (“Logical Compiler”) (tenanted execution context, internal)

Scope: Tenanted compilation (platform-enforced; tenant-specific inputs). Outputs are tenant-scoped.

Role: Control ontology compiler/runtime.

Tenanted purpose: Compile the tenant’s custom workflows (domains, rules, TargetSets, routing logic) while strictly enforcing:

- the global Doctrine and CIRs (the Constitution), and

- the global Support Ontology (kernel semantics).

What it runs:

- Compilation/operationalization of tenant workflow definitions into runtime-safe control primitives.

- Enforcement that control constructs are explicit and computable without defaults (compile canonically or fail).

- Validation that Action primitives have explicit target/effect semantics.

- Validation that TargetSets have deterministic membership semantics and deterministic “as-of” selection rules.

- Release candidate evaluation via CSC S1–S7.

Compile gate (global enforcement): If a tenant workflow (or an AI agent assisting the tenant) attempts to bypass a global belief/invariant, compilation fails with an invariant violation (non-permissive).

What it produces:

- SCR_TBox_Release (tenant-scoped; versioned; packaged per DD-002; references exact SupportOntologyRelease dependencies; carries tenant_id).

- Append-only compilation evidence (what was derived from what; why a candidate failed), cryptographically linked to the release package.

What it must not do:

- No customer side effects.

- No customer AuthorityEvents/ExecutionEvents.

- No “helpful” inference to fill missing semantics; compile canonically or fail.

Audience: Platform operators, tenant administrators (via tooling), and internal AI agents.

### 2.4 Runtime 3 — SCR Customer Runtime (tenant-scoped, customer-facing)

Scope: Strictly tenant-scoped.

Role: Enforcement and operational truth.

What it runs:

- Admission/alignment gates for runtime inputs and proposals (CSC S1–S4).

- Append-only event ledger (DD-003) and deterministic authority derivation.

- Deterministic authorization at evaluation time with canonical reason_codes (DD-004).

- Eligibility evaluation and enforcement prior to execution commitment (DD-005).

- Execution-commitment boundary (ExecutionEvent first; side effects only after).

- Operational controls (HardStopEvent / ResumeEvent) as defined in the loaded SCR TBox (DD-005).

What it produces:

- Authoritative tenant operational record: AuthorityEvents, ExecutionEvents, denials, suspensions, mode transitions.

- As-of recomputation proof and audit views.

Audience: Tenant customers, their operators, and their AI agents.

## 3. Promotion discipline, boundary objects, and chain-of-truth

Between each runtime, only versioned releases cross the boundary. Nothing crosses by presence, placement, naming, or prose.

### 3.1 Boundary objects and scope

### Minimum boundary objects

- SupportOntologyRelease (global; packaged per DD-002)

- SCR_TBox_Release (tenant-scoped; packaged per DD-002; references SupportOntologyRelease dependencies; includes tenant_id)

- SCR_Runtime_LoadManifest (tenant-scoped; declares which SCR_TBox_Release is loaded for a tenant/runtime instance; includes tenant_id)

### 3.2 Upstream evidence prerequisite for downstream loading (anti-drift)

### The SCR Customer Runtime MUST reject loading an SCR_TBox_Release unless

- the release includes (or is cryptographically bound to) its CompilationEvidence, and

- the release tenant_id matches the SCR_Runtime_LoadManifest tenant_id.

### Operationally (minimum)

- SCR_TBox_Release packages include an /evidence/* directory containing compilation evidence.

- The release manifest.json includes SHA-256 digests for evidence files in its file list.

- If evidence is missing or digest verification fails, the release is inadmissible for loading.

This ensures the chain-of-truth is unbroken: upstream compilation gates are a prerequisite for downstream enforcement.

## 4. Governance model and binding boundary

### 4.1 Implementation-agnostic grounding

The system is implementation-agnostic. Specific schemas, cryptographic mechanisms, storage engines, network protocols, and vendor tooling are UNKNOWN or DELEGATED.

### 4.2 Separation of planes (“Lego rule”) with global vs tenanted boundary

Global plane (platform/vendor owned; immutable):

- Doctrine (B1–B10) and CIRs (I1–I23) are global and universal. They apply to every tenant.

- Tenants cannot override doctrine or invariants (no BYO doctrine; no tenant-specific “exceptions”).

- The Support Ontology Engine is global and produces globally versioned SupportOntologyRelease artifacts.

Tenanted plane (customer-owned configuration; compiled under global constraints):

- Tenants define their own organizational domains, workflow rules, TargetSets, and routing logic.

- These are “local laws” only insofar as they compile into canonical, checkable runtime structures without violating global beliefs/invariants.

Collision/enforcement point:

- The SCR TBox Engine compiles tenant workflow definitions in a tenanted execution context while enforcing global doctrine + global kernel semantics.

- Compilation fails (non-permissive) when tenant inputs require defaults, imply authority, or violate a global invariant.

Controls (operational control specification):

- Document: “AI–Ontological Governance & Lifecycle Specification V1”

- Role: executable canonical contracts and lifecycle machinery (CIR/CSC), authority derivation, deterministic evaluation rules.

Traceability rule: Every binding control (CIR/CSC record) must trace to doctrinal source belief(s) (B#). No “floating rules.”

Binding boundary model:

- Prose is non-binding commentary unless represented as canonical contracts in the control specification.

- No-defaults: if a canonical record requires inferred fields, it fails per disposition rules.

## 5. MVP boundaries, operational models, and genesis

Environments:

- OFE-Kernel: Support Ontology Engine (Semantic Kernel) — global

- OFE-Compiler: SCR TBox Engine (Logical Compiler) — tenanted execution context

- SCR: Customer Runtime — tenant-scoped

Genesis seeding: Initial authority must be seeded by explicit events anchored to a root-of-trust.

MVP includes:

- Global doctrine and CIRs (platform-owned; universal)

- Lifecycle control specification (CIR/CSC)

- OFE-Kernel runtime producing global SupportOntologyRelease + release evidence

- OFE-Compiler runtime producing tenant-scoped SCR_TBox_Release + compilation evidence

- SCR customer runtime (tenant ledger; authority/execution/control events; target sets; as-of recomputation)

- Promotion discipline and load binding via SCR_Runtime_LoadManifest

MVP excludes:

- BYO doctrine

- Constraints (DD-004: explicitly unsupported)

- Complex set reasoning

- Claimability model

MVP operational assumptions (explicit):

- Ordering determinism (DD-003): each tenant ledger partition has a single ordering authority that assigns event_time at commit.

- Eligibility enforcement (DD-005): eligibility is evaluated and recorded prior to execution commitment; ineligible/unknown outcomes are non-permissive.

- Chain-of-truth (DD-006): upstream evidence is a prerequisite for downstream loading.

## 6. Canonical document set and relocation map

To preserve “one canonical location” per binding rule while keeping documents short and purpose-driven, binding material that previously appeared in Product Spec Draft 0.6 Sections 5–7 and the Decisions Register has been relocated as follows:

- Canonical governance and lifecycle contracts (CIR/CSC), risk matrix, authority derivation, and Target Set Library:

- AI–Ontological Governance & Lifecycle Specification (Canonical Contracts)

- Decisions register (DD-001…DD-007) and archived Draft 0.6 Sections 5–7 (verbatim):

- AI–Semantic Control OS Decisions Register (DD-001…DD-007) with Archived Sections

This document intentionally does not repeat the binding contract definitions (CIR/CSC) to avoid drift.

Patch Addendum — 2026-03-05 — Repository Governance (BR-00.1 Implemented)

Change type: Documentation alignment to operational state.

Repository Governance (Operational Substrate):

- Canonical repository: https://github.com/Paul-Engender/BB1

- Contract: tools/repo_skeleton_paths.txt defines required repository directories for the build-readiness substrate.

- Enforcement: CI workflow repo-skeleton-check at .github/workflows/repo-skeleton-check.yml validates the contract on push/PR.

- Proof: CI uploads artifact repo-skeleton-proof containing commit.txt, tree.txt, sha256sums.txt (retention-days: 30).

Trace: Phase-0 Build-Readiness Backlog item BR-00.1 is now evidenced as complete in the canonical repo.
