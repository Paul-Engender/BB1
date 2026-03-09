# Proposed Support Ontology Full-Layer Backlog v1

Status: REFERENCE (approved backlog source; not active execution plan)
Owner: paul
Date: 2026-03-07
Approval: approved for protocol activation on 2026-03-07
Execution state: delivered through P1-015 .. P1-026; retained for traceability only
Purpose: Define the full body of work required for the Support Ontology layer to become the real upstream semantic contract for Runtime 2, not just a Runtime 1 packaging/runtime service.

## Primary Source Basis

Primary binding sources used for this backlog:
- `specs/ontoForge_01_Doctrine_v1.1.md`
- `specs/ontoForge_02_Lifecycle-Specification_v1.1.md`
- `specs/ontoForge_03_Product-Spec_V1.1.md`
- `specs/ontoForge_04_Decisions-Register_v1.1.md`

Current repo substrate assessed:
- `ontology/kernel.ttl`
- `ontology/kernel.shacl.ttl`
- `ontology/support.ttl`
- `ontology/scr_tbox.ttl`
- `runtime/kernel_gate.py`
- `runtime/runtime1_engine.py`
- `specs/product_runtime_mapping_v1.md`
- `specs/product_boundary_objects_v1.md`
- `specs/product_event_model_v1.md`

## Constitutional Boundary

Canonical meaning does not move into the Support Ontology layer.

The binding constitutional sources remain:
- doctrine and belief authority in `ontoForge_01`
- lifecycle and invariant authority in `ontoForge_02`
- approved implementation and packaging decisions in `ontoForge_04`

The Support Ontology layer may operationalize those sources into machine-readable contracts for Runtime 1 and Runtime 2, but it must not silently replace them as the authoritative source of meaning.

Every machine-readable support contract must preserve explicit traceability back to those governing sources.

## Approved Decision Anchors

This backlog depends explicitly on these decision anchors:
- `DD-001`: canonical identifier and versioning model
- `DD-002`: release artifact packaging model
- `DD-003`: runtime event ledger and ordering model
- `DD-004`: canonical constraint handling and reason codes
- `DD-005`: eligibility boundary enforcement model
- `DD-007`: global doctrine, tenanted workflows, no BYO doctrine

Implications for this backlog:
- all release and dependency identities must remain identifier-clean under `cid:<uuidv7>` rules
- ordering-dependent semantics must remain in deterministic mechanism territory where required
- unsupported MVP constraint semantics must not be reintroduced through alternative wording
- tenant compilation must remain fail-closed under global doctrine and invariants

## Asset Admission Rule

No existing `.ttl` file is admissible for binding use merely because it exists in the repo.

Binding use includes:
- release payload membership
- import dependency inside canonical support artifacts
- validation corpus used to justify admissibility
- compiler-facing input or output examples
- semantic source material used by Runtime 1 or Runtime 2 gates

Every existing `.ttl` file must be inventoried, reviewed, and explicitly approved by paul before it can be used in any binding path.

Until approved, a `.ttl` file is treated as non-binding exploratory material only.

## Architectural Reading

The Support Ontology layer is complete only when Runtime 2 can compile tenant workflow definitions against a released global semantic contract without consulting prose documents during compile or load.

That means the Support Ontology layer must provide all of the following:
- canonical global semantic vocabulary needed upstream of Runtime 2
- machine-readable lifecycle and admissibility semantics needed for compile safety
- compiler-facing tenant input constraints
- releaseable and version-bound global artifacts
- evidence and traceability proving why the global contract is admissible
- executable validation corpus proving valid and invalid tenant-facing semantics

## Governance Handling Model

Proposed treatment of governance inside the Support Ontology layer:
- Beliefs remain governance-plane authority in the doctrine and lifecycle sources. They do not become binding because they appear in prose. They become usable only when translated into explicit support-layer semantic contracts with traceability back to source beliefs.
- Risks are handled as fail-closed semantic conditions, invariant classes, gate failures, and reason-code families. Risk is not treated as free text commentary once it enters the support layer.
- Objectives are handled as explicit target, action, effect, measurement, and control semantics that can be compiled and enforced. Objectives that cannot be represented without defaults remain non-binding.
- The support layer therefore does not absorb governance as raw prose. It operationalizes approved governance into typed, machine-readable contracts and keeps source authority traceable.

