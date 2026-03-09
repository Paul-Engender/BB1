# Specs Consolidated Presentation

Generated: `2026-03-08T11:32:22+00:00`
Source root: `C:/Users/PaulWeber/Documents/BB1/specs`

## Executive View

- Total markdown specs: **63**
- Additional non-markdown assets: **2**
- Status distribution:
  - `APPROVED`: 34
  - `IS`: 14
  - `UNSPECIFIED`: 7
  - `DIRECTIONAL`: 2
  - `BUILD`: 1
  - `CANONICAL`: 1
  - `DESIGN-TO-BUILD`: 1
  - `DOCTRINE`: 1
  - `PENDING`: 1
  - `REFERENCE`: 1

## Theme Portfolio

| Theme | Document Count |
| --- | ---: |
| Canonical Governance Set | 7 |
| Foundation Technical Specs | 4 |
| Implementation Planning and Backlog | 4 |
| Product and Runtime Contracts | 11 |
| Spec Upgrade Program | 8 |
| Support Ontology Program | 29 |

## Presentation Cards

### Canonical Governance Set

#### AI–Semantic Control OS — Canonical Document Set

- File: `specs/ontoForge_00_Canonical-Document-Set_Map_v1.0.md`
- Status: `Reference map (canonical locations)`
- Version: `1.0`
- Date: `2026-03-04`
- Owner: `UNSPECIFIED`
- Summary: title: AI–Semantic Control OS — Canonical Document Set Map
- Highlights:
  - **Document:** Beliefs and Governance Framework.
  - **Constraint:** Non-operational by design.
  - **Document:** AI–Ontological Governance & Lifecycle Specification.

#### This document is non-operational by design

- File: `specs/ontoForge_01_Doctrine_v1.1.md`
- Status: `Doctrine (non-operational by design)`
- Version: `0.6 (source text, formatted)`
- Date: `2026-03-04`
- Owner: `UNSPECIFIED`
- Summary: Beliefs and Governance Framework
- Highlights:
  - It does not define executable controls, canonical schemas, compilation algorithms, or lifecycle state transitions.
  - It does not create operational authority by its existence.
  - Its content becomes operational only when explicitly operationalized into binding canonical contracts in a lower-order control specification (e.g., the AI-Ontological Governance & Lifecycle Specification) and then adopted via governed processes.

#### 0. Document intent and binding boundary

- File: `specs/ontoForge_02_Lifecycle-Specification_v1.1.md`
- Status: `Canonical Contracts (binding)`
- Version: `1.1-r (Refactored to Canonical Contracts)`
- Date: `2026-03-04`
- Owner: `UNSPECIFIED`
- Summary: AI–Ontological Governance & Lifecycle Specification
- Highlights:
  - Non-binding commentary: explanatory prose intended for human understanding.
  - Binding contracts: canonical records that are permitted to influence admission decisions, authority derivation, policy evaluation, or execution commitment.
  - A) Canonical Invariant Record (CIR) — bridges beliefs to enforceable obligations.

#### AI–Semantic Control OS Product Specification

- File: `specs/ontoForge_03_Product-Spec_V1.1.md`
- Status: `Directional (architecture and product scope)`
- Version: `Draft 0.7 (Refactored)`
- Date: `2026-03-04`
- Owner: `UNSPECIFIED`
- Summary: Global (platform/vendor owned). Immutable per release.
- Highlights:
  - AI–Ontological Governance & Lifecycle Specification (Canonical Contracts)
  - Beliefs and Governance Framework
  - Bring Your Own Doctrine is not permitted. Tenants cannot override, replace, or extend the platform’s global doctrine or CIRs in any way that would affect binding outcomes.

#### AI–Semantic Control OS Decisions Register

- File: `specs/ontoForge_04_Decisions-Register_v1.1.md`
- Status: `Approved decisions register; includes archived Draft 0.6 sections`
- Version: `1.0`
- Date: `2026-03-04`
- Owner: `UNSPECIFIED`
- Summary: AI–Semantic Control OS Decisions Register
- Highlights:
  - All locally minted entities MUST use UUIDv7 identifiers expressed as cid:<uuidv7>.
  - Prefix binding: cid → https://example.org/id/
  - Expanded canonical form: https://example.org/id/<uuidv7>

#### Project Operating Protocol

