# Proposals Backlog

This space holds implementation proposals that are not yet scheduled into active execution.

## Purpose

- Capture incoming proposals in one stable location.
- Preserve proposal intent without treating proposal text as canonical governance.
- Enable later triage into active plans and tasks.

## Rules

- Proposal files are descriptive intake artifacts.
- Proposal presence does not imply approval, priority, eligibility, or execution.
- Canonical binding authority remains in `specs/` contract/governance documents.

## File conventions

- Proposal file: `P-XXXX-<slug>.md`
- Intake template: `TEMPLATE_proposal.md`
- Index: `proposals_index.csv`

## Status values

- `NEW`: captured, not triaged.
- `TRIAGED`: reviewed and classified.
- `SCHEDULED`: linked to a plan/workstream.
- `ARCHIVED`: closed without scheduling or superseded.

## Workflow

1. Create a new proposal file from the template.
2. Add one row to `proposals_index.csv`.
3. Keep proposal text descriptive and non-binding.
4. When ready, map proposal to execution artifacts in `bootstrap/plans/`.