## Provisional External Ontology Approach

External ontologies are treated as reference candidates, not automatically admissible dependencies.

Default policy:
- no direct binding import from an external ontology without explicit approval
- no semantic dependence on external terms by mere namespace reference
- all external ontology use must be version-pinned and reviewable
- semantic conflicts with doctrine, lifecycle, kernel contracts, and packaging rules must be resolved before use
- preferred pattern is curated adoption or translation into the support layer, not uncontrolled direct dependence

This policy is intentionally provisional and should be refined when the external ontology direction is provided.

## MVP Constraint Exclusion Rule

`DD-004` states that constraint fields are unsupported in MVP and must not appear in binding canonical records.

Therefore this backlog carries a hard boundary:
- no support-layer contract may reintroduce unsupported constraint semantics under alternative labels such as eligibility logic, routing policy, effect conditions, guard rules, or similar language
- if a semantic requirement depends on unsupported constraint structure, it must remain non-binding or be deferred until a future approved contract exists

## Current State

What is already strong:
- Runtime 1 release mechanics are operationally hardened.
- Release packaging, manifest discipline, evidence binding, deterministic mode, and promotion gate exist.
- A richer kernel ontology and SHACL layer already exist in `ontology/kernel.ttl` and `ontology/kernel.shacl.ttl`.

What is still incomplete:
- `SupportOntologyRelease` currently packages `ontology/support.ttl`, which is still a bootstrap placeholder.
- The richer kernel semantics are validated during Runtime 1 evaluation but are not yet the released canonical payload consumed by Runtime 2.
- CSC S1-S7 lifecycle semantics remain primarily in docs, not yet in machine-consumable support-layer artifacts.
- The ontology does not yet model the full downstream semantic surface required for Runtime 2 compile safety:
  - authority and issuance subset needed for compile-safe output typing
  - authorization and eligibility subset needed for admissibility
  - target-set, scope, action, and effect semantics
  - fail-closed denial and control-state semantics required for downstream meaning
- The constraint layer is still mostly structural SHACL, not full admissibility and fail-closed compiler gating.
- There is no approved `.ttl` admission register yet.
- Governance handling for belief, risk, and objective semantics is not yet explicitly captured as support-layer design rules.
- External ontology intake rules are not yet written down.
- `DD-001`, `DD-005`, and MVP constraint exclusion are not yet explicitly carried through support-layer design artifacts.

## Full-Layer Done Definition

The Support Ontology layer is done when all of the following are true:
- Runtime 1 releases a canonical global semantic bundle, not a placeholder file.
- Every `.ttl` file used in a binding path is listed in an approved admission register.
- Constitutional meaning remains anchored in `ontoForge_01`, `ontoForge_02`, and `ontoForge_04`, with support-layer contracts explicitly traced back to those sources.
- The release contains the machine-readable support contract required by Runtime 2.
- Governance semantics for belief, risk, and objective handling are explicitly translated into support-layer contract rules with traceability.
- External ontologies, if used, enter only through explicit approved curation rules.
- Support-layer contracts remain identifier-clean under `DD-001` and do not reintroduce unsupported MVP constraint semantics.
- Tenant workflow inputs can be validated against support-layer contracts and fail closed on invariant violations.
- Runtime 2 can compile a positive tenant fixture to a valid `SCR_TBox_Release` using only released support artifacts plus tenant input.
- Invalid tenant fixtures fail with deterministic, reason-coded, non-permissive outcomes.
- The produced tenant release records exact dependency and evidence linkage so Runtime 3 could verify the chain of truth.

## Backlog Shape

This backlog is intentionally written as review-ready decomposition, not as an active execution-plan update.