- File: `specs/ontoForge_80_ProjectOperatingProtocolV01.md`
- Status: `UNSPECIFIED`
- Version: `UNSPECIFIED`
- Date: `UNSPECIFIED`
- Owner: `UNSPECIFIED`
- Summary: This protocol defines the operational rules for managing work, updating project artifacts, and reporting progress during project execution. It operates strictly on the implementation and coordination plane. It does not create or modify binding project governance contracts.
- Highlights:
  - Project plans
  - Design and architecture documents
  - Sprint/cycle execution

#### Work Decomposition Protocol

- File: `specs/ontoForge_81_WorkDecomposition_Protocol_v01.md`
- Status: `UNSPECIFIED`
- Version: `UNSPECIFIED`
- Date: `UNSPECIFIED`
- Owner: `UNSPECIFIED`
- Summary: Define the “agent-executable” decomposition level so bounded-context agents can complete tasks within their attention and reliability constraints.
- Highlights:
  - Single Output: Has exactly one primary deliverable (one artifact).
  - Clear I/O: Has explicitly defined inputs and outputs.
  - Bounded Dependencies: Relies on $\le2$ upstream artifacts.

### Foundation Technical Specs

#### Evaluator Boundary v1 Specification

- File: `specs/evaluator_boundary_v1.md`
- Status: `UNSPECIFIED`
- Version: `UNSPECIFIED`
- Date: `UNSPECIFIED`
- Owner: `UNSPECIFIED`
- Summary: *Status: DRAFT*
- Highlights:
  - **Commit**: A proposed state transition, packaged as a collection of artifacts and claims.
  - **Ruleset**: A collection of stipulations, requirements, and policies that govern the validity of a commit. This ruleset is itself an information artifact identified by a `cid:`.
  - **Evaluation**: The process of applying a Ruleset to a Commit.

#### Identity CID Specification (cid:)

- File: `specs/identity_cid_uuidv7.md`
- Status: `UNSPECIFIED`
- Version: `UNSPECIFIED`
- Date: `UNSPECIFIED`
- Owner: `UNSPECIFIED`
- Summary: *Status: DRAFT*
- Highlights:
  - **`<uuidv7>`**: A 36-character UUID version 7 string, providing a time-ordered, globally unique identifier.
  - **`<sha256_hash_of_canonical_content>`**: A 64-character hexadecimal representation of the SHA-256 digest of the content's canonical form.
  - Identity CID Specification (cid:)

#### IssuerProof v1 Specification

- File: `specs/issuerproof_v1.md`
- Status: `UNSPECIFIED`
- Version: `UNSPECIFIED`
- Date: `UNSPECIFIED`
- Owner: `UNSPECIFIED`
- Summary: *Status: DRAFT*
- Highlights:
  - **`iss` (Issuer)**: REQUIRED. A Decentralized Identifier (DID) URI identifying the entity that issued the proof.
  - **`sub` (Subject)**: REQUIRED. A `cid:` identifying the subject of the assertion (e.g., a piece of code, a document, another proof).
  - **`iat` (Issued At)**: REQUIRED. A Unix timestamp (integer seconds) indicating when the proof was issued.

#### Ledger API and Ordering Rules

- File: `specs/ledger_api_and_ordering.md`
- Status: `UNSPECIFIED`
- Version: `UNSPECIFIED`
- Date: `UNSPECIFIED`
- Owner: `UNSPECIFIED`
- Summary: *Status: DRAFT*
- Highlights:
  - **`202 Accepted`**: The request has been accepted for processing. The response includes a transaction ID for tracking. The event is not yet committed.
  - **`400 Bad Request`**: The request body is malformed or the `event_cid` is invalid.
  - **`403 Forbidden`**: The caller is not the designated ordering authority.

### Implementation Planning and Backlog

#### Integrated Project Plan

- File: `specs/Integrated Project Plan.md`
- Status: `Design-to-Build Transition Tenancy model: Global Doctrine / Tenanted Workflows Baseline stack direction (non-prescriptive): Option B (GCP + Python + Ontology-as-Code CI)`
- Version: `UNSPECIFIED`
- Date: `UNSPECIFIED`
- Owner: `UNSPECIFIED`
- Summary: Document date: 2026-03-04 Plan version: v0.3 (standalone build-readiness plan)
- Highlights:
  - Build readiness: resolve the concrete UNKNOWN/DELEGATED items that block an end-to-end vertical slice.
  - MVP implementation: deliver a minimal “three-runtime” vertical slice demonstrating deterministic governance flow (S1–S6) up to execution commitment, with evidence-chain enforcement.
  - Ontology-as-Code discipline: treat ontologies and control primitives as versioned code artifacts with CI validation and packaged evidence.

