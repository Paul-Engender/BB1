# Runtime 1 Support Release Engine v1

Status: IS
Owner: paul
Plan Item: P1-013
Task: TASK-13.1
Date: 2026-03-07

## Purpose

Define the Runtime 1 service boundary for evaluating support ontology release
candidates and producing evidence-bound `SupportOntologyRelease` packages.

## Runtime 1 Boundary

Addendum anchor: `specs/product_runtime_instantiation_clarification_addendum_2026-03-07.md`

Runtime 1 is global (non-tenant) and is responsible for:
- kernel ontology + SHACL integrity checks
- release-candidate evaluation outputs
- packaging support ontology payload with evidence files

Runtime 1 must not execute customer operational workflows.

## Service Operations

1. `evaluate_release_candidate()`
- Runs parse and SHACL checks over support/kernel artifacts.
- Validates positive examples must conform.
- Validates negative examples must fail.
- Produces structured evidence object:
  - `accepted`
  - `summary` (`total_checks`, `passed`, `failed`)
  - check-level results and excerpts

2. `build_support_ontology_release(release_version, output_root)`
- Requires candidate acceptance.
- Writes evidence bundle files.
- Emits `SupportOntologyRelease` package and `release_manifest.json` via packager.
- Manifest contract: v2 boundary fields, global scope, digest-bound files.

## API Surface

`runtime/main.py` exposes Runtime 1 endpoints:
- `POST /runtime1/release-candidate/evaluate`
- `POST /runtime1/support-release/build`

## Evidence Model

Minimum evidence files packaged under `/evidence/`:
- `release_candidate_evaluation.json`
- `release_candidate_checks.jsonl`

All files in the package are hash-bound in manifest `files[]`.

## Validation Criteria

- Runtime 1 candidate evaluation must be deterministic for the same repository state.
- Built release package must include ontology payload plus evidence payload.
- Loader must verify archive integrity and per-file digests for the package.