Workstream order:
1. Inventory and admit all existing `.ttl` assets under explicit approval.
2. Define how governance semantics enter the support layer without moving constitutional authority.
3. Define the provisional external ontology policy.
4. Define the identifier and MVP admissibility boundary the support layer must honor.
5. Define what the Support Ontology release actually is.
6. Encode lifecycle and invariant semantics needed by Runtime 2.
7. Define compiler-facing tenant semantic contracts.
8. Enforce those contracts with validation and evidence.
9. Prove Runtime 2 readiness with a minimal architectural proof.

## Proposed Workstreams

### SO-W0 Source Admission and Constitutional Boundary

Goal:
- Prevent unapproved `.ttl` assets, unframed governance semantics, or uncontrolled external ontologies from entering the binding support layer.

#### SO-00.1 Inventory existing `.ttl` assets
- Primary deliverable: `specs/support_ontology_ttl_inventory_v1.md`
- Inputs:
  - `ontology/*.ttl`
  - `ontology/examples/*.ttl`
  - `ontology/negative_examples/*.ttl`
- Output:
  - full inventory of existing `.ttl` files with proposed role classification
- Dependencies: none
- Validation:
  - every existing `.ttl` file in repo is listed exactly once

#### SO-00.2 Create `.ttl` admission register under user approval
- Primary deliverable: `specs/support_ontology_ttl_admission_register_v1.md`
- Inputs:
  - `specs/support_ontology_ttl_inventory_v1.md`
- Output:
  - per-file admission state such as `APPROVED`, `NOT_APPROVED`, `NON_BINDING`, or `RETIRE`
- Dependencies:
  - `SO-00.1`
- Validation:
  - no `.ttl` file is eligible for binding use without explicit user approval recorded in the register

#### SO-00.3 Define governance incorporation model for belief, risk, and objective semantics
- Primary deliverable: `specs/support_ontology_governance_incorporation_model_v1.md`
- Inputs:
  - `specs/ontoForge_01_Doctrine_v1.1.md`
  - `specs/ontoForge_02_Lifecycle-Specification_v1.1.md`
  - `specs/ontoForge_03_Product-Spec_V1.1.md`
  - `specs/ontoForge_04_Decisions-Register_v1.1.md`
- Output:
  - explicit rules for how governance content is translated into support-layer semantics and what remains non-binding
- Dependencies: none
- Validation:
  - model distinguishes governance sources from executable support contracts and forbids prose-by-default binding

#### SO-00.4 Define provisional external ontology adoption policy
- Primary deliverable: `specs/support_ontology_external_ontology_policy_v1.md`
- Inputs:
  - `specs/support_ontology_governance_incorporation_model_v1.md`
- Output:
  - approval, versioning, conflict-review, and curation rules for any external ontology candidate
- Dependencies:
  - `SO-00.3`
- Validation:
  - no external ontology can become binding without explicit approval, version pinning, and semantic conflict review

#### SO-00.5 Define identifier and MVP admissibility boundary
- Primary deliverable: `specs/support_ontology_identifier_and_mvp_boundary_v1.md`
- Inputs:
  - `specs/ontoForge_04_Decisions-Register_v1.1.md`
  - `specs/ontoForge_02_Lifecycle-Specification_v1.1.md`
- Output:
  - explicit support-layer rules for `DD-001`, `DD-003`, `DD-004`, and `DD-005` implications on identifiers, ordering-sensitive semantics, MVP constraint exclusion, and eligibility-boundary placement
- Dependencies: none
- Validation:
  - document states which semantics belong in ontology, which belong in deterministic code validators, and which remain out of scope in MVP
  - document explicitly anchors eligibility-boundary semantics to `DD-005` and prevents accidental migration of Runtime 3 operational behavior into Runtime 2 support-layer contracts

### SO-W1 Release Composition and Canonical Payload

Goal:
- Replace the placeholder Support Ontology payload with the real canonical semantic bundle Runtime 2 depends on.