#### ontoForge 90 Implementation-plane backlog

- File: `specs/ontoForge_90_Implementation-plane_backlog.md`
- Status: `Build readiness decomposition (Phase 0)-----Plane Note (Non-Binding)`
- Version: `UNSPECIFIED`
- Date: `UNSPECIFIED`
- Owner: `paul`
- Summary: Implementation-plane backlog for ontoForge (AI-Semantic Control OS)
- Highlights:
  - IS: what is evidenced by artifacts, logs, and verifiable outputs.
  - OUGHT: planned repo paths and planned outputs are OUGHT until evidenced.
  - UNKNOWN: anything not yet evidenced or contract-specified.

#### Phase 0 Build-Readiness Backlog v0.1 (Blocking Gaps)

- File: `specs/ontoForge_91_Build-Readiness Backlog v0.1.md`
- Status: `UNSPECIFIED`
- Version: `UNSPECIFIED`
- Date: `UNSPECIFIED`
- Owner: `UNSPECIFIED`
- Summary: This backlog decomposes GAP-01…GAP-06 into agent-executable work items.
- Highlights:
  - Phase 0 Build-Readiness Backlog v0.1 (Blocking Gaps)
  - GAP-00 Repo skeleton (paths)
  - GAP-01 Identity & minting (cid:)

#### Phase 0 Evidence Pack v0.1

- File: `specs/ontoForge_92_Evidence-Pack_v01.md`
- Status: `pending review`
- Version: `UNSPECIFIED`
- Date: `2026-03-05`
- Owner: `UNSPECIFIED`
- Summary: Plan: Implementation (evidence/validation log; non-binding)-----1. Scope
- Highlights:
  - COMPLETED = outputs claimed to exist, but validation not yet evidenced here.
  - DONE = validation evidenced here with artifact locator + integrity hash + verifier output (or CI run ID with immutable logs).
  - Phase 0 Evidence Pack v0.1

### Product and Runtime Contracts

#### Product Boundary Objects v1

- File: `specs/product_boundary_objects_v1.md`
- Status: `IS`
- Version: `UNSPECIFIED`
- Date: `2026-03-07`
- Owner: `paul`
- Summary: `global`
- Highlights:
  - `SupportOntologyRelease`
  - `SCR_TBox_Release`
  - `SCR_Runtime_LoadManifest`

#### Product Event Model v1

- File: `specs/product_event_model_v1.md`
- Status: `IS`
- Version: `UNSPECIFIED`
- Date: `2026-03-06`
- Owner: `paul`
- Summary: add/remove/delegate authority through explicit eventing.
- Highlights:
  - AuthorityEvents
  - AuthorizationDecision events (with reason codes)
  - EligibilityDecision events (with reason codes)

#### Patch Addendum - Runtime Instantiation, Internal Lifecycle Candidate, Boundary Object, and Operational Instantiation Clarification

- File: `specs/product_runtime_instantiation_clarification_addendum_2026-03-07.md`
- Status: `Directional clarification addendum`
- Version: `UNSPECIFIED`
- Date: `2026-03-07`
- Owner: `UNSPECIFIED`
- Summary: Canonical location intent: AI-Semantic Control OS Product Specification (addendum section)
- Highlights:
  - internal lifecycle candidate
  - runtime lifecycle instance
  - boundary object

#### Product Runtime Mapping v1

- File: `specs/product_runtime_mapping_v1.md`
- Status: `IS`
- Version: `UNSPECIFIED`
- Date: `2026-03-06`
- Owner: `paul`
- Summary: Plan Item: P1-011
- Highlights:
  - runtime-internal lifecycle candidates
  - runtime lifecycle instances
  - boundary objects

#### Runtime 1 Hardening Addendum v1

- File: `specs/runtime1_hardening_addendum_v1.md`
- Status: `IS`
- Version: `UNSPECIFIED`
- Date: `2026-03-07`
- Owner: `paul`
- Summary: Plan Item: P1-014
- Highlights:
  - Packager supports deterministic tar metadata, deterministic ordering, and
  - Runtime 1 uses deterministic mode by default for support-release builds.
  - Runtime 1 validates generated `release_manifest.json` against

#### Runtime 1 Support Release Engine v1

