# Support Ontology Reason-Code Evidence Contract v1

Status: APPROVED
Owner: paul
Plan Item: P1-021
Task: TASK-21.4
Date: 2026-03-07

## Purpose

Define deterministic reason-code and evidence output requirements for Runtime 2
validation and compile outcomes.

This contract applies to both successful and non-permissive outcomes.

## Source Anchors

Primary canonical anchors:
- `specs/ontoForge_04_Decisions-Register_v1.1.md`
- `specs/ontoForge_02_Lifecycle-Specification_v1.1.md`
- `specs/product_runtime_instantiation_clarification_addendum_2026-03-07.md`

Support anchors:
- `specs/runtime2_semantic_gate_requirements_v1.md`
- `specs/support_ontology_invariant_model_v1.md`
- `specs/runtime2_support_admissibility_matrix_v1.md`

## Canonical Reason-Code Format

All non-permissive outcomes must emit reason-codes in canonical format:
- `RC:<Stage>:<InvariantOrRule>:<Detail>`

Rules:
- `Stage` must be one of `S1..S7`
- `InvariantOrRule` must be a canonical invariant id (`I#`) or approved rule id
  (`DD-004`, `DD-005`)
- `Detail` must be deterministic uppercase token

## Primary-Cause Rule

- First reason-code emitted MUST represent the primary cause.
- Secondary reason-codes MAY be appended for dependent causes.
- Secondary codes MUST NOT replace or reorder primary cause.

## Evidence Output Types

Runtime 2 validation outcomes must emit at least these evidence records:

1. `GateExecutionRecord`
- gate id, input refs, result, stage id, reason-codes

2. `CompileDecisionRecord`
- final compile decision, primary cause, dependent causes, timestamp

3. `DependencyBindingRecord`
- exact support release dependency used in decision

4. `EvidenceDigestRecord`
- hash list for all emitted evidence files

5. `CompileOutcomeSummary`
- compact pass/fail summary across all gates

## Outcome-Class Contract

### PASS

Required:
- `CompileDecisionRecord.decision = PASS`
- evidence references to successful gate records
- dependency-binding reference present

### ABORT

Required:
- non-empty reason-code list
- primary reason-code points to structural/blocking cause
- evidence contains failing gate context and deterministic detail token

### QUARANTINE

Required:
- non-empty reason-code list
- reason-code indicates inadmissible binding contamination class
- evidence includes quarantined artifact/input reference

### DENY

Required:
- non-empty reason-code list
- reason-code indicates non-permissive admissibility/evaluation refusal
- evidence includes decision context and denied surface reference

## Minimum Detail Tokens

Approved token set (initial):
- `MISSING_IDENTITY`
- `UNBOUND_REFERENCE`
- `IMPLICIT_TARGET`
- `MISSING_SCOPE`
- `MISSING_EFFECT_SEMANTICS`
- `UNKNOWN_PREMISE`
- `UNKNOWN_ELIGIBILITY`
- `UNSUPPORTED_CONSTRAINT`
- `MISSING_EVIDENCE_LINK`
- `MISSING_REASON_POLICY`

New tokens must be deterministic and documented before use.

## Evidence Integrity Rules

- Every evidence file emitted must be hash-listed in package manifest context.
- Evidence references must be identifier-clean and immutable.
- Missing or hash-invalid evidence is non-permissive (`ABORT`).

## Runtime 2 Output Mapping

Reason-code and evidence artifacts must be linkable to:
- input surface references (`TASK-20.2` contract)
- compiled primitive output references (`TASK-20.3` contract)
- admissibility matrix row/gate identity (`TASK-20.4` contract)

## Addendum Consideration

This contract governs Runtime 2 compile evidence and reason-coding only.
It does not define Runtime 3 operational event reason-code semantics.

## Acceptance Checklist (TASK-21.4)

- canonical reason-code format and primary-cause rule are explicit
- evidence record types are explicit
- per-outcome required evidence behavior is explicit
- minimum detail token policy is explicit
- evidence integrity/hash rules are explicit
- boundary non-conflation is preserved
