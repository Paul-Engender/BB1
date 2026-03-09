# Support Ontology External Ontology Policy v1

Status: APPROVED
Owner: paul
Plan Item: P1-015
Task: TASK-15.4
Date: 2026-03-07

## Purpose

Define controlled intake and promotion rules for external ontology terms so they can be evaluated without creating implicit binding adoption in the support ontology layer.

This policy is bound to:
- `specs/support_ontology_governance_incorporation_model_v1.md`
- `specs/ontoForge_01_Doctrine_v1.1.md`
- `specs/ontoForge_02_Lifecycle-Specification_v1.1.md`
- `specs/ontoForge_04_Decisions-Register_v1.1.md`

## Constitutional Boundary

External ontology references are never self-authorizing.

No external term becomes binding by:
- namespace mention
- import presence
- mapping row existence
- semantic similarity claim

Binding adoption requires explicit promotion and evidence under this policy.

## Default Handling Rule

Default state for every external mapping row is `proposed` and non-binding.

In `proposed` state, rows are:
- excluded from release payload composition
- excluded from compile-permissive semantics
- excluded from canonical support contracts
- allowed only for evaluation and coverage analysis

## Candidate Register

Candidate register path:
- `specs/support_ontology_external_mapping_candidates_v1.csv`

Register role:
- evaluation queue only
- not an adoption register

Required columns in the register:
- `ext_uri_pk`
- `ext_ontology_req`
- `ext_kind_req`
- `ext_label`
- `ext_parent_uri`
- `ext_status`
- `ext_notes`
- `term_id_internal_req`
- `map_strength`
- `bridge_axiom`
- `mapping_status`
- `rationale`

## Lifecycle States

Allowed `mapping_status` values:
- `proposed`
- `under_review`
- `approved_for_eval`
- `approved_for_binding`
- `rejected`
- `retired`

State meaning:
- `approved_for_eval`: allowed in controlled evaluation artifacts only
- `approved_for_binding`: allowed for binding use, but only after explicit approval + evidence

## Promotion Gates

### Gate A: proposed -> approved_for_eval

All must pass:
- source pinning: stable external URI and source ontology identity are explicit
- semantic intent clarity: rationale and mapping strength are explicit
- governance boundary fit: no doctrine/lifecycle/decision conflict found

### Gate B: approved_for_eval -> approved_for_binding

All must pass:
- governance traceability complete per `TASK-15.3` model
- DD-anchor fit verified:
  - DD-001 identifier discipline preserved
  - DD-003 ordering-sensitive semantics not pushed into ontology-only form
  - DD-004 MVP constraint exclusion preserved
  - DD-005 eligibility boundary preserved
- conflict review passed against existing support-layer terms
- binding decision explicitly approved by paul and recorded in evidence

Without Gate B completion, binding use is prohibited.

## Mapping Semantics Rules

`map_strength` interpretation:
- `skos:exactMatch`: candidate equivalence claim, highest review burden
- `skos:closeMatch`: near alignment only, never equivalence
- `skos:noMatch`: intentional gap declaration, valid non-adoption outcome

`bridge_axiom` interpretation:
- `rdfs:subClassOf` is non-binding while status is below `approved_for_binding`
- blank bridge axiom asserts no bridge

## Runtime Usage Controls

1. Runtime 1
- may use candidates for evaluation reports only
- must not include non-binding candidates in canonical support release payload

2. Runtime 2
- must not treat non-binding external mappings as admissibility/permissive defaults
- compile remains fail-closed if required semantics are missing

3. Runtime 3
- out of scope for direct external ontology intake under this task
- no operational authority inference from external mapping rows

## Required Evidence for Binding Promotion

Every `approved_for_binding` row must have evidence artifacts covering:
- review record with decision owner and date
- conflict analysis result
- traceability linkage to canonical sources and decision anchors
- validation output proving no fail-open behavior introduced

## Current Seed Set Disposition

Current BFO/IAO seed rows in the candidate register are retained as:
- `mapping_status = proposed`
- non-binding
- eligible for staged review only

Rows marked `skos:noMatch` remain valid intentional gap records and do not require forced mapping.

## Validation Checklist (TASK-15.4)

- policy forbids implicit external ontology binding
- policy defines promotion gates and explicit approval requirement
- policy aligns with `TASK-15.3` governance boundary
- candidate register exists and is parseable
- all seed rows have explicit `mapping_status`
- no row is treated as binding unless `approved_for_binding` with evidence