- File: `specs/runtime1_support_release_engine_v1.md`
- Status: `IS`
- Version: `UNSPECIFIED`
- Date: `2026-03-07`
- Owner: `paul`
- Summary: Plan Item: P1-013
- Highlights:
  - kernel ontology + SHACL integrity checks
  - release-candidate evaluation outputs
  - packaging support ontology payload with evidence files

#### Runtime 2 Compiled Control Primitives Contract v1

- File: `specs/runtime2_compiled_control_primitives_v1.md`
- Status: `APPROVED`
- Version: `UNSPECIFIED`
- Date: `2026-03-07`
- Owner: `paul`
- Summary: Plan Item: P1-020
- Highlights:
  - `specs/ontoForge_03_Product-Spec_V1.1.md`
  - `specs/ontoForge_04_Decisions-Register_v1.1.md`
  - `specs/ontoForge_02_Lifecycle-Specification_v1.1.md`

#### Runtime 2 Compiler Contract Baseline Review v1

- File: `specs/runtime2_compiler_contract_baseline_review_v1.md`
- Status: `APPROVED`
- Version: `UNSPECIFIED`
- Date: `2026-03-07`
- Owner: `paul`
- Summary: Plan Item: P1-020
- Highlights:
  - `specs/runtime2_tenant_workflow_input_contract_v1.md` (`TASK-20.2`)
  - `specs/runtime2_compiled_control_primitives_v1.md` (`TASK-20.3`)
  - `specs/runtime2_support_admissibility_matrix_v1.md` (`TASK-20.4`)

#### Runtime 2 Semantic Gate Requirements v1

- File: `specs/runtime2_semantic_gate_requirements_v1.md`
- Status: `APPROVED`
- Version: `UNSPECIFIED`
- Date: `2026-03-07`
- Owner: `paul`
- Summary: Plan Item: P1-021
- Highlights:
  - `specs/ontoForge_02_Lifecycle-Specification_v1.1.md`
  - `specs/ontoForge_03_Product-Spec_V1.1.md`
  - `specs/ontoForge_04_Decisions-Register_v1.1.md`

#### Runtime 2 Support Admissibility Matrix v1

- File: `specs/runtime2_support_admissibility_matrix_v1.md`
- Status: `APPROVED`
- Version: `UNSPECIFIED`
- Date: `2026-03-07`
- Owner: `paul`
- Summary: Plan Item: P1-020
- Highlights:
  - `specs/ontoForge_02_Lifecycle-Specification_v1.1.md`
  - `specs/ontoForge_03_Product-Spec_V1.1.md`
  - `specs/ontoForge_04_Decisions-Register_v1.1.md`

#### Runtime 2 Tenant Workflow Input Contract v1

- File: `specs/runtime2_tenant_workflow_input_contract_v1.md`
- Status: `APPROVED`
- Version: `UNSPECIFIED`
- Date: `2026-03-07`
- Owner: `paul`
- Summary: Plan Item: P1-020
- Highlights:
  - `specs/ontoForge_02_Lifecycle-Specification_v1.1.md`
  - `specs/ontoForge_03_Product-Spec_V1.1.md`
  - `specs/ontoForge_04_Decisions-Register_v1.1.md`

### Spec Upgrade Program

#### Canonical Spec Set Baseline v1

- File: `specs/spec_upgrade/canonical_spec_set_v1.md`
- Status: `IS`
- Version: `UNSPECIFIED`
- Date: `2026-03-06`
- Owner: `paul`
- Summary: Plan Item: P1-009
- Highlights:
  - Governance and doctrine contract sources.
  - Operating and decomposition protocols.
  - Phase-0 backlog and evidence gate source records.

#### Spec Migration Delta Register v1

- File: `specs/spec_upgrade/migration_delta_register_v1.md`
- Status: `IS`
- Version: `UNSPECIFIED`
- Date: `2026-03-06`
- Owner: `paul`
- Summary: Plan Item: P1-009
- Highlights:
  - `specs/ontoForge_90_Implementation-plane_backlog.md`
  - `specs/ontoForge_91_Build-Readiness Backlog v0.1.md`
  - `specs/ontoForge_92_Evidence-Pack_v01.md`

#### Pilot Spec Migration Report v1

