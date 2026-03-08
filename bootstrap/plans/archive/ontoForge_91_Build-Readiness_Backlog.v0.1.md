# Phase 0 Build-Readiness Backlog v0.1 (Blocking Gaps)

Source: `specs/ontoForge_91_Build-Readiness Backlog v0.1.md`
Conversion: docx -> markdown (text extraction)

This backlog decomposes GAP-01…GAP-06 into agent-executable work items.
- IS vs OUGHT note
- Any referenced repo path is OUGHT unless verified by evidence (repo tree listing / commit / CI check). If OUGHT, add a bootstrap dependency that creates it.
## GAP-00 Repo skeleton (paths)

## ### Work item BR-00.1 - Task Create repository skeleton folders for specs, schemas, fixtures, tools, src, and tests.
- Context Work items reference target paths (e.g., /docs/specs). Those paths are OUGHT until created and evidenced.
- Inputs None.
- Outputs OUGHT targets: - /docs/specs/ - /schemas/ - /fixtures/ - /tools/ - /src/ - /tests/
- Constraints - Do not claim paths exist (IS) until evidenced.
## Validation (DONE) - Repo tree listing or CI check proves each directory exists (e.g., test -d docs/specs etc.).

- Dependencies None.
- Non-goals - Full repo scaffolding beyond these folders.
## GAP-01 Identity & minting (cid:)

## ### Work item BR-01.1 - Task Define the cid: minting and validation spec.
- Context S2 requires deterministic ID assignment; UNKNOWN must not block admission.
- Inputs Integrated Project Plan GAP-01 section; Decisions Register rule on UUIDv7 cid identifiers.
- Outputs OUGHT target: /docs/specs/identity_cid_uuidv7.md
- Constraints - All locally minted identifiers are cid: - Fail closed on invalid format
## Validation (DONE) - Spec includes regex/BNF, examples (valid/invalid), and error mapping to ABORT/DENY reason codes.

- Dependencies BR-00.1
- Non-goals - Cross-system identifier reconciliation
## ### Work item BR-01.2 - Task Implement cid: library and tests.
- Context Runtime components must mint and validate ids deterministically.
- Inputs /docs/specs/identity_cid_uuidv7.md
- Outputs OUGHT targets: - /src/common/identity.py (or equivalent) - /tests/test_identity.py
- Constraints - No timestamp heuristics beyond UUIDv7 generation itself - Deterministic validation
## Validation (DONE) - Unit tests: mint → validate pass; invalid strings fail; round-trip parsing checks.

- Dependencies BR-01.1
- Non-goals - Distributed id issuance
## GAP-02 Ledger & ordering

## ### Work item BR-02.1 - Task Define ledger API contract (append, read, as-of, replay) and ordering rules.
- Context Ledger must be append-only, partitioned by tenant_id, and totally ordered per partition by a single ordering authority.
- Inputs Integrated Project Plan GAP-02 section; Decisions Register ordering expectations.
- Outputs OUGHT target: /docs/specs/ledger_api_and_ordering.md
- Constraints - Total order per tenant partition - Event_time assigned at commit by ordering authority - Tie-break using event_id ordering (UUID)
## Validation (DONE) - Spec includes: record fields, ordering comparator, example sequences, replay/as-of semantics.

