# Product Event Model v1

Status: IS
Owner: paul
Plan Item: P1-011
Task: TASK-11.2
Date: 2026-03-06

## Purpose

Define the product-level event model for SCR Customer Runtime (Runtime 3) so
AuthorityEvents, ExecutionEvents, denials, suspension/resume controls, and mode
transitions are deterministic, tenant-scoped, and auditable.

## Canonical Source Binding

| Source | Binding Role | Event-Model Impact |
| --- | --- | --- |
| `specs/ontoForge_03_Product-Spec_V1.1.md` | Directional product architecture | Defines Runtime 3 as enforcement and operational truth; requires AuthorityEvents, ExecutionEvents, denials, suspensions, mode transitions, and as-of recomputation |
| `specs/ontoForge_02_Lifecycle-Specification_v1.1.md` | Canonical lifecycle and invariants | Defines CSC S1-S7, CIR invariants, append-only event model, authority derivation, and deterministic ordering semantics |
| `specs/ontoForge_04_Decisions-Register_v1.1.md` | Approved implementation decisions | Defines event ID grammar, per-tenant partitioning, single ordering authority, reason code format, eligibility boundary, and control events |

## Runtime 3 Event Scope

Runtime 3 persists governance-relevant outcomes only. These outcomes are the
authoritative tenant operational record.

Event families required by product contract:
- AuthorityEvents
- AuthorizationDecision events (with reason codes)
- EligibilityDecision events (with reason codes)
- ExecutionEvents
- Denial events
- HardStopEvent / ResumeEvent
- ModeTransitionEvent

## Canonical Event Envelope

Every Runtime 3 event MUST satisfy this envelope contract.

| Field | Type | Rule |
| --- | --- | --- |
| `event_id` | `cid:<uuidv7>` | Required; immutable; locally minted ID must satisfy DD-001 |
| `tenant_id` | `cid:<uuidv7>` | Required; event partition key; events are valid only inside this tenant partition |
| `event_type` | string enum | Required; one of declared event families/subtypes |
| `event_time` | RFC3339 timestamp | Assigned by ordering authority at commit time (not proposer-supplied) |
| `subject` | object | Required; explicit subject identity; no implicit expansion |
| `scope` | object | Required when relevant; explicit boundary semantics |
| `target` | object | Required when relevant; target set identity + as-of binding where applicable |
| `action` | string | Required for authorization/eligibility/execution semantics |
| `stage_id` | `S1`..`S7` | Required lifecycle anchor |
| `reason_codes` | array[string] | Required for ABORT, QUARANTINE, DENY; format `RC:<Stage>:<InvariantOrRule>:<Detail>` |
| `evidence_refs` | array[`cid:<uuidv7>`] | Optional; references upstream proof/release artifacts |
| `supersedes_event_id` | `cid:<uuidv7>` | Optional; required when event semantically supersedes an earlier event |
| `payload` | object | Event-type specific fields; must remain canonical and deterministic |

## Event Types

### 1) AuthorityEvent

Purpose: add/remove/delegate authority through explicit eventing.

Required subtype values:
- `AuthorityGrantEvent`
- `AuthorityRevokeEvent`
- `AuthorityDelegateEvent`

Minimum payload fields:
- `authority_subject_id`
- `scope_id`
- `target_set_id`
- `action_id`
- `issuer_proof_cid`
- `effect` (`GRANT` | `REVOKE` | `DELEGATE`)

Semantics:
- Authority is event-derived only; default state is deny.
- Exact-match only on `(subject, scope, target, action)`.
- No taxonomy/classification inference may imply authority.

### 2) AuthorizationDecisionEvent

Purpose: record deterministic authorization evaluation outcome at operation time.

Minimum payload fields:
- `authorization_result` (`ALLOW` | `DENY`)
- `matched_authority_event_ids` (array)
- `evaluation_as_of_event_id`

Semantics:
- Computed from admitted premises and event history only.
- `DENY` requires non-empty `reason_codes`.

### 3) EligibilityDecisionEvent

Purpose: record execution eligibility before execution commitment.

Minimum payload fields:
- `eligibility_result` (`eligible` | `ineligible` | `unknown`)
- `tbox_release_id`
- `ruleset_id`

