# Support Ontology Namespace and Import Policy v1

Status: APPROVED
Owner: paul
Plan Item: P1-016
Task: TASK-16.2
Date: 2026-03-07

## Purpose

Define namespace, import-closure, and versioning rules for canonical `SupportOntologyRelease` payloads so Runtime 2 receives a stable, deterministic upstream semantic contract.

This policy applies to the canonical payload defined in:
- `specs/support_ontology_release_composition_v1.md`
- `specs/product_runtime_instantiation_clarification_addendum_2026-03-07.md`

## Current State (Observed)

Current canonical-candidate files:
- `ontology/kernel.ttl`
- `ontology/kernel.shacl.ttl`

Observed characteristics:
- both files are anchored on `https://ontology.engender.co.za/kernel#`
- neither file currently declares `owl:imports`
- both files reference standard vocabularies (RDF/RDFS/OWL/SKOS/XSD/PROV)
- `kernel.ttl` references BFO/IAO IRIs by prefix but does not import external ontology graphs

Legacy/non-canonical files still present:
- `ontology/support.ttl` (placeholder; `http://example.org/support-ontology#`)
- `ontology/scr_tbox.ttl` (`http://example.org/scr-tbox#`, imports `so:`)

Per approved admission register, these legacy files are not canonical payload members.

## MVP Baseline (Current Enforced Mode)

MVP baseline for canonical payload remains:
- strict closed payload
- no external `owl:imports` in canonical support payload members
- no placeholder namespaces in canonical payload members

This baseline is the active policy mode for `TASK-16.2` closure and immediate Runtime 1/2 boundary safety.

## vNext Namespace Architecture (Directional, Governed)

The following architecture is accepted as directional for progressive adoption.

### 1) Façade tiers

- `A0` facade: upper canonical anchors (BFO-oriented anchor layer)
- `A2` facade: mid-level canonical bridge for information/normative semantics (IAO-oriented bridge)
- `A1` facade: non-canonical lens/mapping view (for interpretation and mapping only)

Governance stance:
- `A0` and `A2` may participate in binding semantic lineage when explicitly approved
- `A1` is non-binding and mapping-only

### 2) Functional governance namespaces

- `ontoGov`: governance boundary/rule namespace
- `ontoMean`: meaning assertions and status gating namespace
- `ontoTbox`: structural/TBox axiomatic namespace
- `u0`/`u4`: role/act semantic channels (governance-aware metadata lanes)

These are architectural channels and do not automatically become canonical payload members without explicit approval.

## Namespace Policy

### NP-1 Canonical base namespace

Canonical support payload namespaces MUST use governed production IRIs (not `example.org` placeholders).

Current canonical namespace root:
- `https://ontology.engender.co.za/kernel#`

### NP-2 Prefix hygiene

Canonical payload files MUST:
- declare explicit prefixes for all used namespaces
- avoid implicit/default namespace assumptions for governed terms
- keep prefix usage stable across releases unless explicitly versioned and documented

### NP-3 Placeholder namespace exclusion

The following namespace pattern is non-canonical for support release payload:
- `http://example.org/*`

Any file using placeholder namespaces may exist for transitional/testing purposes but MUST NOT be included in canonical support payloads.

## Facade Sanitary Rules (vNext)

### FS-1 No façade-level mixing in one channel

Do not mix terms from different external ontology levels into a single façade channel definition.

### FS-2 Canonical parent exclusivity

A binding kernel class MUST NOT assert canonical parents from both `A0` and `A2` simultaneously in the same asserted parent set.

Selection rule:
- choose one canonical asserted parent path
- use mapping assertions for alternate correspondence, not dual asserted lineage

### FS-3 A1 non-binding lens rule

`A1` classes MUST NOT be asserted parents of binding kernel classes.

`A1` may be used for:
- mapping views
- comparison lenses
- non-binding analysis artifacts

### FS-4 Equivalence governance rule

`owl:equivalentClass` across external/binding boundaries is high-risk and treated as a governance event.