#### SO-01.1 Define SupportOntologyRelease composition contract
- Primary deliverable: `specs/support_ontology_release_composition_v1.md`
- Inputs:
  - `specs/ontoForge_03_Product-Spec_V1.1.md`
  - `specs/ontoForge_02_Lifecycle-Specification_v1.1.md`
  - `specs/support_ontology_ttl_admission_register_v1.md`
  - `specs/support_ontology_identifier_and_mvp_boundary_v1.md`
  - `ontology/kernel.ttl`
  - `ontology/kernel.shacl.ttl`
  - `ontology/support.ttl`
- Output:
  - exact definition of which ontology modules, shapes, and metadata constitute the released support layer
- Dependencies:
  - `SO-00.2`
  - `SO-00.5`
- Validation:
  - review document explicitly names release members, import policy, and consumer contract

#### SO-01.2 Define namespace, import, and version policy
- Primary deliverable: `specs/support_ontology_namespace_policy_v1.md`
- Inputs:
  - `ontology/kernel.ttl`
  - `specs/support_ontology_release_composition_v1.md`
- Output:
  - namespace policy, import closure rules, version policy, and release identity rules
- Dependencies:
  - `SO-01.1`
- Validation:
  - policy forbids ambiguous imports, implicit namespace drift, and unreleased dependencies

#### SO-01.3 Align Runtime 1 payload contract to canonical semantic bundle
- Primary deliverable: `specs/support_ontology_release_payload_contract_v1.md`
- Inputs:
  - `runtime/runtime1_engine.py`
  - `specs/support_ontology_release_composition_v1.md`
  - `specs/support_ontology_namespace_policy_v1.md`
- Output:
  - exact package payload contract for `SupportOntologyRelease`
- Dependencies:
  - `SO-01.1`
  - `SO-01.2`
- Validation:
  - contract states exact payload paths, primary file rules, and evidence expectations

### SO-W2 Lifecycle and Invariant Semantics for the Support Layer

Goal:
- Translate the lifecycle and invariant material needed by Runtime 2 into machine-consumable support-layer contracts without relocating constitutional authority.

#### SO-02.1 Define CSC stage vocabulary and stage-bound support semantics
- Primary deliverable: `specs/support_ontology_csc_stage_model_v1.md`
- Inputs:
  - `specs/ontoForge_02_Lifecycle-Specification_v1.1.md`
  - `specs/ontoForge_03_Product-Spec_V1.1.md`
  - `specs/support_ontology_governance_incorporation_model_v1.md`
- Output:
  - support-layer model of CSC S1-S7 as it constrains Runtime 1 and Runtime 2
- Dependencies:
  - `SO-00.3`
- Validation:
  - every stage has explicit relevance, upstream and downstream role, and non-goals for the support layer

#### SO-02.2 Define invariant taxonomy and non-permissive outcome model
- Primary deliverable: `specs/support_ontology_invariant_model_v1.md`
- Inputs:
  - `specs/ontoForge_02_Lifecycle-Specification_v1.1.md`
  - `specs/ontoForge_04_Decisions-Register_v1.1.md`
- Output:
  - invariant classes, failure categories, and reason-code alignment for compile-time and promotion-time failures
- Dependencies: none
- Validation:
  - document covers abort, quarantine, deny, and unknown handling without permissive defaults

#### SO-02.3 Define machine-readable support contract targets
- Primary deliverable: `specs/support_ontology_machine_contract_map_v1.md`
- Inputs:
  - `specs/support_ontology_csc_stage_model_v1.md`
  - `specs/support_ontology_invariant_model_v1.md`
  - `specs/support_ontology_identifier_and_mvp_boundary_v1.md`
  - `ontology/kernel.ttl`
  - `ontology/kernel.shacl.ttl`
- Output:
  - explicit map of which lifecycle and invariant semantics must become ontology terms, SHACL rules, or code-level validators
- Dependencies:
  - `SO-02.1`
  - `SO-02.2`
  - `SO-00.5`
- Validation:
  - every mapped semantic has a declared implementation form

### SO-W3 Compiler-Relevant Semantic Vocabulary Expansion

