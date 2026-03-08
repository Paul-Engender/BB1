# P-0001: Term Card View for Kernel Ontology Terms

## Metadata

- Proposal ID: `P-0001`
- Title: `Term Card View for Kernel Ontology Terms`
- Submitted date: `2026-03-08`
- Source: conversation intake
- Status: `NEW`
- Scope tags: ontology, shacl, ui, deterministic-build, semantic-inspection

## Plane note (non-binding)

This file is an implementation proposal capture and does not create governance authority, approval state, eligibility, execution state, or canonical contract meaning.

## Purpose

Build a term-card view that gives a full, structured, inspection-oriented view of an ontology term (especially classes) in context, while preserving semantic plane separation and non-entailment rules.

## Product intent

A selected term should open a coherent card showing:

- identity
- ontology definition
- inheritance context
- linked properties
- SHACL constraints
- neighboring terms
- runtime/context tagging
- examples
- interpretation guardrails

## Non-goals

- No governance-force inference from ontology structure
- No runtime-authority inference from class membership
- No semantics inferred beyond RDF/OWL/SHACL assertions
- No executable meaning inferred from prose notes
- No ontology editing from this surface
- No canonical contract generation from this surface
- No source-of-truth shift away from canonical ontology payload

## Core design principles

1. Plane separation across:
- ontology facts
- descriptive text
- SHACL constraints
- architecture/runtime context
- governance interpretation guardrails

2. Non-entailment by default:
- if not explicitly modeled, do not imply it

3. Source traceability:
- each field must trace to ontology triples, SHACL, curated enrichment, or deterministic derivation

4. Deterministic output:
- same input ontology + enrichment must produce same card JSON

## Proposed term-card sections

A. Identity
- iri, qname, localName, label, entityType, sourceOntology, versionTag

B. Definition
- definition, comment, editorialNote, alternativeLabels, explicit status

C. Ontological position
- classes: direct/all superclasses, direct subclasses, equivalent/disjoint classes
- properties: subPropertyOf, inverseOf, declared characteristics

D. Structural semantics
- incoming/outgoing properties, domain/range participation, expected linked terms

E. Constraint context (SHACL layer)
- applicable shapes, required/optional props, cardinality/datatype/class/enum/conditional rules, closed-shape indicator

F. Usage neighborhood
- common neighbors, motifs, connected patterns, related terms by shared contexts

G. Runtime/architecture context (curated enrichment only)
- primaryRuntime, lifecycleRole, notes

H. Guardrails
- common misreadings, explicit non-entailments, interpretation warnings

I. Examples
- minimal ontology example turtle
- minimal SHACL-conformant example turtle
- narrative

## Extraction model

Layer 1: ontology extraction from `ontology/kernel.ttl`
- declarations, labels/definitions/comments, subclass/domain/range, explicit restrictions, relevant named individuals

Layer 2: SHACL extraction from `ontology/kernel.shacl.ttl`
- targets, property shapes, min/max, datatype/class, enums, hasValue, simple conditionals

Layer 3: deterministic derivation
- ancestry/descendancy closures, touching properties, related shapes, local neighbors, section summaries

Layer 4: curated enrichment
- runtime ownership, lifecycle role, explanatory notes, guardrails, ordering hints

## Build/output contract

- normalized JSON schema for term cards
- one generated JSON card per term (Phase 1 starts with classes)
- deterministic static generation recommended first
- outputs include a searchable index and per-term artifacts

## UI guidance

- search/click term opens card page or side panel
- visibly separate asserted facts, derived facts, SHACL constraints, curated notes
- include source-layer badges/tags
- local graph neighborhood only by default (not full ontology graph)

## Repository layout proposal

- `/apps/term-cards-ui`
- `/packages/ontology-parser`
- `/packages/term-card-builder`
- `/data/ontology/kernel.ttl`
- `/data/shapes/kernel.shacl.ttl`
- `/data/enrichment/term-card.enrichment.yaml`
- `/generated/term-cards/`

## Acceptance criteria

- AC-1 class cards can be generated for any class in `kernel.ttl`
- AC-2 targeted SHACL shapes and rules appear on card
- AC-3 clear separation across asserted/constraint/derived/curated layers
- AC-4 no unstated semantic inference
- AC-5 navigable links across related super/sub/property/shape terms
- AC-6 each card has guardrail field(s)
- AC-7 deterministic build output
- AC-8 generated card layer does not mutate ontology semantics

## Tests requested

- Test 1: `kern:TargetReference` superclass + required shape rules
- Test 2: `kern:Stipulation` nature enum + `stipulatesOn` target rule
- Test 3: conditional evaluator rule appears only in constraints section
- Test 4: curated runtime note updates without mutating asserted ontology facts
- Test 5: missing enrichment file does not break generation

## Phased delivery

- Phase 1: class cards
- Phase 2: properties + individuals
- Phase 3: graph navigation
- Phase 4: version diff mode

## Risks and controls

- Risk: blending ontology and governance meaning
  Control: section separation + source-layer badges

- Risk: runtime ownership inferred from names/namespaces
  Control: runtime context only from curated enrichment

- Risk: SHACL mistaken for ontology definition
  Control: label as constraint layer

- Risk: synthetic lossy summaries
  Control: prefer structured fields over generated prose

## Triage placeholder

- Decision: pending
- Owner: pending
- Scheduled work item(s): pending
- Notes: captured for backlog holding area
