# Runtime 1 Hardening Addendum v1

Status: IS
Owner: paul
Plan Item: P1-014
Date: 2026-03-07

## Purpose

Close remaining Runtime 1 tooling gaps so Support Ontology release operations are
stable, deterministic-capable, schema-validated, and promotion-gated.

## Hardening Controls

1. Deterministic build mode
- Packager supports deterministic tar metadata, deterministic ordering, and
  deterministic CID generation from content digests.
- Runtime 1 uses deterministic mode by default for support-release builds.

2. Manifest schema gate
- Runtime 1 validates generated `release_manifest.json` against
  `schemas/release_manifest.schema.json` before promotion.

3. Promotion gate artifact
- Runtime 1 executes loader verification before promotion approval.
- Runtime 1 emits `promotion_decision.json` with decision status and digest
  references.

4. Test hardening
- Deterministic rebuild test asserts stable digest/IDs across repeated builds.
- Promotion-decision test asserts approved decision artifact is emitted.

## Exit Criteria

Runtime 1 is considered operationally hardened when:
- deterministic mode builds are stable for unchanged inputs,
- manifests pass schema checks,
- promotion decision artifacts are produced,
- loader verification passes during promotion gate.