- File: `specs/spec_upgrade/pilot_migration_report_v1.md`
- Status: `IS`
- Version: `UNSPECIFIED`
- Date: `2026-03-06`
- Owner: `paul`
- Summary: Plan Item: P1-009
- Highlights:
  - Source scope: OF-90 / OF-91 backlog intent and OF-92 evidence-gate framing.
  - Target scope: P1-009 `TASK-09.1` through `TASK-09.4` with EP-09 closure criteria.
  - Exercises all critical control upgrades: ID mapping, decomposition enforcement, executable validation, evidence hashing, and phase-gate scoping.

#### Spec Contract Validation Matrix v1

- File: `specs/spec_upgrade/spec_contract_validation_matrix_v1.md`
- Status: `IS`
- Version: `UNSPECIFIED`
- Date: `2026-03-06`
- Owner: `paul`
- Summary: Plan Item: P1-009
- Highlights:
  - `specs/spec_upgrade/canonical_spec_set_v1.md`
  - `specs/spec_upgrade/migration_delta_register_v1.md`
  - `bootstrap/task_ledger.csv`

#### Wave-2 Canonical Spec Set Baseline v1

- File: `specs/spec_upgrade/wave2_canonical_spec_set_v1.md`
- Status: `IS`
- Version: `UNSPECIFIED`
- Date: `2026-03-06`
- Owner: `paul`
- Summary: Plan Item: P1-010
- Highlights:
  - `specs/spec_upgrade/canonical_spec_set_v1.md`
  - `specs/ontoForge_00_Canonical-Document-Set_Map_v1.0.md`
  - recurring migration execution controls,

#### Wave-2 Migration Delta Register v1

- File: `specs/spec_upgrade/wave2_migration_delta_register_v1.md`
- Status: `IS`
- Version: `UNSPECIFIED`
- Date: `2026-03-06`
- Owner: `paul`
- Summary: Plan Item: P1-010
- Highlights:
  - Wave-2 Migration Delta Register v1
  - Purpose
  - Delta Register (Wave-2)

#### Wave-2 Pilot Migration Report v1

- File: `specs/spec_upgrade/wave2_pilot_migration_report_v1.md`
- Status: `IS`
- Version: `UNSPECIFIED`
- Date: `2026-03-06`
- Owner: `paul`
- Summary: Plan Item: P1-010
- Highlights:
  - Baseline refresh (`TASK-10.1`)
  - Delta hardening (`TASK-10.2`)
  - Validation matrix update (`TASK-10.3`)

#### Wave-2 Spec Contract Validation Matrix v1

- File: `specs/spec_upgrade/wave2_spec_contract_validation_matrix_v1.md`
- Status: `IS`
- Version: `UNSPECIFIED`
- Date: `2026-03-06`
- Owner: `paul`
- Summary: Plan Item: P1-010
- Highlights:
  - Wave-2 Spec Contract Validation Matrix v1
  - Purpose
  - Validation Matrix

### Support Ontology Program

#### Support Ontology Authority Model v1

- File: `specs/support_ontology_authority_model_v1.md`
- Status: `APPROVED`
- Version: `UNSPECIFIED`
- Date: `2026-03-07`
- Owner: `paul`
- Summary: Plan Item: P1-019
- Highlights:
  - `specs/ontoForge_02_Lifecycle-Specification_v1.1.md`
  - `specs/ontoForge_03_Product-Spec_V1.1.md`
  - `specs/ontoForge_04_Decisions-Register_v1.1.md`

#### Support Ontology CSC Stage Model v1

- File: `specs/support_ontology_csc_stage_model_v1.md`
- Status: `APPROVED`
- Version: `UNSPECIFIED`
- Date: `2026-03-07`
- Owner: `paul`
- Summary: Plan Item: P1-017
- Highlights:
  - truth product
  - permitted side effects
  - scope of state and inputs

#### Support Ontology External Ontology Policy v1

- File: `specs/support_ontology_external_ontology_policy_v1.md`
- Status: `APPROVED`
- Version: `UNSPECIFIED`
- Date: `2026-03-07`
- Owner: `paul`
- Summary: Plan Item: P1-015
- Highlights:
  - `specs/support_ontology_governance_incorporation_model_v1.md`
  - `specs/ontoForge_01_Doctrine_v1.1.md`
  - `specs/ontoForge_02_Lifecycle-Specification_v1.1.md`

#### Support Ontology Governance Incorporation Model v1