Semantics:
- `eligible` is the only permissive outcome.
- `ineligible` and `unknown` are non-permissive and imply deny.
- Missing eligibility semantics cannot be defaulted.

### 4) ExecutionEvent

Purpose: represent execution commitment boundary crossing.

Minimum payload fields:
- `execution_result` (`committed` | `failed`)
- `authorized_decision_event_id`
- `eligibility_decision_event_id`
- `execution_commit_id`

Semantics:
- Side effects are permitted only after `ExecutionEvent` commit.
- If execution is not committed, side effects must not occur.

### 5) DenialEvent

Purpose: preserve denied operational attempts as first-class audit records.

Minimum payload fields:
- `denial_kind` (`authorization_denial` | `eligibility_denial` | `quarantine` | `abort`)
- `blocked_action_id`
- `decision_event_id`

Semantics:
- Must include `reason_codes` with primary cause first.
- Provides deterministic audit trace for non-permissive outcomes.

### 6) HardStopEvent

Purpose: operational emergency stop for explicit scope/target/action set.

Minimum payload fields:
- `hardstop_scope_id`
- `hardstop_target_set_id`
- `hardstop_action_set`
- `stop_reason`

Semantics:
- Immediately disables execution in declared boundary.
- Remains active until superseded by `ResumeEvent`.

### 7) ResumeEvent

Purpose: lift a prior hard stop.

Minimum payload fields:
- `resumes_event_id`
- `resume_scope_id`

Semantics:
- Must reference an existing active `HardStopEvent`.
- Cannot broaden scope beyond original stop boundaries.

### 8) ModeTransitionEvent

Purpose: record operational mode transitions for tenant runtime control state.

Minimum payload fields:
- `from_mode`
- `to_mode`
- `transition_reason`

Semantics:
- Transition must be explicit event, never mutable flag rewrite.
- Transition must be compatible with active HardStop/Resume state.

## Ordering and Partition Contract

Runtime 3 ordering and replay rules:
- Ledger partition key is `tenant_id` (minimum).
- Each tenant partition has exactly one ordering authority at a time.
- Ordering authority assigns `event_time` at commit.
- Stable total order is `(event_time, event_id)`.
- If `event_time` collides, `event_id` lexical order is tie-breaker.
- History is append-only; correction is superseding event, not mutation.

## As-Of Recomputation Contract

For any tenant and any event boundary `T`, runtime MUST recompute:
- active authority state
- active control-state (HardStop/Resume + mode)
- authorization and eligibility decisions
- execution/denial outcomes

using only:
- append-only event history up to `T`
- version-bound release and ruleset references

Mutable snapshots may be caches, never sole proof.

## Lifecycle Placement (CSC Alignment)

| Lifecycle Stage | Runtime 3 Event Outputs |
| --- | --- |
| S5 Attribution | AuthorityEvent |
| S6 Operation | AuthorizationDecisionEvent, EligibilityDecisionEvent, ExecutionEvent, DenialEvent |
| S7 Deprecation | ModeTransitionEvent and superseding control events |

S1-S4 remain upstream gating contexts; Runtime 3 consumes their admitted outputs but
must not re-interpret prose or infer missing canonical fields.

## Current Repo Gap Mapping

Current primitives:
- `src/ledger.py`: append-only in-memory log, no tenant partition model, no structured event envelope
- `src/evaluator.py`: stub evaluator, no canonical reason codes or eligibility model
- `src/issuer_proof.py`: structural proof checks, not integrated as product event fields

Required uplift to satisfy this model:
- introduce typed Runtime 3 event structures and validation
- enforce tenant partitioning and ordering authority semantics
- enforce authorization/eligibility/commit sequence before side effects
- persist control-state events as first-class records

## Acceptance Checklist for TASK-11.2

- Product event families are explicitly defined.
- Event envelope is deterministic and tenant-scoped.
- Ordering/as-of semantics align with DD-001/DD-003 and CIR I20/I21.
- Eligibility and execution boundary semantics align with DD-005.
- Control events align with HardStop/Resume operational model.

## Next Input

This artifact is the direct input to `TASK-11.3` (boundary object definitions)
and to Runtime 3 implementation decomposition under `P1-011`.
