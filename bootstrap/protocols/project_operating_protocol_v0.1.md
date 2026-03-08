# Project Operating Protocol v0.1 (Bootstrap Canonical)

## Canonical Source Rule

- Governance authority source: `specs/ontoForge_80_ProjectOperatingProtocolV01.md`.
- This markdown file is the repo-operational mirror used for execution and tooling.
- If conflict exists, the governance source doc prevails.

## Purpose

This protocol governs implementation-plane execution during bootstrap and Phase-0 coordination.
It does not create or modify governance-plane authority.

## Scope

Applies to:
- Project plans
- Design and architecture working docs
- Sprint/cycle execution
- Operational communication and reporting

Excludes:
- Canonical governance contract changes
- Governance authority interpretation by prose or file placement

## IS vs OUGHT Discipline

- `IS`: Proven operational state supported by evidence.
- `OUGHT`: Intended state or target not yet proven.
- `UNKNOWN`: State that has not been evidenced.

Rules:
- Do not assert `IS` without evidence.
- If state is planned, label it `OUGHT`.
- If state is unknown, label it `UNKNOWN`.
- Any path/state mentioned in a task must be classifiable as `IS`, `OUGHT`, or `UNKNOWN`.

## Document Classes

1. Canonical governance documents
- Binding for governance semantics.
- Must change only through decision protocol and canonical update process.

2. Directional design documents
- Non-binding architecture direction.
- Evolves through reviewed updates.

3. Implementation-plane documents
- Operational coordination only.
- No governance authority.

## Status Model

- `TO_DO`: Committed upcoming work.
- `IN_PROGRESS`: Work in execution.
- `BLOCKED`: Work cannot proceed due to an explicit blocker.
- `COMPLETED`: Output exists; validation not fully passed.
- `DONE`: Output validated with evidence.
- `DID_NOT_DO`: Planned work not executed.

Invariants:
- `DONE != COMPLETED`
- `DONE = COMPLETED + VERIFIED + VALIDATED`

## Task Validation Rule

Every task must define validation criteria before execution.

Required for `DONE`:
- Validation method present
- Validation evidence present
- Referenced output paths exist (for IS claims)

## Change Record Minimum

Every operational change should include:
- Change type (`proposal|update|decision|correction`)
- Affected document/section
- Reason
- Impact class (`governance|architecture|execution`)
- Status (`pending review|accepted|rejected`)

## Sprint Checkpoint Output

Checkpoint reports should include:
- `DONE`
- `COMPLETED`
- `DID NOT DO`
- `TO DO`
- `NEXT RECOMMENDED ACTION`
- `RISKS / BLOCKERS`