Goal:
- Extend the ontology only as far as Runtime 2 needs for compile-safe typing, admissibility, and downstream meaning.

Non-goal:
- full Runtime 3 operational event-system design

#### SO-03.1 Define authority and issuance subset needed by Runtime 2
- Primary deliverable: `specs/support_ontology_authority_model_v1.md`
- Inputs:
  - `specs/ontoForge_02_Lifecycle-Specification_v1.1.md`
  - `specs/product_event_model_v1.md`
  - `ontology/kernel.ttl`
- Output:
  - support-layer terms for authority effect, issuance right, root-of-trust anchors, and exact-match authority semantics only where required for compile-safe output typing and admissibility
- Dependencies:
  - `SO-02.1`
- Validation:
  - model distinguishes issuance authority from execution authority and forbids implicit authority inference

#### SO-03.2 Define operation and control subset needed by Runtime 2
- Primary deliverable: `specs/support_ontology_operation_model_v1.md`
- Inputs:
  - `specs/ontoForge_02_Lifecycle-Specification_v1.1.md`
  - `specs/product_event_model_v1.md`
- Output:
  - support-layer terms for authorization, eligibility, denial, hard stop, resume, and mode semantics only to the extent needed for compile-safe output meaning
- Dependencies:
  - `SO-02.1`
  - `SO-02.2`
- Validation:
  - model states which outcomes are permissive vs non-permissive and does not expand into full Runtime 3 operational event design

#### SO-03.3 Define target-set, scope, action, and effect vocabulary
- Primary deliverable: `specs/support_ontology_target_scope_action_model_v1.md`
- Inputs:
  - `specs/ontoForge_02_Lifecycle-Specification_v1.1.md`
  - `specs/ontoForge_03_Product-Spec_V1.1.md`
  - `ontology/kernel.ttl`
- Output:
  - support-layer model for explicit target semantics, action semantics, scope boundaries, and effect typing
- Dependencies:
  - `SO-02.2`
- Validation:
  - model forbids implicit target expansion and ambiguous action or effect semantics

### SO-W4 Runtime 2 Compiler Input and Output Contracts

Goal:
- Define the semantic handshake between the support layer and the tenant compiler.

#### SO-04.1 Define minimum tenant workflow input surface for first compile
- Primary deliverable: `specs/runtime2_tenant_workflow_input_contract_v1.md`
- Inputs:
  - `specs/ontoForge_03_Product-Spec_V1.1.md`
  - `specs/support_ontology_target_scope_action_model_v1.md`
  - `specs/support_ontology_operation_model_v1.md`
  - `specs/support_ontology_identifier_and_mvp_boundary_v1.md`
- Output:
  - canonical tenant input surface for explicit actions, target sets, effect semantics, routing and domain declarations, and `ai_operable` semantics required for fail-closed first compile
- Dependencies:
  - `SO-03.2`
  - `SO-03.3`
- Validation:
  - contract explicitly states what tenant inputs are admissible and what remains forbidden

#### SO-04.2 Define compiled control primitive contract
- Primary deliverable: `specs/runtime2_compiled_control_primitives_v1.md`
- Inputs:
  - `specs/runtime2_tenant_workflow_input_contract_v1.md`
  - `specs/product_boundary_objects_v1.md`
- Output:
  - semantic contract for what Runtime 2 emits into `SCR_TBox_Release`
- Dependencies:
  - `SO-04.1`
  - `SO-01.3`
- Validation:
  - every compiler output has support-layer provenance and downstream load meaning

#### SO-04.3 Define support-to-compiler admissibility matrix
- Primary deliverable: `specs/runtime2_support_admissibility_matrix_v1.md`
- Inputs:
  - `specs/support_ontology_machine_contract_map_v1.md`
  - `specs/runtime2_tenant_workflow_input_contract_v1.md`
- Output:
  - rule matrix mapping tenant input features to support-layer admissibility checks
- Dependencies:
  - `SO-02.3`
  - `SO-04.1`
- Validation:
  - matrix yields deterministic accept and reject expectations per rule family

