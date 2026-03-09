# Cutover C0 Snapshot Record v1

Status: ACTIVE
Owner: paul
Date: 2026-03-08
Plane: implementation
Operational role: ACTIVE_CONTROL
Cutover ID: C0
Cutover timestamp: 2026-03-08T18:42:11+02:00

## Purpose

Record the authoritative cutover marker between legacy CSV-ledger execution
management and forward kernel-aligned project instantiation.

This document defines the freeze boundary, frozen-hash snapshot, and forward
instantiation rule.

## Boundary Notice

This is an implementation-plane control record.

It does not create governance authority, runtime permission, or execution truth
by prose. Execution truth remains evidence-bound through explicit records.

## Source Inputs

- `bootstrap/plans/inactive/reference/cutover_and_legacy_archive_proposal_v1.md`
- `bootstrap/plans/phase1_execution_plan.md`
- `bootstrap/plans/phase1_plan_items.csv`
- `bootstrap/task_ledger.csv`
- `bootstrap/evidence_register.csv`
- `bootstrap/artifact_registry.csv`

## Cutover Preconditions (at C0)

The following state was true at cutover:
- support-ontology program work P1-001..P1-026 is complete
- successor M1 (`P2-001`) is complete and verified
- Runtime 1 successor task package (`TASK-28.1..28.3`) is complete and
  verification-ready under `EP-28`
- Runtime 2 decomposition task package (`TASK-29.1..29.5`) is complete
- no Runtime 2 executable compiler implementation task after decomposition has
  yet been created

## Freeze Scope (L0)

Legacy execution control surfaces frozen at `C0`:
- `bootstrap/plans/phase1_execution_plan.md`
- `bootstrap/plans/phase1_plan_items.csv`
- `bootstrap/task_ledger.csv`
- `bootstrap/evidence_register.csv`
- `bootstrap/artifact_registry.csv`

Freeze rule:
- pre-`C0` rows are historical truth and are read-only
- only additive cross-reference pointers are permitted for pre-`C0` entries

## Frozen Hash Snapshot

SHA256 at `C0`:
- `bootstrap/plans/phase1_execution_plan.md`
  - `cd06951f3fce35ca76f72dab3e0cf8fc703e7c7c14492516fa22db4aa29690ea`
- `bootstrap/plans/phase1_plan_items.csv`
  - `396434d6d6910ef85e4e72010ceec64cbe9fb4676079b0311222d95573e096ef`
- `bootstrap/task_ledger.csv`
  - `44efd2d7b25baf551bfb4674205b5214877f0f7b65f97e78605260347b4d28ff`
- `bootstrap/evidence_register.csv`
  - `e593ddcc7a49e39cae2e587874ceffdffe387e81b4f62eaac137bb331223b51b`
- `bootstrap/artifact_registry.csv`
  - `d820bf8613788d96f8da0d68d6c161e0b6af0d7523b7afb189558a78a7a622e6`

## Authority Split Rule

Before `C0`:
- legacy CSV-ledger control surfaces are authoritative historical execution
  truth

From `C0` onward:
- kernel-aligned project records are authoritative for newly created work

No dual authority is allowed for the same time slice.

## Forward Scope (N0)

From `C0`, recreate and manage only open/planned work in kernel-aligned form:
- active and queued workstreams
- open work packages
- open task specifications
- checkpoint specifications
- dependency relations
- validation specifications
- migration risk/issue/mitigation/change structures

Historical backfill is deferred and not part of first-pass cutover.

## Open Frontier at C0

Open tasks:
- `TASK-30.1`
- `TASK-31.1`
- `TASK-32.1`

Open evidence rows:
- `EP-28`
- `EP-29`
- `EP-30`
- `EP-31`
- `EP-32`

## Immediate Follow-on

Next control artifact:
- `bootstrap/plans/active/cutover_execution_transition_plan_v1.md`

This follow-on should define exact first kernel-aligned forward objects and the
projection policy for any residual legacy views.
