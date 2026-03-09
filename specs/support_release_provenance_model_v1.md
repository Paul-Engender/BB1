# Support Release Provenance Model v1

Status: APPROVED
Owner: paul
Plan Item: P1-022
Task: TASK-22.3
Date: 2026-03-07

## Purpose

Define provenance and evidence semantics for `SupportOntologyRelease` issuance in
Runtime 1.

This model binds release identity, payload integrity, validation outcomes, and
issuance evidence for deterministic downstream trust.

## Inputs

- `specs/support_ontology_release_payload_contract_v1.md`
- `specs/support_ontology_reasoncode_evidence_contract_v1.md`
- `specs/product_boundary_objects_v1.md`
- `specs/ontoForge_03_Product-Spec_V1.1.md`
- `specs/ontoForge_04_Decisions-Register_v1.1.md`

## Provenance Record Contract

Each issued `SupportOntologyRelease` MUST include a `SupportReleaseProvenanceRecord`:

- `release_id`: CID for the packaged release
- `release_version`: semantic version identifier
- `release_time`: issuance timestamp
- `payload_members`: canonical payload file list
- `payload_hashes`: digest map for each payload member
- `primary_file`: canonical primary semantic file
- `validation_profile`: validator profile id/version used for evaluation
- `validation_results_digest`: digest of validation result bundle
- `reasoncode_digest`: digest of reason-code output bundle
- `evidence_bundle_digest`: digest for all release evidence files
- `issuer_proof_ref`: cryptographic issuer proof reference
- `promotion_decision_ref`: promotion decision record reference
- `source_traceability_refs`: references to traceability records for key semantic surfaces

## Binding Rules

1. Hash binding is mandatory.
- Payload/evidence membership and digests are mandatory; missing digests are non-permissive.

2. Exact payload identity only.
- `payload_members` and `payload_hashes` must match package manifest exactly.

3. Evaluation-to-release continuity.
- `validation_results_digest` and `reasoncode_digest` must correspond to evidence files included in package.

4. Issuance proof required.
- A release without valid `issuer_proof_ref` is not admissible for downstream use.

5. No implicit provenance completion.
- Missing provenance fields are not defaulted.

## Minimal Evidence Bundle Semantics

Minimum evidence set:
- release candidate evaluation report
- validation checks log
- reason-code output (including success/failure summaries)
- promotion decision record

Each evidence artifact must be digest-bound and linked in provenance record.

## Validation Checks

A `SupportOntologyRelease` provenance check fails if:
- any required provenance field is missing
- payload hash mismatch occurs
- evidence digest mismatch occurs
- issuer proof is absent/invalid
- source traceability references are absent for required semantic surfaces

## Runtime Boundary Note

This model is Runtime 1 issuance provenance only.
It does not define Runtime 2 compilation outputs or Runtime 3 operational events.

## Done Test

This artifact is complete only if all are true:
- every release has deterministic payload and evidence digest lineage
- evaluation outputs are linked to issuance record
- issuer proof and promotion decision linkage are explicit
- provenance model is non-conflated with Runtime 2/3 runtime semantics
