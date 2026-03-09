# Planning Target Operating Model v1

Status: ACTIVE
Owner: paul
Date: 2026-03-08

## Purpose

Define the target project-management discipline for this repo by translating the canonical ontoForge governance and protocol documents into explicit execution-plane operating rules.

## Canonical basis

- `specs/ontoForge_00_Canonical-Document-Set_Map_v1.0.md`
- `specs/ontoForge_01_Doctrine_v1.1.md`
- `specs/ontoForge_02_Lifecycle-Specification_v1.1.md`
- `specs/ontoForge_03_Product-Spec_V1.1.md`
- `specs/ontoForge_04_Decisions-Register_v1.1.md`
- `specs/ontoForge_80_ProjectOperatingProtocolV01.md`
- `specs/ontoForge_81_WorkDecomposition_Protocol_v01.md`

## Operating interpretation

- Descriptive surfaces do not carry operational force.
- Only explicit records may drive execution state, completion claims, or authority over planning scope.
- Governance meaning remains in `specs/`.
- Execution truth remains in `bootstrap/`.
- If a planning claim cannot be represented explicitly without defaults, it is commentary, not control.

## Authority chain

Planning authority resolves in this order:

1. `specs/` canonical governance and decisions
2. `bootstrap/plans/PLAN_INDEX.md`
3. `bootstrap/plans/phase1_execution_plan.md`
4. `bootstrap/plans/phase1_plan_items.csv`
5. `bootstrap/bridge/task_ledger.csv`
6. `bootstrap/bridge/evidence_register.csv`
7. `bootstrap/bridge/artifact_registry.csv`
8. `bootstrap/plans/manifests/plans_manifest.csv`

## Document classes

- `CANONICAL_GOVERNANCE`: binding governance and decision documents in `specs/`
- `DIRECTIONAL_DESIGN`: non-binding architecture and product direction in `specs/`
- `ACTIVE_CONTROL`: execution-plane documents that actively govern planning and work progression
- `REFERENCE`: execution-plane documents kept for traceability or historical interpretation
- `PROPOSAL`: intake material that does not authorize work
- `ARCHIVE`: closed or superseded records retained for auditability
- `TEMPLATE`: reusable intake or structure documents

## Lifecycle states

Allowed lifecycle states for planning documents:

- `DRAFT`
- `PROPOSED`
- `ACTIVE`
- `SUPERSEDED`
- `ARCHIVED`

Rule:

- For the same scope and `doc_type`, only one document may be both `ACTIVE` and `ACTIVE_CONTROL`.

## Folder model

Target structure for `bootstrap/plans/`:

- `active/`: active execution controls and orientation surfaces
- `programs/`: program and workstream decomposition documents
- `inactive/reference/`: retained backlog sources, alignment notes, and supporting interpretation docs
- `manifests/`: machine-readable planning manifests
- `inactive/proposals_backlog/`: non-binding proposal intake
- `archive/`: archived and superseded records

Implementation status note:

- Controlled relocation completed on 2026-03-09; inactive planning surfaces now live under `inactive/`.
- Validation, manifests, and cross-references were updated to match the inactive-folder structure.

## Naming convention

Planning filenames should use:

- lowercase
- underscores only
- no spaces
- terminal version tags such as `_v1.md` or `_v1.0.md`

Pattern:

- `<scope>_<artifact_type>_<state?>_v<version>.md`

Examples:

- `p2_full_solution_program_v1.md`
- `support_ontology_full_layer_backlog_reference_v1.md`
- `planning_target_operating_model_v1.md`

## Record model

Execution truth must be expressed through explicit records:

- plan items
- tasks
- evidence rows
- artifact rows
- planning manifest rows

Markdown plans are permitted, but they are views over these records and must not silently diverge from them.

## Transition rules

- A planning document becomes operational only when it has a manifest row.
- A document may move from `PROPOSED` to `ACTIVE` only if the manifest says so.
- A superseded document must name its replacement in the manifest.
- An archived document must remain immutable except for archive metadata corrections.
- A task may claim `DONE` only with validation evidence, consistent with the work decomposition protocol.

## Current repo application

- `bootstrap/plans/phase1_execution_plan.md` is the active execution-plan control.
- `bootstrap/plans/programs/post_p1_026_full_solution_program_plan_v1.md` is the active successor program control for P2 scope.
- `bootstrap/plans/inactive/reference/proposed_support_ontology_full_layer_backlog_v1.md` is a superseded reference backlog, not active execution control.
- `bootstrap/plans/inactive/proposals_backlog/` holds non-binding proposal intake only.

## Migration plan

Phase A:

- add target operating model
- add planning manifest
- classify existing planning docs
- fix contradictory status surfaces

Phase B:

- relocate files into target folders
- update cross-references
- update artifact hashes where tracked
- archive superseded paths

Phase C:

- extend validation tooling to check planning-manifest consistency
- fail closed on conflicting active documents for the same scope



