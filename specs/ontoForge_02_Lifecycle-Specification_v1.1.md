AI–Ontological Governance & Lifecycle Specification

Version: 1.1-r (Refactored to Canonical Contracts)

Status: Canonical Contracts (binding)

Date: 2026-03-04

Audience: Human Operators (Audit/Architecture) & Inference-Heavy AI Agents (Behavioral Contract)

# 0. Document intent and binding boundary

This document establishes governance-plane constraints for a governed system. It is a constitutional boundary for both human operators and inference-heavy AI agents.

## 0.1 Implementation-agnostic grounding

This document is implementation-agnostic. Any specific schema, cryptographic mechanism, network protocol, storage engine, or vendor tooling is treated as UNKNOWN or DELEGATED.

## 0.2 Binding boundary rule (Belief 3 enforcement)

### This document contains two kinds of content

- Non-binding commentary: explanatory prose intended for human understanding.

- Binding contracts: canonical records that are permitted to influence admission decisions, authority derivation, policy evaluation, or execution commitment.

Only binding contracts expressed in Canonical Form are admissible as binding inputs. Prose is non-binding unless it is represented as a canonical record. If a statement cannot be represented as a canonical record without defaults, it is inadmissible as a binding contract and must be quarantined as non-binding commentary.

## 0.3 Canonical Forms used in this document

### This refactor uses two canonical forms

- A) Canonical Invariant Record (CIR) — bridges beliefs to enforceable obligations.

- B) Canonical Stage Contract (CSC) — defines the lifecycle as a formal state machine using Design-by-Contract fields.

## 0.4 Doctrine separation and traceability

The constitutional doctrine (Beliefs B1–B10) is defined in the companion doctrine artifact “Laws & Beliefs — Patched Core Beliefs And Governance Framework.”

That document defines doctrine only and is non-operational by design.

This specification operationalizes those beliefs by translating them into executable canonical contracts (CIR and CSC records). Doctrine constrains this specification but is not directly executable input for evaluators.

## 0.5 Belief traceability rule (binding)

