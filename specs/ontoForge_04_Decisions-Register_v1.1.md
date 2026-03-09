AI–Semantic Control OS Decisions Register

Version: 1.0

Status: Approved decisions register; includes archived Draft 0.6 sections

Date: 2026-03-04

Audience: Platform operators and implementation teams

# AI–Semantic Control OS Decisions Register

Version: 1.0 (DD-001…DD-007; includes archived Draft 0.6 binding sections to preserve verbatim content)

Date: 2026-03-04

Status: Approved decisions register (binding by adoption; separate from canonical CIR/CSC contracts)

## 1. Decisions register (resolved)

### DD-001 — Canonical identifier and versioning model

Status: Approved

Date: 2026-03-04

Format

- All locally minted entities MUST use UUIDv7 identifiers expressed as cid:<uuidv7>.

- Prefix binding: cid → https://example.org/id/

- Expanded canonical form: https://example.org/id/<uuidv7>

Anonymity

- Identifiers MUST be opaque and must not embed semantic meaning such as type, tenant, actor, environment, or classification.

- The timestamp component inherent in UUIDv7 is accepted.

Admission (S2)

- All locally minted Subjects and internal object references MUST match the grammar cid:<uuidv7>.

- External IRIs from approved vocabularies (rdf, rdfs, owl, prov, obo, skos, sh, etc.) are permitted as predicates or external object references and are exempt from this format check.

Versioning

- Released artifacts carry explicit artifact_version fields.

- “Latest” references are implemented using governed alias identifiers (e.g., cid:latest-support-ontology) that resolve to a specific canonical UUID artifact. Alias reassignment occurs only through explicit governed events.

Ordering

- Event folds are ordered by (1) event_time, then (2) event_id.

- If event_time values collide, records are ordered lexicographically by the UUID string in the cid: identifier.

Minimal invariants

- Canonical identifiers are immutable.

- UUID identifiers are never reused.

- Alias reassignment must occur via governed event.

- Any locally minted identifier not matching cid:<uuidv7> fails Admission.

### DD-002 — Release artifact packaging model (Support Ontology and SCR TBox)

Status: Approved

Date: 2026-03-04

Artifact identity

- artifact_id: cid:<uuidv7>

- artifact_version: SemVer string

- A new release MUST mint a new cid:<uuidv7> identifier.

Scope fields (global vs tenant-scoped)

- tenant_scope: {global | tenant}

- If tenant_scope = tenant, the manifest MUST include tenant_id (a locally minted identifier; recommended cid:<uuidv7>).

- If tenant_scope = global, tenant_id MUST be absent.

Package layout (minimum)

/manifest.json

/payload/ontology.(ttl | jsonld | rdfxml)

