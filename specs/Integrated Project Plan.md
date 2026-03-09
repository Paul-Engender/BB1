Document date: 2026-03-04 Plan version: v0.3 (standalone build-readiness plan)

Project Manager: paul

Status: Design-to-Build Transition Tenancy model: Global Doctrine / Tenanted Workflows Baseline stack direction (non-prescriptive): Option B (GCP + Python + Ontology-as-Code CI)

1. Purpose and scope

This document is an implementation-plane project plan intended to carry full context for execution. It does not create, modify, or supersede any binding governance contracts. Binding meaning remains anchored to the canonical control specification and decisions register; this plan only schedules and structures implementation work required to make those contracts buildable, testable, and operable.

In scope

- Build readiness: resolve the concrete UNKNOWN/DELEGATED items that block an end-to-end vertical slice.

- MVP implementation: deliver a minimal “three-runtime” vertical slice demonstrating deterministic governance flow (S1–S6) up to execution commitment, with evidence-chain enforcement.

- Ontology-as-Code discipline: treat ontologies and control primitives as versioned code artifacts with CI validation and packaged evidence.

Out of scope (MVP)

- Constraint language support (explicitly unsupported).

- Multi-writer distributed ledgers without a sequencer/ordering authority.

- Broad feature coverage beyond the vertical slice.

1. Context summary (why this plan exists)

We are at the edge of design and build: the canonical documents define what must be true, but several implementation dependencies are explicitly UNKNOWN/DELEGATED and therefore must be concretized before we can deploy the three runtimes. This plan organizes that concretization into a readiness gate (Phase 0) and integrated workstreams, culminating in a vertical slice that proves the architecture’s core claims.

Core architectural intent to preserve operationally

- Deterministic, auditable governance and execution: AI may propose; deterministic code commits at the execution boundary.

- Promotion discipline: nothing crosses runtime boundaries by presence/placement/prose; only versioned release artifacts and explicit load manifests.

- Non-permissive handling of unknowns at execution: unknown/ineligible → DENY.

2. Glossary (minimal)

- CSC S1–S7: lifecycle stages used across the three runtimes.

- CIR I1–I23: canonical invariant set; used as binding checks.

- SupportOntologyRelease: global, versioned release artifact for the Support Ontology.

- SCR_TBox_Release: tenant-scoped, versioned release artifact for compiled tenant workflows/control primitives.

- SCR_Runtime_LoadManifest: tenant-scoped manifest declaring which SCR_TBox_Release is loaded for a runtime instance.

- Evidence chain: build/compile evidence packaged with releases and verified at load time.

- Ontology-as-Code: treating OWL/RDF artifacts as code with CI validation, version binding, and reproducible packaging.

3. Phase 0 — Build Readiness (Go/No-Go gate)

This phase must be completed and the gate passed before deploying the three runtimes.

3.1 Phase 0 objectives

- Resolve the explicit build blockers (GAP-01..GAP-06) to make the system buildable and testable.

- Produce a minimal validated release pipeline that enforces promotion discipline (no “informal” loading).

3.2 Build Readiness gate criteria (Go/No-Go)

Gate evidence pack must include:

- A buildable repository skeleton with canonical directory layout.

- Identity model defined and validated (including cid/uuid conventions as per Decisions Register).

- Evidence Ledger prototype that can record mentions/extractions/proposed triples with deterministic replay proof.

- Schema package and load/verify enforcement: releases must be rejected if tampered or malformed.

- Minimal releases produced: SupportOntologyRelease and SCR_TBox_Release (tenant).

- A minimal runtime loader that only loads via explicit manifest and verifies evidence chain.

Go decision rule (implementation-plane): Gate is “Go” only when the above evidence is produced and independently verifiable from the artifacts and logs.

4. Workstreams

4.1 Workstream A — Repository + build system

- Goal: establish a buildable repo with CI that validates schemas and ontology artifacts as code.

- Outputs:

  - Repo skeleton + CI pipeline

  - Initial schema validation jobs (SHACL/contract validation where applicable)

4.2 Workstream B — Identity + naming + addressing

- Goal: define identity model usable across ledger and releases.

- Outputs:

  - cid identifier scheme implemented (UUIDv7-based where required by decision)

  - Naming + addressing conventions for manifests, releases, and artifacts

4.3 Workstream C — Evidence Ledger prototype (deterministic)

- Goal: implement Evidence Ledger as separate from Truth Graph, with deterministic ordering and replay.

- Outputs:

  - Append-only event store with deterministic ordering

  - Replay tool that reproduces identical state/hashes

4.4 Workstream D — Packaging + release discipline

- Goal: package ontologies/control primitives as releases with evidence chain and load manifests.

- Outputs:

  - Packager for SupportOntologyRelease and SCR_TBox_Release

  - Loader/verifier that rejects invalid or tampered releases

4.5 Workstream E — Minimal three-runtime vertical slice

- Goal: demonstrate governance flow S1–S6 with deterministic enforcement boundary.

- Outputs:

  - Minimal “three-runtime” deployment that uses manifests/releases and enforces non-permissive unknown handling

5. Milestones

- M0: Phase 0 Gate passed (Go)

- M1: SupportOntologyRelease produced + load verified

- M2: SCR_TBox_Release produced + load verified

- M3: Evidence Ledger replay determinism proven

- M4: Vertical slice demo (S1–S6) with evidence chain enforcement

6. Risks and mitigations

- Risk: Ambiguity in delegated/unknown implementation requirements

- Mitigation: Convert each UNKNOWN/DELEGATED item into an explicit spec artifact with testable acceptance criteria.

- Risk: Status inflation by intent/prose

- Mitigation: Only mark DONE with reproducible artifacts + hashes/CI logs (evidence pack discipline).

7. Appendix (links and references)

- Binding governance: Canonical control spec + Decisions Register (see canonical doc set map)

- Directional design: Product spec drafts

3.3 Phase 0 Evidence Ledger (Implementation-plane)

Phase 0 gate status must be evaluated using the Phase 0 Evidence Pack v0.1 (implementation-plane evidence ledger). This plan does not claim Phase 0 DONE by intent; Phase 0 is DONE only when the Evidence Pack records DONE status for every gate criterion with reproducible evidence (artifact locator + integrity hash and/or CI run ID with immutable logs).

Outputs

- Phase 0 Evidence Pack v0.1 exists and is maintained as the single evidence ledger for Phase 0.

Validation (DONE)

- Evidence Pack contains, for every gate criterion: artifact locators (repo paths and/or URLs); integrity identifiers (hashes/tags); validation evidence (CI run IDs/log links); and a status of DONE for all criteria.

Change record

- Change type: proposal

- Document & Section affected: Integrated Project Plan v0.3 - add §3.3 Phase 0 Evidence Ledger

- Reason for change: Make Phase 0 DONE evidence-based (COMPLETED vs DONE discipline).

- Impact: execution impact

- Status: pending review

- Date: 2026-03-05