- File: `specs/support_ontology_governance_incorporation_model_v1.md`
- Status: `APPROVED`
- Version: `UNSPECIFIED`
- Date: `2026-03-07`
- Owner: `paul`
- Summary: Plan Item: P1-015
- Highlights:
  - constitutional sources (doctrine, lifecycle, decisions), and
  - executable support-layer contracts consumed by Runtime 1 and Runtime 2.
  - `specs/ontoForge_01_Doctrine_v1.1.md`

#### Support Ontology Identifier and MVP Boundary v1

- File: `specs/support_ontology_identifier_and_mvp_boundary_v1.md`
- Status: `APPROVED`
- Version: `UNSPECIFIED`
- Date: `2026-03-07`
- Owner: `paul`
- Summary: Plan Item: P1-015
- Highlights:
  - DD-001 (identifier and versioning discipline)
  - DD-003 (event ordering authority and deterministic ordering)
  - DD-004 (MVP constraint exclusion and reason codes)

#### Support Ontology Invariant Model v1

- File: `specs/support_ontology_invariant_model_v1.md`
- Status: `APPROVED`
- Version: `UNSPECIFIED`
- Date: `2026-03-07`
- Owner: `paul`
- Summary: Plan Item: P1-017
- Highlights:
  - `specs/ontoForge_02_Lifecycle-Specification_v1.1.md`
  - `specs/ontoForge_04_Decisions-Register_v1.1.md`
  - `specs/product_runtime_instantiation_clarification_addendum_2026-03-07.md`

#### Support Ontology Machine Contract Map v1

- File: `specs/support_ontology_machine_contract_map_v1.md`
- Status: `APPROVED`
- Version: `UNSPECIFIED`
- Date: `2026-03-07`
- Owner: `paul`
- Summary: Plan Item: P1-017
- Highlights:
  - ontology terms
  - SHACL rules
  - deterministic validator/runtime logic

#### Support Ontology Namespace and Import Policy v1

- File: `specs/support_ontology_namespace_policy_v1.md`
- Status: `APPROVED`
- Version: `UNSPECIFIED`
- Date: `2026-03-07`
- Owner: `paul`
- Summary: Plan Item: P1-016
- Highlights:
  - `specs/support_ontology_release_composition_v1.md`
  - `specs/product_runtime_instantiation_clarification_addendum_2026-03-07.md`
  - `ontology/kernel.ttl`

#### Support Ontology Negative Fixture Set v1

- File: `specs/support_ontology_negative_fixture_set_v1.md`
- Status: `APPROVED`
- Version: `UNSPECIFIED`
- Date: `2026-03-07`
- Owner: `paul`
- Summary: Plan Item: P1-023
- Highlights:
  - `ontology/negative_examples/targetref_missing_isaboutentity.ttl`
  - `ontology/negative_examples/targetref_two_isaboutentity.ttl`
  - `ontology/negative_examples/stipulation_two_stipulateson.ttl`

#### Support Ontology Operation-Control Model v1

- File: `specs/support_ontology_operation_model_v1.md`
- Status: `APPROVED`
- Version: `UNSPECIFIED`
- Date: `2026-03-07`
- Owner: `paul`
- Summary: Plan Item: P1-019
- Highlights:
  - `specs/ontoForge_02_Lifecycle-Specification_v1.1.md`
  - `specs/ontoForge_03_Product-Spec_V1.1.md`
  - `specs/ontoForge_04_Decisions-Register_v1.1.md`

#### Support Ontology Positive Fixture Set v1

- File: `specs/support_ontology_positive_fixture_set_v1.md`
- Status: `APPROVED`
- Version: `UNSPECIFIED`
- Date: `2026-03-07`
- Owner: `paul`
- Summary: Plan Item: P1-023
- Highlights:
  - `ontology/examples/example-target-reference.ttl`
  - `ontology/examples/example-stipulation.ttl`
  - `ontology/examples/example-promotion-chain.ttl`

#### Support Ontology Post-Review Hardening Review v1

- File: `specs/support_ontology_post_review_hardening_review_v1.md`
- Status: `APPROVED`
- Version: `UNSPECIFIED`
- Date: `2026-03-08`
- Owner: `paul`
- Summary: Plan Item: P1-024
- Highlights:
  - `ontology/kernel.ttl`
  - `ontology/kernel.shacl.ttl`
  - `specs/support_ontology_release_payload_contract_v1.md`

#### Support Ontology Priority-1 Uplift Review v1

- File: `specs/support_ontology_priority1_uplift_review_v1.md`
- Status: `APPROVED`
- Version: `UNSPECIFIED`
- Date: `2026-03-08`
- Owner: `paul`
- Summary: Plan Item: P1-025
- Highlights:
  - `TargetSet`
  - `ScopeBoundary`
  - `ActionSpecification`

