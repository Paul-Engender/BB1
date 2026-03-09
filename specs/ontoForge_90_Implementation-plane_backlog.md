Implementation-plane backlog for ontoForge (AI-Semantic Control OS)

Document date: 2026-03-04

Backlog version: v0.1

Owner: paul

Status: Build readiness decomposition (Phase 0)-----Plane Note (Non-Binding)

This backlog decomposes implementation work required to satisfy binding governance contracts. Presence of tasks, folder names, or draft files does not imply authority or “Done.” “Done” requires evidence outputs and validation per ticket criteria.-----Status Discipline: IS vs OUGHT

- IS: what is evidenced by artifacts, logs, and verifiable outputs.

- OUGHT: planned repo paths and planned outputs are OUGHT until evidenced.

- UNKNOWN: anything not yet evidenced or contract-specified.

-----Backlog Ticket Header Requirements (Mandatory)

Each ticket must include:

- Canonical Ref(s): Decision ID(s) and/or Contract section(s) it implements (e.g., DD-00x; CIR/CSC §…).

- Evidence Pack Row(s): which Evidence Ledger row(s) this ticket contributes to.

- Evidence Output(s): concrete artifact(s) plus how they will be validated (hash/CI run).

Validation (DONE)

- A ticket cannot be marked DONE unless its Evidence Outputs are recorded as DONE in Phase 0 Evidence Pack v0.1.

-----GAPS and Work ItemsGAP-01: Repo skeleton and CI do not exist as evidenced artifactsWork item BR-00.1 — Create repo skeleton and canonical directory layout

- Canonical Ref(s): TBD

- Evidence Pack Row(s): TBD

- Evidence Output(s): TBD

- Outputs:

  - Repo initialized with canonical directory layout for docs, schemas, code, ontologies, releases

  - CI pipeline that runs baseline checks

- Constraints:

  - Repo paths described below are OUGHT until proven by repo tree listing

- Validation (DONE):

  - Commit hash exists and repo tree output is attached in evidence pack

  - CI run exists with green status for baseline pipeline

GAP-02: Identity model is undefined at implementable levelWork item BR-01.1 — Define identity model and cid identifier scheme

- Canonical Ref(s): TBD

- Evidence Pack Row(s): TBD

- Evidence Output(s): TBD

- Outputs:

  - Identity spec doc (cid rules, UUIDv7, scoping rules)

  - Reference implementation for cid generation

- Constraints:

  - Must match Decisions Register decision(s) on cid/UUIDv7 where binding

- Validation (DONE):

  - Identity spec exists and is referenced by other work items

  - Unit tests confirm deterministic cid generation and formatting

GAP-03: Evidence Ledger requirements are underspecified (ordering, determinism, replay)Work item BR-02.1 — Specify Evidence Ledger API and ordering model

- Canonical Ref(s): TBD

- Evidence Pack Row(s): TBD

- Evidence Output(s): TBD

- Outputs:

  - Evidence Ledger API spec (append, query, replay)

  - Ordering model spec aligned to Decisions Register

- Constraints:

  - Ledger must remain separate from Truth Graph

- Validation (DONE):

  - API spec exists and includes ordering + replay requirements

  - Spec includes acceptance tests for determinism and replay

Work item BR-02.2 — Implement Evidence Ledger prototype with deterministic replay

- Canonical Ref(s): TBD

- Evidence Pack Row(s): TBD

- Evidence Output(s): TBD

- Outputs:

  - Append-only event store with deterministic ordering

  - Replay tool that reproduces identical state and hashes

- Constraints:

  - Must conform to ordering model spec

- Validation (DONE):

  - Determinism test suite passes

  - Replay of same input produces identical outputs/hashes across runs

  - Evidence of test runs recorded in Evidence Pack

GAP-04: Schema contracts and validation pipeline are missingWork item BR-05.1 — Implement canonical JSON schemas for releases/manifests

- Canonical Ref(s): TBD

- Evidence Pack Row(s): TBD

- Evidence Output(s): TBD

- Outputs:

  - JSON schemas for SupportOntologyRelease, SCR_TBox_Release, LoadManifest, EvidencePack metadata

- Constraints:

  - Must match contract requirements where applicable

- Validation (DONE):

  - Schemas exist and validate sample artifacts

  - CI runs schema validation

GAP-05: Packaging/release discipline is not enforced by mechanismWork item BR-05.2 — Build packager for SupportOntologyRelease and SCR_TBox_Release

- Canonical Ref(s): TBD

- Evidence Pack Row(s): TBD

- Evidence Output(s): TBD

- Outputs:

  - Packager tool that outputs versioned release bundles

  - Release metadata includes integrity identifiers

- Constraints:

  - Must not allow informal loading of raw files into runtimes

- Validation (DONE):

  - Packager produces release artifacts reproducibly

  - Artifact hashes recorded in Evidence Pack

Work item BR-05.3 — Build loader/verifier that rejects tampered or malformed releases

- Canonical Ref(s): TBD

- Evidence Pack Row(s): TBD

- Evidence Output(s): TBD

- Outputs:

  - Loader that only loads via explicit manifest

  - Verifier that checks integrity identifiers and required evidence chain

- Constraints:

  - Fail closed: unknown/ineligible/tampered → reject

- Validation (DONE):

  - Negative tests demonstrate tamper → reject

  - Logs and CI outputs recorded in Evidence Pack

GAP-06: Minimal releases and vertical slice are not producedWork item BR-06.1 — Produce minimal SupportOntologyRelease

- Canonical Ref(s): TBD

- Evidence Pack Row(s): TBD

- Evidence Output(s): TBD

- Outputs:

  - SupportOntologyRelease artifact (versioned)

  - Install/load verification output

- Constraints:

  - Must be loadable only via manifest and verifier

- Validation (DONE):

  - Artifact exists with hash/tag

  - Loader verifies and loads successfully; evidence recorded

Work item BR-06.2 — Produce minimal SCR_TBox_Release (tenant) and LoadManifest

- Canonical Ref(s): TBD

- Evidence Pack Row(s): TBD

- Evidence Output(s): TBD

- Outputs:

  - Tenant SCR_TBox_Release artifact

  - SCR_Runtime_LoadManifest that declares loaded release

- Constraints:

  - Must conform to schemas and promotion discipline

- Validation (DONE):

  - Artifact exists with hash/tag

  - Loader verifies and loads successfully; evidence recorded

Phase 0 Gate VerificationWork item BR-07.1 — Run Phase 0 gate verification and compile Evidence Pack

- Canonical Ref(s): TBD

- Evidence Pack Row(s): TBD

- Evidence Output(s): TBD

- Outputs:

  - Phase 0 Evidence Pack v0.1 completed with all gate rows DONE

- Constraints:

  - Evidence Pack is the single source of truth for Phase 0 DONE

- Validation (DONE):

  - All gate criteria entries are DONE with reproducible artifact locators and hashes/CI logs

-----Change Record

| Change type | Document & Section affected | Reason for change | Impact | Status | Date |
| --- | --- | --- | --- | --- | --- |
| proposal | Phase 0 Build-Readiness Backlog v0.1 - add ticket header requirements + per-ticket fields | Enforce traceability to canonical decisions/contracts and evidence-based DONE. | execution impact | pending review | 2026-03-05 |
