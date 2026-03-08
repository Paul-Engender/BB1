# Work Decomposition Protocol v0.1 (Bootstrap Canonical)

## Canonical Source Rule

- Governance authority source: `specs/ontoForge_81_WorkDecomposition_Protocol_v01.md`.
- This markdown file is the repo-operational mirror used for execution and tooling.
- If conflict exists, the governance source doc prevails.

## Purpose

Define agent-executable decomposition so bounded-context execution can complete reliably.

## Decomposition Rule

Decompose work until each task has:
- One primary deliverable (one artifact)
- Explicit inputs and outputs
- Bounded dependencies (at most two upstream dependencies)
- Machine-checkable DONE criteria
- No mixed intent (decision and implementation are separate tasks)

## Sizing Heuristic

Split if any are true:
- The task requires more than 10-15 lines to specify clearly
- Validation crosses more than one subsystem boundary
- Acceptance criteria cannot be written without additional design work

## Work Item Template

- Task: Verb + object
- Context: 2-4 lines with canonical references when relevant
- Inputs: Files, records, fixtures
- Outputs: Exact artifact path(s)
- Constraints: Hard boundaries
- Validation (DONE): Commands/tests and expected outcomes
- Dependencies: At most two upstream dependencies
- Non-goals: Explicit exclusions

## Status Mapping

- `COMPLETED`: Outputs exist but validation not yet passed
- `DONE`: Validation passed and evidence is recorded

## Enforceable Bootstrap Rules

For `TASK-*` rows in the task ledger:
- Must map to a `BPL-*` coordination task
- Must include at least one evidence row id
- Must declare exactly one output path
- Must declare no more than two dependencies
- `DONE` requires non-empty validation evidence