#### Support Ontology Priority-2 Uplift Review v1

- File: `specs/support_ontology_priority2_uplift_review_v1.md`
- Status: `APPROVED`
- Version: `UNSPECIFIED`
- Date: `2026-03-08`
- Owner: `paul`
- Summary: Plan Item: P1-026
- Highlights:
  - `CompiledControlPrimitive` plus the required primitive family hierarchy
  - explicit output/provenance anchors for support release references, dependency binding records, gate execution records, compile decision records, evidence digest records, and compile trace bundles
  - explicit `CompileReasonCodePolicy` and `ReasonCodeCategory` vocabulary anchors

#### Support Ontology Provenance Traceability Review v1

- File: `specs/support_ontology_provenance_traceability_review_v1.md`
- Status: `APPROVED`
- Version: `UNSPECIFIED`
- Date: `2026-03-07`
- Owner: `paul`
- Summary: Plan Item: P1-022
- Highlights:
  - `specs/support_ontology_traceability_model_v1.md` (`TASK-22.2`)
  - `specs/support_release_provenance_model_v1.md` (`TASK-22.3`)
  - `specs/support_to_tbox_dependency_provenance_v1.md` (`TASK-22.4`)

#### Support Ontology Reason-Code Evidence Contract v1

- File: `specs/support_ontology_reasoncode_evidence_contract_v1.md`
- Status: `APPROVED`
- Version: `UNSPECIFIED`
- Date: `2026-03-07`
- Owner: `paul`
- Summary: Plan Item: P1-021
- Highlights:
  - `specs/ontoForge_04_Decisions-Register_v1.1.md`
  - `specs/ontoForge_02_Lifecycle-Specification_v1.1.md`
  - `specs/product_runtime_instantiation_clarification_addendum_2026-03-07.md`

#### Support Ontology Release Composition v1

- File: `specs/support_ontology_release_composition_v1.md`
- Status: `APPROVED`
- Version: `UNSPECIFIED`
- Date: `2026-03-07`
- Owner: `paul`
- Summary: Plan Item: P1-016
- Highlights:
  - `specs/support_ontology_ttl_admission_register_v1.md`
  - `specs/support_ontology_identifier_and_mvp_boundary_v1.md`
  - `specs/product_boundary_objects_v1.md`

#### Support Ontology Release Payload Contract v1

- File: `specs/support_ontology_release_payload_contract_v1.md`
- Status: `APPROVED`
- Version: `UNSPECIFIED`
- Date: `2026-03-07`
- Owner: `paul`
- Summary: Plan Item: P1-016
- Highlights:
  - `specs/support_ontology_release_composition_v1.md` (what belongs in payload)
  - `specs/support_ontology_namespace_policy_v1.md` (namespace/import discipline)
  - `runtime/runtime1_engine.py` and `tools/packager.py` (how payload is produced)

#### Support Ontology Runtime2 Readiness Gate v1

- File: `specs/support_ontology_runtime2_readiness_gate_v1.md`
- Status: `APPROVED`
- Version: `UNSPECIFIED`
- Date: `2026-03-07`
- Owner: `paul`
- Summary: Plan Item: P1-023
- Highlights:
  - `specs/support_ontology_positive_fixture_set_v1.md`
  - `specs/support_ontology_negative_fixture_set_v1.md`
  - `specs/support_to_tbox_dependency_provenance_v1.md`

#### Support Ontology Runtime2 Readiness Review v1

- File: `specs/support_ontology_runtime2_readiness_review_v1.md`
- Status: `APPROVED`
- Version: `UNSPECIFIED`
- Date: `2026-03-07`
- Owner: `paul`
- Summary: Plan Item: P1-023
- Highlights:
  - `specs/support_ontology_positive_fixture_set_v1.md` (`TASK-23.2`)
  - `specs/support_ontology_negative_fixture_set_v1.md` (`TASK-23.3`)
  - `specs/support_ontology_runtime2_readiness_gate_v1.md` (`TASK-23.4`)

#### Support Ontology Target-Scope-Action-Effect Model v1

