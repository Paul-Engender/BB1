# Spec Migration Delta Register v1

Status: IS
Owner: paul
Plan Item: P1-009
Task: TASK-09.2
Date: 2026-03-06

## Purpose

Capture concrete deltas between source backlog contracts and the current execution control system.
This register is the authoritative input to TASK-09.3 (validation matrix) and TASK-09.4 (pilot migration report).

## Sources Compared

- `specs/ontoForge_90_Implementation-plane_backlog.md`
- `specs/ontoForge_91_Build-Readiness Backlog v0.1.md`
- `specs/ontoForge_92_Evidence-Pack_v01.md`
- Active controls in `bootstrap/` (`task_ledger.csv`, `artifact_registry.csv`, `evidence_register.csv`, validator/snapshot tooling)

## Delta Taxonomy

- `ID-MAPPING`: identifier model differences between source and active execution.
- `CONTROL-HARDENING`: enforcement added in tooling that source docs did not operationalize.
- `EVIDENCE-BINDING`: evidence/hash traceability upgrades.
- `GATE-SCOPING`: gate semantics clarified to prevent cross-phase contamination.

## Delta Register

| Delta ID | Source Reference | Current State | Delta Type | Impact | Required Action | Target Task |
| --- | --- | --- | --- | --- | --- | --- |
| D-001 | BR work item IDs in OF-90/OF-91 | Active execution uses `TASK-*` and `BPL-*` with explicit alignment map | ID-MAPPING | Medium | Preserve BR-to-TASK/BPL mapping as a required migration artifact in every future backlog import | TASK-09.3 |
| D-002 | OF-90 has `Canonical Ref(s): TBD` and `Evidence Pack Row(s): TBD` in multiple items | Active ledger requires populated evidence links and plan mapping for all `TASK-*` rows | EVIDENCE-BINDING | High | Enforce non-empty canonical refs/evidence linkage for migrated tasks prior to `DONE` eligibility | TASK-09.3 |
| D-003 | OF-91 describes `IS vs OUGHT` as process guidance | Validator now enforces `DONE` invariants and rejects OUGHT-marked done state | CONTROL-HARDENING | High | Add machine-check rules to matrix for IS/OUGHT compliance at task closeout | TASK-09.3 |
| D-004 | Source docs define validation intent but not executable command standard | Active `DONE TASK-*` rows require executable `validation_method` commands and can be run in strict mode | CONTROL-HARDENING | High | Keep strict command execution as mandatory migration acceptance criterion | TASK-09.3 |
| D-005 | Source decomposition allows mixed implementation phrasing (`X and Y`) | Active validator fails mixed-intent task naming and limits dependencies/output cardinality | CONTROL-HARDENING | Medium | Include decomposition lint checks in contract validation matrix | TASK-09.3 |
| D-006 | Evidence gate in source backlog is Phase-0-centric | Active system introduced `EP-09` for next phase; phase-0 closure now scoped to `EP-01..EP-05` | GATE-SCOPING | High | Maintain scoped gate evaluation rules per phase to avoid false gate reopen | TASK-09.3 |
| D-007 | Source docs do not define deterministic artifact hash recording per task row | Active artifact registry stores SHA256 for produced artifacts and validates hash fidelity | EVIDENCE-BINDING | High | Require hash-bound artifact entry for every `DONE` task in migrated plans | TASK-09.3 |
| D-008 | OF-92 evidence structure is static and phase-specific | Active evidence register supports extending rows (`EP-09`) while preserving phase closure semantics | GATE-SCOPING | Medium | Introduce phase-tagged evidence policy in pilot migration report | TASK-09.4 |

## Decision Notes

1. No source governance authority was altered; only execution-plane controls were hardened.
2. Deltas above represent operationalization gaps, not doctrine conflicts.
3. Pilot migration must prove these deltas are reproducible without manual interpretation.

## Hand-off to TASK-09.3

Inputs provided:
- This delta register.
- Canonical baseline file `specs/spec_upgrade/canonical_spec_set_v1.md`.

Expected output from TASK-09.3:
- `specs/spec_upgrade/spec_contract_validation_matrix_v1.md` mapping each delta/action to a concrete validation command and evidence artifact.