### SO-W5 Constraint, Validation, and Fail-Closed Gates

Goal:
- Move from structural validation to true support-layer admissibility enforcement.

#### SO-05.1 Define ontology and SHACL uplift targets
- Primary deliverable: `specs/support_ontology_validation_uplift_v1.md`
- Inputs:
  - `ontology/kernel.ttl`
  - `ontology/kernel.shacl.ttl`
  - `specs/support_ontology_machine_contract_map_v1.md`
- Output:
  - explicit backlog of ontology-term additions and SHACL additions needed for support-layer completeness
- Dependencies:
  - `SO-02.3`
- Validation:
  - every missing machine-consumable semantic has an implementation target

#### SO-05.2 Define non-SHACL validator requirements
- Primary deliverable: `specs/runtime2_semantic_gate_requirements_v1.md`
- Inputs:
  - `specs/runtime2_support_admissibility_matrix_v1.md`
  - `specs/support_ontology_invariant_model_v1.md`
  - `specs/support_ontology_identifier_and_mvp_boundary_v1.md`
- Output:
  - deterministic validator requirements for semantics that cannot be encoded safely in SHACL alone
- Dependencies:
  - `SO-04.3`
  - `SO-02.2`
  - `SO-00.5`
- Validation:
  - each required validator has explicit input, output, and fail mode

#### SO-05.3 Define reason-code and evidence output contract
- Primary deliverable: `specs/support_ontology_reasoncode_evidence_contract_v1.md`
- Inputs:
  - `specs/ontoForge_04_Decisions-Register_v1.1.md`
  - `specs/runtime2_semantic_gate_requirements_v1.md`
- Output:
  - reason-code and evidence requirements for failed and successful support and compile validation
- Dependencies:
  - `SO-05.2`
- Validation:
  - all non-permissive outcomes require deterministic reason-coded evidence

### SO-W6 Traceability, Provenance, and Evidence Semantics

Goal:
- Ensure the support layer carries enough provenance to justify downstream trust and audit.

#### SO-06.1 Define doctrinal and lifecycle traceability model
- Primary deliverable: `specs/support_ontology_traceability_model_v1.md`
- Inputs:
  - `specs/ontoForge_01_Doctrine_v1.1.md`
  - `specs/ontoForge_02_Lifecycle-Specification_v1.1.md`
  - `specs/ontoForge_03_Product-Spec_V1.1.md`
  - `specs/ontoForge_04_Decisions-Register_v1.1.md`
- Output:
  - traceability rules from support-layer semantics back to governing sources
- Dependencies: none
- Validation:
  - trace model covers terms, shapes, validators, and release evidence

#### SO-06.2 Define support release provenance and evidence ontology
- Primary deliverable: `specs/support_release_provenance_model_v1.md`
- Inputs:
  - `ontology/kernel.ttl`
  - `specs/support_ontology_release_payload_contract_v1.md`
  - `specs/support_ontology_reasoncode_evidence_contract_v1.md`
- Output:
  - provenance and evidence model for release candidate evaluation and release issuance
- Dependencies:
  - `SO-01.3`
  - `SO-05.3`
- Validation:
  - model links release evidence to exact semantic payload and exact validation outcomes

#### SO-06.3 Define downstream dependency provenance rules
- Primary deliverable: `specs/support_to_tbox_dependency_provenance_v1.md`
- Inputs:
  - `specs/runtime2_compiled_control_primitives_v1.md`
  - `specs/support_release_provenance_model_v1.md`
- Output:
  - rules for how `SCR_TBox_Release` records exact dependence on `SupportOntologyRelease`
- Dependencies:
  - `SO-04.2`
  - `SO-06.2`
- Validation:
  - dependency rules support exact replay and audit from Runtime 3 back to Runtime 1

### SO-W7 Runtime 2 Readiness Proof

Goal:
- Prove the support layer can actually serve as Runtime 2's upstream semantic contract.

