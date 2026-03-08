# Support Ontology Release Payload Contract v1

Status: APPROVED
Owner: paul
Plan Item: P1-016
Task: TASK-16.3
Date: 2026-03-07

## Purpose

Define the exact Runtime 1 packaging contract for canonical `SupportOntologyRelease` payloads, aligned to approved composition and namespace/import policy.

This contract is the implementation-facing bridge between:
- `specs/support_ontology_release_composition_v1.md` (what belongs in payload)
- `specs/support_ontology_namespace_policy_v1.md` (namespace/import discipline)
- `runtime/runtime1_engine.py` and `tools/packager.py` (how payload is produced)

## Canonical Payload Membership (Binding)

Runtime 1 canonical `SupportOntologyRelease` payload MUST include:
- `ontology/kernel.ttl`
- `ontology/kernel.shacl.ttl`

Runtime 1 canonical `SupportOntologyRelease` payload MUST NOT include:
- `ontology/support.ttl`
- `ontology/scr_tbox.ttl`
- `ontology/examples/*`
- `ontology/negative_examples/*`

## Primary File Contract

Manifest `primary_file` MUST be:
- `ontology/kernel.ttl`

`primary_file` MUST NOT be placeholder-oriented files (for example `ontology/support.ttl`).

## Evidence Payload Contract

Release package MUST include evidence files under `evidence/` role, including at minimum:
- `release_candidate_evaluation.json`
- `release_candidate_checks.jsonl`

Evidence files must be hash-bound in manifest and loader-verifiable under existing boundary controls.

## Namespace and Import Contract

Canonical payload files MUST satisfy:
- governed production namespace usage for canonical terms
- no placeholder namespace payload members (`http://example.org/*` files excluded)
- MVP import closure (no external `owl:imports` in canonical payload members unless explicit approved exception exists)

If these checks fail, Runtime 1 candidate promotion is non-permissive.

## Runtime 1 Engine Contract Updates (Implementation Intent)

### R1-P1 Payload source set

`runtime/runtime1_engine.py` build path must package canonical payload set:
- from single-file `support.ttl` payload to two-file canonical bundle (`kernel.ttl` + `kernel.shacl.ttl`)

### R1-P2 Candidate evaluation checks

Candidate evaluation must include parse/validation checks over canonical payload members as required release members.

### R1-P3 Rejection behavior

Runtime 1 must reject canonical release build if:
- required canonical payload member missing
- payload contains prohibited placeholder payload file as canonical member
- namespace/import policy violations are detected in canonical payload set

### R1-P4 Manifest expectations

Generated manifest must preserve existing boundary invariants and additionally reflect:
- canonical payload membership
- canonical primary file
- evidence completeness

## Backward Compatibility Rule

Legacy support payload mode (`ontology/support.ttl`) is non-canonical and allowed only as historical artifact handling, not as forward canonical release mode.

No implicit fallback to legacy payload is permitted in canonical mode.

## Acceptance Tests (Contract-Level)

Expected verification outcomes for runtime hardening implementation:
1. Build success when payload is exactly canonical members and policies pass.
2. Build failure when `kernel.ttl` missing.
3. Build failure when `kernel.shacl.ttl` missing.
4. Build failure when canonical payload attempts to include placeholder namespace file as primary semantic payload.
5. Build failure when canonical payload violates import-closure policy (unless approved exception metadata is present).

## Addendum Consideration

Runtime 1 payload packaging is treated as boundary-object emission only; it is not conflated with Runtime 2 candidate state or Runtime 3 operational instantiation.

## Non-Goals

Out of scope for this contract artifact:
- direct code modification of Runtime 1 engine in this task
- Runtime 2 compiler behavior implementation
- Runtime 3 runtime changes

## Review Focus

Confirm these architectural commitments before implementation tasking:
- canonical payload membership is final for current phase
- legacy placeholder payload is fully non-canonical
- namespace/import compliance should be hard-gated (not advisory) for canonical release builds