- Dependencies BR-00.1, BR-01.1
- Non-goals - Multi-writer distributed ledger
## ### Work item BR-02.2 - Task Implement append-only ledger service with single-writer ordering authority.
- Context Need atomic append + stable replay/as-of reads for build readiness gate.
- Inputs /docs/specs/ledger_api_and_ordering.md
- Outputs OUGHT targets: - /src/ledger/* - /tests/test_ledger_determinism.py
- Constraints - Immutable history (no updates/deletes) - Partitioned by tenant_id - event_time assigned on append
## Validation (DONE) - Deterministic replay test passes. - As-of reads return correct prefix by event_time.

- Dependencies BR-02.1
- Non-goals - High availability/failover in MVP
## GAP-03 Root-of-trust / IssuerProof determinism (S5)

## ### Work item BR-03.1 - Task Define IssuerProof format and verification algorithm (MVP-single mechanism).
- Context S5 requires deterministic IssuerProof verification.
- Inputs Integrated Project Plan GAP-03 section.
- Outputs OUGHT target: /docs/specs/issuerproof_v1.md
- Constraints - Single proof mechanism for MVP - Fail closed
## Validation (DONE) - Spec includes fields, canonicalization, verify steps, error→reason-code mapping.

- Dependencies BR-00.1, BR-02.1
- Non-goals - Multiple proof schemes
## ### Work item BR-03.2 - Task Implement IssuerProof verifier and negative tests.
- Context Verifier must be deterministic.
- Inputs /docs/specs/issuerproof_v1.md
- Outputs OUGHT targets: - /src/security/issuerproof_verify.py - /tests/test_issuerproof_verify.py
- Constraints - Deterministic canonicalization - No network calls during verify
## Validation (DONE) - Valid proof passes; modified payload fails; wrong key fails; missing fields fail.

- Dependencies BR-03.1
- Non-goals - KMS integration beyond minimal test keys
## GAP-04 Execution engine boundary (S6)

## ### Work item BR-04.1 - Task Define evaluator boundary interface and commit semantics.
- Context Evaluation must have no side effects; side effects only after commit.
- Inputs Integrated Project Plan GAP-04 section.
- Outputs OUGHT target: /docs/specs/evaluator_boundary_v1.md
- Constraints - Commit ordering: ExecutionEvent appended first - Fail closed
## Validation (DONE) - Spec includes inputs/outputs and evaluate→commit→execute sequence.

- Dependencies BR-00.1, BR-02.1
- Non-goals - Full workflow engine
## ### Work item BR-04.2 - Task Implement evaluator stub and commit-boundary enforcement tests.
- Context Prove commit-first semantics.
- Inputs /docs/specs/evaluator_boundary_v1.md
- Outputs OUGHT targets: - /src/runtime/evaluator.py - /tests/test_commit_boundary.py
- Constraints - Evaluator pure (no side effects)
## Validation (DONE) - If commit fails → side effect not called; if commit succeeds → side effect called exactly once.

- Dependencies BR-04.1, BR-02.2
- Non-goals - External integrations beyond mocks
## GAP-05 Evidence chain & packaging

## ### Work item BR-05.1 - Task Define release manifest and load-manifest schemas + fixtures.
- Context Runtimes must verify payload and evidence before load.
- Inputs Integrated Project Plan GAP-05 section.
- Outputs OUGHT targets: - /schemas/release_manifest.schema.json - /schemas/runtime_load_manifest.schema.json - /fixtures/manifests/*
- Constraints - SHA-256 digests - No constraints fields in MVP
## Validation (DONE) - Schema tests validate positive fixtures and reject forbidden fields.

- Dependencies BR-00.1, BR-01.1
- Non-goals - Multi-format packaging
## ### Work item BR-05.2 - Task Implement packager that emits manifest + hashes + file list.
- Inputs /schemas/release_manifest.schema.json
- Outputs OUGHT targets: - /tools/packager.py - /tests/test_packager_golden.py
- Constraints - Deterministic file ordering
## Validation (DONE) - Golden test: identical inputs → identical manifest/hashes.

- Dependencies BR-05.1
- Non-goals - Signing packages
## ### Work item BR-05.3 - Task Implement verifier + loader rejection logic with tamper tests.
- Inputs /schemas/*; /tools/packager.py
- Outputs OUGHT targets: - /src/runtime/loader_verify.py - /tests/test_loader_rejects_tamper.py - /tests/test_loader_tenant_mismatch.py
- Constraints - Fail closed
## Validation (DONE) - Tamper/mismatch tests reject.

- Dependencies BR-05.2, BR-02.2
- Non-goals - Alias management beyond explicit manifest selection
## GAP-06 Operational ontologies (minimal real artifacts)

## ### Work item BR-06.1 - Task Create minimal SupportOntologyRelease payload + first package.
- Outputs OUGHT targets: - /ontologies/support/support_v0.1.ttl (or .jsonld) - /releases/support_ontology/support_v0.1/*
## Validation (DONE) - Ontology validation passes and package verifies.

- Dependencies BR-05.2, BR-05.3
## ### Work item BR-06.2 - Task Create minimal SCR_TBox_Release payload + first tenant package.
- Outputs OUGHT targets: - /ontologies/tenant/<tenant_id>/scr_tbox_v0.1.ttl (or .jsonld) - /releases/scr_tbox/<tenant_id>/scr_tbox_v0.1/*
## Validation (DONE) - Validation passes; package verifies; loader enforces tenant match.

- Dependencies BR-05.3, BR-02.2

---

Note: This conversion preserves extracted text for planning traceability.