/payload/compiled/* (optional)

/evidence/* (required for SCR_TBox_Release loading per DD-006)

/signature.sig (optional but recommended)

manifest.json must include

- schema_version

- artifact_id

- artifact_type (SupportOntology | SCR_TBox)

- artifact_version

- released_at (RFC3339 timestamp)

- tenant_scope (global|tenant)

- tenant_id (required iff tenant_scope=tenant)

### Payload description

- primary_file

- primary_format

- compiled_present

- compiled_reproducible

### Integrity verification

- content_digest (sha256)

- file list with SHA-256 hashes for all included files (manifest, payload, compiled, and evidence)

### Dependency bindings

- dependencies list of exact bindings (dependency_artifact_id, dependency_artifact_type, dependency_artifact_version)

Payload rules

- Canonical ontology payload is the source of truth.

- Compiled/index artifacts are optional; if present they MUST be reproducible and must not introduce semantic differences.

Integrity verification

- Runtime MUST verify SHA-256 digests prior to admitting the artifact. Digest failure → inadmissible.

Signature binding

- Signature MAY be included; if present it MUST cover the manifest and therefore the payload digests.

Latest alias handling

- “Latest” MUST NOT be resolved by timestamps or version comparison.

- Governed alias identifiers resolve to specific artifact IDs; reassignment occurs via explicit governed events.

### DD-003 — Runtime event ledger and ordering model

Status: Approved

Date: 2026-03-04

SCR Runtime persists all governance-relevant events into an append-only event ledger providing atomic append, immutable history, and replayable reads sufficient for as-of recomputation.

### Partitioning

- Partitioned by deterministic scope key (at minimum: tenant_id).

- Ordering guarantees are per-partition.

### Ordering authority

- Each partition MUST have exactly one ordering authority at a time.

- Ordering authority serializes appends and assigns event_time at commit time.

### Ordering fields

- event_id: cid:<uuidv7>

- event_time: assigned by ordering authority at commit time

### Distributed constraint (MVP)

- Multi-writer distributed appends without sequencer/consensus ordering authority are not permitted.

### As-of read model

- As-of recomputation uses the ledger’s stable total order.

### DD-004 — Canonical constraint handling and reason codes

Status: Approved

Date: 2026-03-04

### Constraints (MVP stance)

- Constraints are explicitly unsupported in MVP.

- Binding canonical records MUST NOT include constraint fields.

- Constraints present during S5 issuance → ABORT.

- Constraint-like expressions at S1–S2 → QUARANTINE unless/until a future canonical constraint contract exists.

### Reason codes

- AuthorizationDecision records MUST include canonical reason_codes.

### Reason code format

RC:<Stage>:<InvariantOrRule>:<Detail>

### Rules

- ABORT/QUARANTINE/DENY MUST include at least one reason code.

- Multiple codes MAY be present.

- The first code MUST represent the primary cause consistent with the failure-disposition precedence rule.

### DD-005 — Eligibility boundary enforcement model

Status: Approved

Date: 2026-03-04

### Eligibility determination

- Eligibility is evaluated prior to execution commitment during S6.

### * The evaluation produces an EligibilityDecision record

- decision_id: cid:<uuidv7>

- subject, scope, target, action

- eligibility_result: {eligible | ineligible | unknown}

- reason_codes

- event_time

### Execution rule

- Execution commitment MUST NOT occur unless eligibility_result = eligible.

- ineligible → DENY

- unknown → DENY

### Monitoring primitives

- HardStopEvent disables execution for a defined scope/target_set/action_set until superseded.

- ResumeEvent lifts a previously issued HardStopEvent.

### MVP eligibility model

- Action primitives MUST declare ai_operable (boolean) in the SCR TBox.

- true → eligible; false → ineligible; missing → unknown (non-permissive).

### DD-006 — Three-runtime CSC instantiation and promotion discipline

Status: Approved

Date: 2026-03-04

### Decision

- The product has three engines/runtimes: Support Ontology Engine (Semantic Kernel), SCR TBox Engine (Logical Compiler), and SCR Customer Runtime.

- CSC S1–S7 is the canonical lifecycle state machine and is executed in all three engines; only the truth product and permitted side effects differ.

- Only versioned releases and explicit load manifests cross boundaries; nothing is promoted by presence, placement, naming, or prose.

- Upstream evidence prerequisite: SCR Customer Runtime MUST reject loading an SCR_TBox_Release unless the associated CompilationEvidence is present and cryptographically linked (at minimum: included under /evidence/* and covered by manifest SHA-256 digests).

### DD-007 — Global doctrine, tenanted workflows (no BYO doctrine)

Status: Approved

Date: 2026-03-04

### Decision

- Doctrine (B1–B10) and CIRs are global, platform-owned, immutable, and apply universally to all tenants.

- The Support Ontology Engine is global and produces globally versioned SupportOntologyRelease artifacts.

- Tenant customizations are limited to workflow/domain/routing and related control primitives compiled under global constraints.

- The SCR TBox Engine compiles tenant workflow definitions in a tenanted execution context; compilation fails (non-permissive) on any attempt to bypass a global belief/invariant.

- The SCR Customer Runtime is tenant-scoped and loads only tenant-scoped SCR_TBox_Release artifacts via SCR_Runtime_LoadManifest; tenant_id MUST match across the load manifest, the TBox release, and the tenant ledger partition.

## 2. Archived text (verbatim) — Product Spec Draft 0.6 Sections 5–7

This section preserves the verbatim text of Draft 0.6 Sections 5–7, which were relocated out of the directional Product Specification in Draft 0.7 to preserve a single canonical location for binding contracts.

CIRs are binding contracts bridging beliefs to enforceable obligations.

### 5.1 CIR record format (binding)

| Field | Meaning |
| --- | --- |
| invariant_id | Stable identifier (e.g., I14) |
| source_belief_id | Source belief(s) (e.g., B7) |
| enforceable_condition | Checkable condition (no rhetorical wording) |
| enforcement_points | Where it must hold (stages / execution-commitment boundary) |
| prohibited_defaults | Fields that must not be inferred by “common sense” |
| failure_disposition | What happens on failure: abort / quarantine / deny |

### 5.2 Failure disposition precedence rule (binding)

### To preserve deterministic outcomes across evaluators

- Invariant failures concerning inadmissible binding input (I6, I7, I12, I13) → QUARANTINE, unless at execution-commitment boundary, in which case DENY.

- Invariant failures concerning structural invalidity (I8, I19, I20, I22, I23) → ABORT.

- Invariant failures concerning authorization or unknown premises (I4, I10, I11, I16, I17, I14 when treated as “attempted mandate inference”) → DENY.

### 5.3 CIR set (I1–I23)

(As per current draft; unchanged content. Formatting is intentionally compact until we decide whether to normalize this into a separate appendix.)

## 6. Lifecycle state machine (CSC S1–S7) — Binding contracts

## CSC S1–S7 is the canonical lifecycle state machine. It is executed in all three engines; only the truth product and permitted side effects differ.

### 6.1 CSC record format (binding)

| Field | Meaning |
| --- | --- |
| stage_id | Stable identifier (S1…S7) |
| stage_name | Human-readable stage name |
| purpose | Commentary only (non-binding) |
| inputs | Explicit inputs required |
| preconditions | Binding preconditions |
| invariants | Binding invariants (CIR references) |
| abort_triggers | Binding abort triggers (checkable) |
| postconditions | Binding postconditions |
| outputs | Explicit outputs |
| unknowns_dependencies | Explicit UNKNOWN/DELEGATED dependencies; must not be defaulted |

### 6.2 CSC stage contracts (high-level)

CSC S1 — Origination (Descriptive Layer)

- invariants: I1, I2, I6, I12, I13, I7

CSC S2 — Admission (Point-of-Entry Governance)

- invariants: I6, I8, I19, I10, I11, I7, I22

CSC S3 — Classification (MECE Subject Taxonomy)

- invariants: I14, I6

CSC S4 — Alignment (Subject-First External Mapping)

- invariants: I10, I16, I17, I1

CSC S5 — Attribution (Evented Authority Layer)

- invariants: I5, I15, I18, I20, I6

- note: constraints present → ABORT (DD-004, MVP stance)

CSC S6 — Operation (Composition and Execution)

- invariants: I4, I3, I10, I11, I16, I17, I9, I1, I21, I23

- outputs (customer runtime): AuthorizationDecision (with reason_codes), EligibilityDecision (with reason_codes), ExecutionEvent, SideEffects

CSC S7 — Deprecation (Supersession and Tombstoning)

- invariants: I20, I18, I21

## 7. Authority derivation and TargetSets (binding)

### 7.1 Authority derivation (exact-match; default deny)

Default state: Denied.

Allowed effects: GRANT, REVOKE, DELEGATE.

Ledger partitioning (DD-003): authority is derived within a partition keyed by tenant_id at minimum. Ordering guarantees are per-partition.

### Deterministic fold ordering (DD-001, DD-003)

- Order events strictly by (event_time, event_id).

- event_id is cid:<uuidv7>.

- event_time is assigned by the ordering authority at commit time.

- If event_time values collide, ties are broken lexicographically by the UUID string in the cid: identifier.

Exact-match rule: Authority applies only when subject, scope, target, action match exactly. No implicit expansion.

### 7.2 TargetSet primitives

### TargetSet requirements

- Stable ID (cid:<uuidv7>)

- Explicit deterministic membership semantics

- Membership computed only from admitted premises as-of time T

### Deterministic “as-of T” selection

- Pick the non-superseded version with greatest (event_time, event_id); if event_time collides, compare event_id lexicographically by the UUID string in the cid: identifier.

- If multiple non-superseded versions exist → ABORT.

- If none exist → exclude from membership.

Patch Addendum — 2026-03-05 — Operational Link for Approved Decision (BR-00.1)

Purpose: Add operational implementation link for the already-approved governance decision on stable interface + retention.

This addendum does not create a new decision; it records where the approved rule is implemented.

Repository: https://github.com/Paul-Engender/BB1

Contract file: tools/repo_skeleton_paths.txt

CI workflow: .github/workflows/repo-skeleton-check.yml (repo-skeleton-check)

Evidence artifact: repo-skeleton-proof (retention-days: 30)

Implementation commits (for evidence lookup):

- 6a12f35 (contract + initial proof files)

- 83b1371 (workflow corrected to include proof + artifact upload)

- 5e7b68d (directory placeholders tracked to satisfy CI checkout semantics)

Note: Prior repo name AA1 is legacy; BB1 is the canonical repository for Phase 0 going forward.