Default relation for external alignment is:
- `rdfs:subClassOf` or explicit mapping assertions

`owl:equivalentClass` may be used only with explicit approval and evidence.

## Import Closure Policy

### IP-1 Default import stance (active)

Canonical payload files are import-closed for MVP:
- no `owl:imports` to external ontologies in canonical payload members
- semantic dependencies represented via governed local terms and approved mappings

Rationale:
- deterministic load behavior
- reduced supply-chain drift
- alignment with controlled external ontology intake policy

### IP-2 Conditional import exception

If an import is proposed, it is admissible only if all are true:
- external source is explicitly approved under external ontology policy
- version pinning is explicit and stable
- conflict review is complete and approved
- import is recorded in release evidence and dependency contract

Without those conditions, import is disallowed.

### IP-3 Transitive closure determinism

Runtime consumers must resolve canonical payload semantics without network fetches or mutable external state.

Canonical release verification therefore treats unresolved/implicit external imports as non-permissive.

## Version Policy

### VP-1 Release version authority

Release version authority remains at release-manifest layer (`artifact_version`, `artifact_id`).

Ontology-level version metadata is encouraged for clarity but must not conflict with manifest authority.

### VP-2 Ontology version metadata expectation

Canonical ontology artifacts should declare stable ontology identifiers and explicit version info (for example `owl:versionInfo`, and optionally `owl:versionIRI`), consistent with release manifests.

### VP-3 Breaking vs non-breaking namespace changes

Treat as breaking for support release contracts:
- namespace root change for canonical governed terms
- term IRI renaming/removal without compatibility plan
- import-policy changes affecting closure/determinism
- canonical lineage rule changes (`A0/A2` exclusivity, `A1` asserted-parent prohibition)

Treat as non-breaking (subject to review):
- additive term introduction within stable namespace
- additive SHACL constraints that do not invalidate previously valid canonical release artifacts without declared migration path

## Runtime Integration Rules

1. Runtime 1 packaging
- MUST include only canonical payload files (`kernel.ttl`, `kernel.shacl.ttl` per current composition contract)
- MUST reject canonical packaging attempts that include placeholder namespace payload members

2. Runtime 1 evaluation
- MUST verify namespace policy compliance and import-closure compliance as part of release candidate checks
- SHOULD emit explicit findings when façade sanitary rules are violated (for later hard-gate rollout)

3. Runtime 2 consumption
- MUST treat support payload namespace/import policy violations as non-permissive input
- MUST NOT infer permissive semantics from lens/mapping channels (`A1`)

## Policy Compliance Checklist

A support release composition is namespace/import compliant only if all are true:
- canonical payload members use governed production namespace(s)
- no placeholder namespace file is included as canonical payload
- import closure is satisfied (or approved exception recorded)
- version semantics are consistent between ontology metadata and manifest metadata
- no uncontrolled external dependency is required for semantic resolution
- no `A1` asserted-parent usage in binding kernel lineage
- no unapproved cross-boundary `owl:equivalentClass` commitments

## Implementation Notes for Next Task (TASK-16.3)

`TASK-16.3` should use this policy to update Runtime 1 payload contract with:
- explicit canonical payload file list
- explicit rejection behavior for placeholder namespace payloads
- explicit import-closure verification expectations in release candidate evaluation
- explicit handling rule for `A1` as non-binding lens channel
- explicit review gate for external `owl:equivalentClass` use

## Review Options

### Option A (Recommended): Strict closed payload + phased façade controls
- keep no-external-import MVP baseline
- adopt façade rules as policy now and roll into hard validator gates progressively

### Option B: Controlled pinned imports + phased façade controls
- allow narrowly approved external imports with version pinning and evidence gates
- higher governance overhead and higher drift/supply risk

Draft currently assumes **Option A**.

## Addendum Consideration

Namespace and import rules are defined to protect boundary-object integrity across runtime handoffs, not to blur runtime-internal lifecycle candidate semantics.