- File: `specs/support_ontology_target_scope_action_model_v1.md`
- Status: `APPROVED`
- Version: `UNSPECIFIED`
- Date: `2026-03-07`
- Owner: `paul`
- Summary: Plan Item: P1-019
- Highlights:
  - `specs/ontoForge_02_Lifecycle-Specification_v1.1.md`
  - `specs/ontoForge_03_Product-Spec_V1.1.md`
  - `specs/ontoForge_04_Decisions-Register_v1.1.md`

#### Support Ontology Traceability Model v1

- File: `specs/support_ontology_traceability_model_v1.md`
- Status: `APPROVED`
- Version: `UNSPECIFIED`
- Date: `2026-03-07`
- Owner: `paul`
- Summary: Plan Item: P1-022
- Highlights:
  - `specs/ontoForge_01_Doctrine_v1.1.md`
  - `specs/ontoForge_02_Lifecycle-Specification_v1.1.md`
  - `specs/ontoForge_03_Product-Spec_V1.1.md`

#### Support Ontology TTL Admission Register v1

- File: `specs/support_ontology_ttl_admission_register_v1.md`
- Status: `APPROVED`
- Version: `UNSPECIFIED`
- Date: `2026-03-07`
- Owner: `paul`
- Summary: Plan Item: P1-015
- Highlights:
  - `APPROVED`: allowed for binding use in the declared scope
  - `NOT_APPROVED`: explicitly rejected for binding use
  - `NON_BINDING`: allowed only as non-binding reference or fixture

#### Support Ontology TTL Inventory v1

- File: `specs/support_ontology_ttl_inventory_v1.md`
- Status: `IS`
- Version: `UNSPECIFIED`
- Date: `2026-03-07`
- Owner: `paul`
- Summary: Plan Item: P1-015
- Highlights:
  - `ontology/*.ttl`
  - `ontology/examples/*.ttl`
  - `ontology/negative_examples/*.ttl`

#### Support Ontology Validation Gate Review v1

- File: `specs/support_ontology_validation_gate_review_v1.md`
- Status: `APPROVED`
- Version: `UNSPECIFIED`
- Date: `2026-03-07`
- Owner: `paul`
- Summary: Plan Item: P1-021
- Highlights:
  - `specs/support_ontology_validation_uplift_v1.md` (`TASK-21.2`)
  - `specs/runtime2_semantic_gate_requirements_v1.md` (`TASK-21.3`)
  - `specs/support_ontology_reasoncode_evidence_contract_v1.md` (`TASK-21.4`)

#### Support Ontology Validation Uplift v1

- File: `specs/support_ontology_validation_uplift_v1.md`
- Status: `APPROVED`
- Version: `UNSPECIFIED`
- Date: `2026-03-07`
- Owner: `paul`
- Summary: Plan Item: P1-021
- Highlights:
  - `specs/ontoForge_02_Lifecycle-Specification_v1.1.md`
  - `specs/ontoForge_03_Product-Spec_V1.1.md`
  - `specs/ontoForge_04_Decisions-Register_v1.1.md`

#### Support Ontology W3 Compiler Vocabulary Review v1

- File: `specs/support_ontology_w3_compiler_vocabulary_review_v1.md`
- Status: `APPROVED`
- Version: `UNSPECIFIED`
- Date: `2026-03-07`
- Owner: `paul`
- Summary: Plan Item: P1-019
- Highlights:
  - authority model (`TASK-19.2`)
  - operation/control model (`TASK-19.3`)
  - target/scope/action/effect model (`TASK-19.4`)

#### Support Release Provenance Model v1

- File: `specs/support_release_provenance_model_v1.md`
- Status: `APPROVED`
- Version: `UNSPECIFIED`
- Date: `2026-03-07`
- Owner: `paul`
- Summary: Plan Item: P1-022
- Highlights:
  - `specs/support_ontology_release_payload_contract_v1.md`
  - `specs/support_ontology_reasoncode_evidence_contract_v1.md`
  - `specs/product_boundary_objects_v1.md`

#### Support to TBox Dependency Provenance v1

- File: `specs/support_to_tbox_dependency_provenance_v1.md`
- Status: `APPROVED`
- Version: `UNSPECIFIED`
- Date: `2026-03-07`
- Owner: `paul`
- Summary: Plan Item: P1-022
- Highlights:
  - `specs/runtime2_compiled_control_primitives_v1.md`
  - `specs/support_release_provenance_model_v1.md`
  - `specs/product_runtime_mapping_v1.md`

## Non-Markdown Assets Annex

- `specs/.gitkeep`
- `specs/support_ontology_external_mapping_candidates_v1.csv`
