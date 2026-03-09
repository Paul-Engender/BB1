# Canonical Spec Set Baseline v1

Status: IS
Owner: paul
Plan Item: P1-009
Task: TASK-09.1
Date: 2026-03-06

## Purpose

Define the canonical specification set used as the authority baseline for the spec-upgrade program.
This baseline freezes source-of-truth boundaries before delta analysis and migration execution.

## Scope Boundary

In scope:
- Governance and doctrine contract sources.
- Operating and decomposition protocols.
- Phase-0 backlog and evidence gate source records.
- Active module-level implementation specs used by runtime components.

Out of scope:
- Generated runtime artifacts in `dist/`.
- Bootstrap ledger files (`bootstrap/*.csv`) as authority sources.
- Archived conversion copies in `bootstrap/plans/archive/`.

## Canonical Set

| Canonical ID | File | Role | Authority Tier | Baseline State |
| --- | --- | --- | --- | --- |
| OF-00 | `specs/ontoForge_00_Canonical-Document-Set_Map_v1.0.md` | Canonical document map | Governance | IS |
| OF-01 | `specs/ontoForge_01_Doctrine_v1.1.md` | Program doctrine | Governance | IS |
| OF-02 | `specs/ontoForge_02_Lifecycle-Specification_v1.1.md` | Lifecycle contract | Governance | IS |
| OF-03 | `specs/ontoForge_03_Product-Spec_V1.1.md` | Product contract | Governance | IS |
| OF-04 | `specs/ontoForge_04_Decisions-Register_v1.1.md` | Decision authority register | Governance | IS |
| OF-80 | `specs/ontoForge_80_ProjectOperatingProtocolV01.md` | Project operating protocol | Governance/Protocol | IS |
| OF-81 | `specs/ontoForge_81_WorkDecomposition_Protocol_v01.md` | Work decomposition protocol | Governance/Protocol | IS |
| OF-90 | `specs/ontoForge_90_Implementation-plane_backlog.md` | Implementation-plane backlog source | Backlog | IS |
| OF-91 | `specs/ontoForge_91_Build-Readiness Backlog v0.1.md` | Build-readiness backlog source | Backlog | IS |
| OF-92 | `specs/ontoForge_92_Evidence-Pack_v01.md` | Evidence gate source | Evidence | IS |
| CID-SPEC | `specs/identity_cid_uuidv7.md` | Identity implementation spec | Module spec | IS |
| LEDGER-SPEC | `specs/ledger_api_and_ordering.md` | Ledger implementation spec | Module spec | IS |
| ISSUERPROOF-SPEC | `specs/issuerproof_v1.md` | IssuerProof implementation spec | Module spec | IS |
| EVALUATOR-SPEC | `specs/evaluator_boundary_v1.md` | Evaluator boundary implementation spec | Module spec | IS |
| RUNTIME-INST-ADD-20260307 | `specs/product_runtime_instantiation_clarification_addendum_2026-03-07.md` | Runtime instantiation clarification addendum | Directional Addendum | IS |

## Baseline Rules

1. Canonical authority for governance semantics remains in the `specs/ontoForge_*.md` set.
2. Markdown files under `bootstrap/` are operational mirrors and controls, not governance authority.
3. New migration tasks must reference only canonical-set members as input authority.
4. Any source changes require a delta entry in `specs/spec_upgrade/migration_delta_register_v1.md`.

## Execution Hand-off to TASK-09.2

Inputs provided to TASK-09.2:
- This baseline file.
- Canonical set member files listed above.

Required output from TASK-09.2:
- `specs/spec_upgrade/migration_delta_register_v1.md` with one row per canonical source delta.
