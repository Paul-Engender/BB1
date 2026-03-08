# Runtime 1 Support Release Engine v2

Status: APPROVED
Owner: paul
Plan Item: P2-002
Task: TASK-28.1
Date: 2026-03-08

## Purpose

Translate the retained Runtime 1 baseline into the narrow successor closure
contract for P2.

This document is not a semantic redesign of Runtime 1. It defines the successor
closure criteria needed to treat Runtime 1 as release-stable for the first
three-runtime solution slice.

## Retained Baseline

This successor contract retains the approved baseline from:
- `specs/runtime1_support_release_engine_v1.md`
- `specs/support_ontology_release_payload_contract_v1.md`
- `specs/support_ontology_namespace_policy_v1.md`
- `specs/runtime1_hardening_addendum_v1.md`
- `specs/p2_contract_delta_register_v1.md`

The retained baseline remains active unless this successor surface states an
explicit additional closure criterion.

## Successor Delta Judgment

`P2-D02` does not justify reopening Runtime 1 semantics.

The required successor delta is narrower:
- translate the retained Runtime 1 baseline into explicit release-stable closure
  criteria for downstream Runtime 2 and Runtime 3 dependence
- prove whether the current hardened Runtime 1 already satisfies those criteria
- record any residual implementation delta explicitly rather than assuming a new
  rewrite lane

## Runtime 1 Successor Closure Criteria

### 1) Global-only scope remains fixed

Runtime 1 remains global-only.

Rules:
- `SupportOntologyRelease` MUST remain `tenant_scope = global`
- Runtime 1 MUST NOT mint tenant-scoped release artifacts
- Runtime 1 MUST NOT absorb Runtime 2 or Runtime 3 operational semantics

### 2) Canonical support payload remains fixed

Rules:
- Runtime 1 release output MUST remain bound to the canonical support payload
- Runtime 1 MUST NOT reopen support-ontology membership scope under P2 without
  explicit approved change control
- Runtime 1 output MUST remain dependency-safe for downstream release binding

### 3) Deterministic evaluation and packaging remain mandatory

Rules:
- candidate evaluation MUST remain deterministic for the same repo state
- package emission MUST remain digest-bound and evidence-bound
- deterministic build mode MUST remain available for release comparison and
  downstream reproducibility proof

### 4) Downstream-loadable proof becomes a successor closure requirement

Rules:
- Runtime 1 must be shown to emit a package that remains admissible to the
  downstream loader under current boundary discipline
- successor closure requires proof that the current Runtime 1 output is suitable
  for exact downstream dependency use in the P2 chain

### 5) Residual delta handling is explicit

Rules:
- if the current Runtime 1 implementation already satisfies successor closure,
  P2-002 may close without further code change
- if a residual gap remains, it must be recorded as a narrow implementation
  delta, not inferred as a blanket Runtime 1 rewrite

## Follow-on Task Set

- `TASK-28.2` verify Runtime 1 successor release-stable criteria against the
  current hardened implementation
- `TASK-28.3` publish Runtime 1 productization closure note for `EP-28`

## Acceptance Checklist (TASK-28.1)

- retained Runtime 1 baseline is explicitly named
- successor closure criteria are explicit
- downstream-loadable proof is explicit
- no Runtime 1 semantic rewrite is implied
- follow-on closure tasks are explicit