Every binding CIR or CSC record MUST declare its source belief identifier(s) (B#) as traceability anchors. No binding governance contract exists without an explicit doctrinal source.

________________

# PART A — Constitutional Beliefs (Non-operational doctrine)

Beliefs are stable doctrine. They take precedence.

B1 Representation Non-Entailment: Descriptions, labels, placement, structure, and metadata are inert; they do not imply truth, authority, approval, eligibility, or execution.

B2 Authority is Evented: Authority exists only as explicitly recorded authority-events anchored to a non-self-originating root-of-trust. Root-of-trust mechanism is UNKNOWN/DELEGATED.

B3 Interpretability as an Invariant: Binding governance meaning is inadmissible unless it compiles to a canonical, checkable form with explicit fields and no defaults.

B4 Determinacy Enables Composition: Only primitives with crisp identity conditions and explicit boundaries may act as building blocks.

B5 Closed World / Epistemic Closure: The system’s reality is bounded by admitted premises. Unmodeled claims remain unknown; unknown does not become permissive by default.

B6 Descriptive Hygiene / Naked Truth: Descriptive surfaces (ontology definitions/labels/notes) do not contain teleology, deontic language, evaluative claims without criteria, or optimization targets.

B7 Orthogonality / Severed Destinies: Classification never entails mandate; binding between identity/classification and mandate occurs only via explicit joins/events.

B8 Operational Closure / Bounded Strike: Governance and execution act only on explicitly identified, scoped target sets.

B9 True Form / Form-to-Kind Alignment: Types describe sets; relations describe edges; events describe transitions. Governance-relevant change is represented as an event, not a mutable flag.

B10 Immutability / Append-Only Reality: Truth is historical. Change is additive; correction is a superseding event.

________________

# PART B — Bridge Layer: Canonical Invariant Records (CIR)

CIRs are binding contracts that operationalize beliefs as enforceable conditions. They are the only admissible “invariant inputs” for governance decisions.

## CIR record format (binding)

Field

Meaning

invariant_id

Stable identifier (e.g., I14)

source_belief_id

Source belief (e.g., B7)

enforceable_condition

Checkable condition (no rhetorical wording)

enforcement_points

Where it must hold (stages / execution-commitment boundary)

prohibited_defaults

Fields that must not be inferred by “common sense”

failure_disposition

What happens on failure: abort / quarantine / deny

Failure disposition precedence rule (binding)

### To preserve deterministic outcomes across evaluators

- Invariant failures concerning inadmissible binding input (I6, I7, I12, I13) → QUARANTINE, unless at execution-commitment boundary, in which case DENY.

- Invariant failures concerning structural invalidity (I8, I19, I20, I22, I23) → ABORT.

- Invariant failures concerning authorization or unknown premises (I4, I10, I11, I16, I17) → DENY.

## CIR set (I1–I23)

Invariant

Source

Enforceable condition

Enforcement points

Failure disposition

I1

B1

Rename/move/tag/format changes do not alter authority, admissibility, eligibility, or execution outcomes.

Stages 1–6; Execution commitment

abort

I2

B1

Observation/read/index/ingest operations do not commit state changes or side effects.

Stages 1–6; Execution commitment

abort

I3

B2

Authority state at time T is a deterministic function of authority-events up to T under explicit ordering/conflict rules.

Stages 5–6; Execution commitment

abort

I4

B2

No execution commitment occurs without required authority satisfied by event-derived authority at evaluation time.

Stage 6; Execution commitment

deny

I5

B2

Authority-event validity is attributable through an issuance chain anchored to a non-self-originating root of trust.

Stage 5

abort

I6

B3

Binding governance statements compile to canonical forms (CIR/CSC) without defaults.

All stages; policy evaluation

quarantine

I7

B3

Binding references resolve to modeled identifiers and versions; deictics are absent from binding inputs.

Stages 1–2; policy evaluation

abort

I8

B4

Primitives have explicit identity conditions and boundaries.

Stage 2

abort

I9

B4

Composition rules are explicit and checkable; no implicit coercions/defaults/merges.

Stage 6

abort

I10

B5

Only admitted premises influence decisions; unadmitted claims remain unknown.

Stages 2, 4, 6

deny

I11

B5

Missing facts yield unknown/non-permissive outcomes; no permissive defaults.

Stages 2, 6

deny

I12

B6

Descriptive surfaces do not restate or enforce policy; deontic/teleological/evaluative/optimization language is inadmissible in descriptive surfaces.

Stages 1–2

quarantine

I13

B6

Normativity is quarantined into governance constructs; descriptive surfaces may reference policy IDs but do not restate rules.

Stages 1–2

quarantine

I14

B7

Classification/taxonomy does not entail mandate/authority/eligibility.

Stages 3, 6

deny

I15

B7

Identity-to-mandate bindings require explicit join constructs/events naming subject, scope, effect.

Stage 5

abort

I16

B8

Rules/mandates explicitly name target sets and scope boundaries.

Stages 4, 6

abort

I17

B8

No implicit target expansion through similarity/proximity/default inheritance.

Stages 4, 6

deny

I18

B9

Governance-relevant state change is represented as an event, not a mutable flag.

Stages 5, 7

abort

I19

B9

Form matches kind (type/relation/event); no overloading across kinds.

Stage 2

abort

I20

B10

Event history is append-only; no update/delete of historical records.

Stage 7

abort

I21

B10

As-of recomputation is possible from event history and version bindings without relying on mutable snapshots as sole proof.

Stages 6–7; audit

abort

I22

B10

AdmittedPrimitive records are append-only and versioned; updates create new versions with explicit supersession.

Stage 2

abort

I23

B4/B8

Executable Action primitives must declare explicit target semantics and effect semantics; actions lacking explicit semantics are inadmissible for execution.

Stages 2, 6

abort (S2) / deny (S6)

________________

# PART C — Lifecycle as Canonical Stage Contracts (CSC)

The lifecycle is a formal state machine. Each stage is defined by a CSC record. CSCs are binding contracts.

## CSC record format (binding)

Field

Meaning

stage_id

Stable identifier (S1…S7)

stage_name

Human-readable stage name

purpose

Commentary only (non-binding)

inputs

Explicit inputs required

preconditions

Binding preconditions

invariants

Binding invariants (CIR references)

abort_triggers

Binding abort triggers (checkable)

postconditions

Binding postconditions

outputs

Explicit outputs

unknowns_dependencies

Explicit UNKNOWN/DELEGATED dependencies; must not be defaulted

CSC S1 — Origination (Descriptive Layer)

Field

Value

stage_id

S1

stage_name

Origination (Descriptive Layer)

purpose

Capture inputs without normative force; enforce interpretability and descriptive hygiene.

inputs

raw payload; ingestion vector

preconditions

raw payload exists; ingestion vector exists

invariants

I1, I2, I6, I12, I13, I7

abort_triggers

Any binding decision would require UNKNOWN/DELEGATED defaults (I6); binding references cannot be version-bound or contain deictics (I7); normative fragments cannot be quarantined or stripped without inference/default completion (I6, I12)

postconditions

Output is non-binding commentary unless and until compiled into canonical records

outputs

sanitized payload

unknowns_dependencies

ingestion transport layer: UNKNOWN; lexical filtering algorithm: DELEGATED (non-binding unless compiled)

S1 Stage Data Contract (binding where referenced)

Input object: RawPayload

- payload_id (temporary, non-authoritative)

- content_blob (opaque)

- declared_format (if any)

- arrival_metadata (transport-level; non-authoritative by rule I1)

Transformation constraints

- Any lexical filtering or normalization is non-binding unless its result is compiled into a canonical record (I6).

- Transport metadata cannot be promoted to identity, authority, scope, or target set (I1, I10).

Output object: SanitizedPayload

- candidate_content (descriptive only)

- extracted_references (unbound until version-resolved)

- detected_normative_fragments (if any; flagged)

- governance_weight = none

Commit boundary definition (S1)

No ledger append. No authority derivation. No state mutation outside temporary processing buffers (I2). If any binding inference would be required, processing halts and the payload is quarantined as commentary (I6).

## CSC S2 — Admission (Point-of-Entry Governance)

Field

Value

stage_id

S2

stage_name

Admission (Point-of-Entry Governance)

purpose

Hard gate between description and governed primitive.

inputs

sanitized payload

preconditions

sanitized payload exists

invariants

I6, I8, I19, I10, I11, I7

abort_triggers

identity/boundaries missing (I8); kind/form not determinable without defaults (I19); referenced dependencies not admitted (I10)

postconditions

admitted primitive exists with explicit identity, boundaries, kind; holds no operational authority (B2/B7)

outputs

admitted primitive

unknowns_dependencies

ID assignment protocol: UNKNOWN (if required for admission, admission aborts per I6)

S2 Stage Data Contract (binding)

Input object: SanitizedPayload

- candidate_content, extracted_references, detected_normative_fragments

Admissibility checks (must compile; no defaults)

- Identity condition: explicit identity boundaries; if identity requires hashing/ID generation and mechanism is UNKNOWN → abort (I6, I8).

- Kind determination: exactly one of Type (set), Relation (edge), Event (transition); no contextual guessing (I19, I6).

- Boundary declaration: scope/boundary explicit; missing boundaries → abort (I8).

- Reference closure: all referenced entities already admitted; no implicit external lookups (I10).

Output object: AdmittedPrimitive

- primitive_id, primitive_kind, identity_conditions, boundary_conditions, version_identifier

- governance_weight = structural_only

Commit boundary definition (S2)

Admission results in append-only structural registration (not authority event). No execution rights are altered. No mandate is inferred.

## CSC S3 — Classification (MECE Subject Taxonomy)

Field

Value

stage_id

S3

stage_name

Classification (MECE Subject Taxonomy)

purpose

Organize admitted primitives without implying mandate.

inputs

admitted primitive

preconditions

admitted primitive exists

invariants

I14, I6

abort_triggers

classification implies mandate/authority (I14); taxonomy mapping requires defaults beyond declared scope (I6)

postconditions

classified primitive exists; classification_state ∈ {Classified, Unknown/Unclassified}

outputs

classified primitive

unknowns_dependencies

business taxonomy: UNKNOWN

CSC S4 — Alignment (Subject-First External Mapping)

Field

Value

stage_id

S4

stage_name

Alignment (Subject-First External Mapping)

purpose

Map external artifacts to kinds without laundering meaning.

inputs

classified primitive; external metadata

preconditions

classified primitive exists

invariants

I10, I16, I17, I1

abort_triggers

external delivery context used as premise for validity/authority (I10); implicit target expansion (I17)

postconditions

aligned primitive exists; external context is not treated as admission/authority evidence

outputs

aligned primitive

unknowns_dependencies

host environment metadata schema: UNKNOWN

CSC S5 — Attribution (Evented Authority Layer)

Field

Value

stage_id

S5

stage_name

Attribution (Evented Authority Layer)

purpose

Only stage where binding authority is generated.

inputs

aligned primitive; authority-event proposal; issuer proof

preconditions

aligned primitive exists; authority-event proposal exists

invariants

I5, I15, I18, I20, I6

abort_triggers

issuer proof cannot trace to root-of-trust without defaults (I5/I6); authority change represented as mutable status flag (I18); subject/scope/effect not explicit (I15)

postconditions

authority event appended (event form; append-only)

outputs

authority event

unknowns_dependencies

signature verification algorithm: DELEGATED; ledger storage tech: UNKNOWN

S5 Stage Data Contract (binding)

Input object: AuthorityEventProposal

- proposed_event_kind (AuthorityEvent)

- issuer_identifier

- subject_identifier

- scope

- target

- action

- effect (GRANT | REVOKE | DELEGATE)

- issuance_rights

- effective_time

- justification_reference

Input object: IssuerProof

- proof_material, proof_type, proof_context

Admissibility checks (must compile; no defaults)

- Explicit triplet completeness: issuer, subject, scope/target_set, effect all present → else abort (I15, I6).

- Root-of-trust traceability: IssuerProof must verify deterministically → else abort (I5, I6).

- Event-only authority: no mutable fields (I18).

- Constraints disallowed: AuthorityEvent proposals must not include constraints in v1.1-r → if present abort (I6).

Output object: AuthorityEvent (append-only)

- event_id, event_kind, issuer_identifier, subject_identifier

- target_scope, target_set

- effect

- constraints (absent in v1.1-r)

- effective_time, event_time

- proof_binding, version_binding

Commit boundary definition (S5)

Commit is the append of AuthorityEvent to the immutable event history. No downstream execution occurs by presence alone (I4).

## CSC S6 — Operation (Composition and Execution)

Field

Value

stage_id

S6

stage_name

Operation (Composition and Execution)

purpose

Deterministic execution-commitment boundary. AI may propose; code commits.

inputs

execution proposal

preconditions

execution proposal exists

invariants

I4, I3, I10, I11, I16, I17, I9, I1, I21

abort_triggers

authority cannot be recomputed deterministically (I3); required premise unadmitted/unknown would be defaulted permissively (I10/I11); target set/scope implicit (I16)

postconditions

if authorized, commit occurs as an event (not mutable flags)

outputs

execution event; side effects

unknowns_dependencies

evaluation runtime engine: DELEGATED

S6 Stage Data Contract (binding)

Input object: ExecutionProposal

- proposer_identifier

- requested_action

- target

- authorization_target

- required_premises

- requested_effect

- proposed_execution_time

Binding rules

- Authorize only against authorization_target (exact match). No inferring TargetSet (I16, I17).

- If requested_action lacks explicit semantics, proposal is denied (I23).

Evaluation contract (deterministic; no side effects)

- Premise isolation: only admitted premises; metadata/taxonomy excluded as authority evidence (I10, I1).

- Temporal authority recomputation: compute strictly from AuthorityEvents as-of time T (I3, I21).

- Scope/target determinacy: target_scope and target_set explicit; no similarity/proximity expansion (I16, I17).

- Composition check: composition rules explicit; no merges/coercions (I9).

- Non-permissive unknown handling: any unknown premise → deny (I11).

Output objects

- AuthorizationDecision (binding): decision (authorize | deny | abort), decision_time, derived_authority_proof, premise_set_used, reason_codes.

- ExecutionEvent (append-only): event_kind, issuer_identifier, request_reference, targets, effect, execution_time.

- SideEffects: occur only after ExecutionEvent append.

Commit boundary definition (S6)

The execution-commitment boundary is the append of ExecutionEvent to history. The committing actor is deterministic code.

## CSC S7 — Deprecation (Supersession and Tombstoning)

Field

Value

stage_id

S7

stage_name

Deprecation (Supersession and Tombstoning)

purpose

End-of-life without rewriting history.

inputs

deprecation proposal

preconditions

deprecation proposal exists; authority event authorizing deprecation exists

invariants

I20, I18, I21

abort_triggers

any update/delete against historical records (I20); deprecation represented as mutable flag rather than event (I18)

postconditions

tombstone/supersession event appended; operational filtering excludes target from forward execution

outputs

tombstone event

unknowns_dependencies

view routing implementation: UNKNOWN

________________

# PART D — Governance Risk Matrix (binding triggers)

Risk triggers are binding only when represented as canonical records. The matrix below is commentary unless compiled.

- R1 Surface inference: deriving authority from labels/titles/locations rather than events.

- R2 Behavioral implication: treating representational language as execution trigger.

- R3 Teleology smuggling: deontic/teleological/optimization language appears in descriptive surfaces.

- R4 Interpretability failure: admitting primitives that require contextual guessing.

- R5 Underdetermined primitive: missing boundaries or identity.

- R6 Unmodeled injection: using unadmitted premises.

- R7 Cross-surface laundering: bypassing rejection by pointing to external presence.

- R8 Scope collapse: expanding mandates to similar targets.

- R9 Axis conflation: taxonomy implies permission.

- R10 Circular authority: authority event fails trace to root-of-trust.

- R11 Stochastic-to-commit leak: AI directly triggers execution without deterministic commit boundary.

- R12 History rewrite: delete/overwrite to fix errors.

- R13 State-as-attribute: mutable governance flags.

- R14 Snapshot dependence: cached state substitutes for recomputation from event log.

________________

# PART E — Authority Derivation Model (Deterministic, Exact-Match)

This section defines how authority is computed from AuthorityEvents. It is binding governance-plane logic.

- E1 Default State: For any tuple (Subject, Scope, Target, Action): Default state = Denied. No implicit permissions.

- E2 Admissible Authority Event Effects: GRANT, REVOKE, DELEGATE. Higher-level constructs (MODIFY) must compile to these first.

- E3 Deterministic Ordering Rule: strictly by (event_time, event_id).

- E4 Exact-Match Application Rule: Applies only when all match exactly: subject, scope, target, action. No taxonomy-based expansion (I16, I17).

- E5 Fold Algorithm (Authority State Derivation): Select all AuthorityEvents where event_time ≤ T. Order per E3. Initialize to Denied. Process events: GRANT → Allowed; REVOKE → Denied. Later events override earlier ones.

- E6 Delegation and Issuance Validity: Delegation grants issuance authority (ISSUE_GRANT, ISSUE_REVOKE, ISSUE_DELEGATE), not execution authority. Issuer must possess the corresponding issuance right for an event to be valid (I5, I15).

- E7 Execution Authorization Rule (Stage 6 Binding): Recompute via Fold Algorithm. If Allowed → authorize; otherwise → deny.

- E8 Genesis Seeding: Initial authority must be seeded by explicit events anchored to root-of-trust.

________________

# PART F — Target Set Library (Explicit, Admitted Primitives)

TargetSet primitives reduce per-object event volume while preserving Exact-Match authority.

- F1 TargetSet primitive requirements (binding): Stable ID, explicit/checkable membership semantics, deterministic evaluation, no similarity/fuzzy matching.

F2 TargetSet instances

- F2.1 SET:AllCases: Membership: includes exactly Case identifiers admitted in Scope CaseMgmt.

- F2.2 SET:CasesByTeam(Team_ID): Membership: includes Case_ID iff REL:CaseAssignedToTeam(Case_ID, Team_ID) holds at T.

- F2.3 SET:CasesByAccountManager(AccountManager_ID): Membership: includes Case_ID iff REL:CaseAssignedToAccountManager(Case_ID, AM_ID) holds at T.

- F3 Operational constraint: target must be exactly one of: a specific Case_ID, or a TargetSet_ID. Evaluators treat membership as deterministic.

F4 Required Relation Primitives (binding)

- F4.1 Relation: CaseAssignedToTeam

- Domain: Case_ID; Range: Team_ID.

- Changes are new versions with explicit supersession (I22).

- If multiple non-superseded versions exist → ABORT.

- F4.2 Relation: CaseAssignedToAccountManager

- Domain: Case_ID; Range: Principal_ID.

- Rules identical to F4.1.