#### SO-07.1 Define positive semantic fixture set
- Primary deliverable: `specs/support_ontology_positive_fixture_set_v1.md`
- Inputs:
  - `ontology/examples/`
  - `specs/runtime2_tenant_workflow_input_contract_v1.md`
- Output:
  - positive fixture catalogue for support ontology and tenant compile input
- Dependencies:
  - `SO-04.1`
- Validation:
  - fixture catalogue covers at least one valid path for each major semantic family used by first compile

#### SO-07.2 Define negative semantic fixture set
- Primary deliverable: `specs/support_ontology_negative_fixture_set_v1.md`
- Inputs:
  - `ontology/negative_examples/`
  - `specs/runtime2_support_admissibility_matrix_v1.md`
  - `specs/support_ontology_reasoncode_evidence_contract_v1.md`
- Output:
  - negative fixture catalogue covering invariant violations and forbidden defaults
- Dependencies:
  - `SO-04.3`
  - `SO-05.3`
- Validation:
  - fixture catalogue includes expected failure class and expected reason-code family

#### SO-07.3 Define minimum Runtime 2 readiness gate
- Primary deliverable: `specs/support_ontology_runtime2_readiness_gate_v1.md`
- Inputs:
  - `specs/support_ontology_positive_fixture_set_v1.md`
  - `specs/support_ontology_negative_fixture_set_v1.md`
  - `specs/support_to_tbox_dependency_provenance_v1.md`
- Output:
  - explicit gate proving the support layer is sufficient to start Runtime 2 implementation
- Dependencies:
  - `SO-07.1`
  - `SO-07.2`
- Validation:
  - positive proof: one tenant fixture compiles to a valid tenant-scoped `SCR_TBox_Release` using only released support artifacts plus tenant input
  - negative proof: one tenant fixture is rejected with deterministic reason-coded non-permissive output
  - lineage proof: produced release records exact dependency and evidence linkage so Runtime 3 load could verify the chain of truth

## Critical Gaps To Resolve First

These are the highest-value blockers:
- The released `SupportOntologyRelease` payload is not yet the real semantic bundle.
- There is no approved `.ttl` admission register yet.
- Governance handling for belief, risk, and objective semantics is not yet explicitly turned into support-layer design rules.
- `DD-001`, `DD-003`, `DD-005`, and MVP constraint exclusion are not yet explicitly carried through support-layer design artifacts.
- Lifecycle and invariant semantics needed by Runtime 2 are not yet machine-readable support-layer artifacts.
- The support ontology lacks the downstream semantic vocabulary needed for Runtime 2 compile safety.
- There is no canonical minimum tenant workflow input contract for Runtime 2.
- There is no external ontology intake policy yet.
- There is no minimum readiness gate proving Runtime 2 can rely on the support layer alone.

## Recommended Review Questions

Use these questions to review the backlog before execution:
- Do we agree that `SupportOntologyRelease` must package the real kernel contract, not just `support.ttl`?
- Which existing `.ttl` files do you already consider admissible, questionable, or provisional?
- Do we agree that constitutional meaning stays anchored in `ontoForge_01`, `ontoForge_02`, and `ontoForge_04`, while the support layer only operationalizes those meanings?
- Which CSC semantics belong in ontology and SHACL versus deterministic code-level validators?
- How far do we want the support layer to go in representing belief, risk, and objective semantics before Runtime 2 starts?
- What is the minimum tenant workflow input surface Runtime 2 must support first?
- Do we want the support layer to model only the Runtime-2-relevant subset of Runtime 3 semantics and defer the full Runtime 3 event system?
- Should external ontologies be curated into our namespace, referenced through a translation layer, or remain reference-only by default?
- What is the minimum Runtime 2 readiness proof we will accept before starting compiler implementation?

## Out Of Scope For This Backlog

Not included here:
- implementation of Runtime 2 compiler code
- implementation of the full Runtime 3 tenant runtime service
- full Runtime 3 operational event-system design beyond the subset needed for Runtime 2 compile safety
- bootstrap ledger updates, task ledger rows, or evidence rows

Those should follow only after this proposed backlog is reviewed and accepted.







