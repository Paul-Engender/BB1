# Cutover and Legacy Archive Proposal v1

Status: SUPERSEDED
Owner: paul
Date: 2026-03-08
Plane: implementation
Role: reference proposal

## Purpose

Define the earliest safe cutover point to separate legacy CSV-ledger project
management from the kernel-aligned execution method, while preserving historical
execution truth and reducing migration risk.

## Boundary Notice

This is an implementation-plane proposal.

It does not create governance authority, execution permission, or completion
truth by prose. Binding execution truth remains evidence-bound through explicit
records.

## Core Cutover Decision

Cut over at the first boundary where:
- historical support-ontology program work is complete
- successor M1 closure is complete
- Runtime 2 decomposition is complete
- Runtime 2 executable compiler implementation has not started

Current repository state satisfies that boundary.

## Cutover Marker

`C0` is defined as:
- after `TASK-29.5` completion
- before first new Runtime 2 executable implementation task is created

This marker creates a clean split between:
- historical control-plane truth (legacy mode)
- forward planning/execution truth (kernel-aligned mode)

## Legacy Freeze Scope (L0)

At `C0`, freeze the following as read-only historical execution truth:
- `bootstrap/plans/phase1_execution_plan.md`
- `bootstrap/plans/phase1_plan_items.csv`
- `bootstrap/task_ledger.csv`
- `bootstrap/evidence_register.csv`
- `bootstrap/artifact_registry.csv`
- existing P1 and closed P2 control artifacts

Freeze rule:
- no further semantic mutation of pre-`C0` rows
- only additive cross-reference pointers are allowed

## Forward Recreate Scope (N0)

Recreate only open/planned work in kernel-aligned form:
- active workstreams and queued workstreams
- open work packages
- open task specifications
- checkpoint specifications
- explicit dependency relations
- validation specifications for forward tasks
- migration risk/issue/mitigation/change objects

Do not backfill historical execution records in first pass.

## Authority Split Rule

Before `C0`:
- legacy ledgers remain authoritative historical execution truth

From `C0` onward:
- kernel-aligned project records become the authoritative planning/execution
  surface for newly created work

No dual authority is permitted for the same time slice.

## Migration Modes

### Sequential Mode (recommended)

1. snapshot and freeze legacy control surfaces at `C0`
2. create kernel-aligned forward planning structures
3. create first new forward tasks only in new mode
4. add projection views if needed

Reason:
- lowest ambiguity and easiest auditability

### Parallel Mode (allowed with guardrails)

Run legacy and new-mode entries in parallel for a short proving window, but with
strict constraints:
- all new work is authored in new mode first
- legacy surfaces are projection-only mirrors for that window
- one-way projection only (new mode -> legacy view)

Reason:
- supports transition confidence while limiting split-brain risk

## Immediate Work Package

WP-CUTOVER-01 (proposal package):
- define `C0` snapshot record
- define legacy freeze policy
- define forward-only object creation policy
- define projection policy (none, one-way, or deferred)
- define migration verification checks

## Acceptance Criteria

AC-1
`C0` is explicitly recorded with source references.

AC-2
Legacy pre-`C0` execution surfaces are frozen and marked historical.

AC-3
New forward tasks created after `C0` are instantiated in kernel-aligned form.

AC-4
No work item exists with conflicting authority between legacy and new mode.

AC-5
Migration verification report can prove temporal and authority separation.

## Risks and Controls

Risk: split-brain authority between old and new modes.
Control: hard time-slice authority rule at `C0`.

Risk: migration drifts into full historical rewrite.
Control: first pass is forward-only recreate; historical backfill is deferred.

Risk: closure claims without validation proof.
Control: preserve explicit validation-specification and evidence-record binding.

## Recommended Next Artifact

`cutover_c0_snapshot_record_v1.md`

This should capture:
- exact timestamp
- exact pre-cutover artifact hashes
- exact legacy freeze declaration
- exact forward instantiation start marker


## Merged Into

- `bootstrap/plans/active/cutover_c0_snapshot_record_v1.md`
- `bootstrap/plans/active/cutover_execution_transition_plan_v1.md`
- `bootstrap/plans/active/kernel_pm_authority_switch_policy_v1.md`
