# Kernel PM v1 Scope Decision - Full Profile Operations v1

Status: ACTIVE
Owner: paul
Date: 2026-03-09
Plane: implementation
Operational role: ACTIVE_CONTROL

## Purpose

Record the approved scope decision for kernel PM v1 and define the activation
boundary for forward project-management operations.

## Decision

Approved scope target:
- full profile operations for kernel PM v1

Effective date:
- 2026-03-09

## Existing Scope (As Implemented Before This Decision)

Bridge subset operations:
- forward bundle authority for selected planning objects
- deterministic projection of forward bundle into:
  - `phase2_plan_items_projection.csv`
  - `task_ledger_projection.csv`
  - `evidence_register_projection.csv`
- legacy/bridge CSV controls retained for execution continuity:
  - `phase1_plan_items.csv`
  - `task_ledger.csv`
  - `evidence_register.csv`
  - `artifact_registry.csv`

## New Scope (Approved Target)

Kernel PM v1 forward operations now target the full profile object space:
- planning objects
- dependencies
- role assignment
- checkpoints
- execution activity/recording
- evidence linkage
- risk/issue/mitigation
- change requests and impact assessments

## Activation Boundary

This decision applies to forward work instantiation after `C0`.

It does not retroactively rewrite pre-`C0` historical records.

## Implementation Rule

Until full-profile projections and validators are complete:
- existing bridge controls remain valid
- forward additions should be represented in the kernel bundle first
- deterministic projection surfaces are the approved read views

## Operational Note

`specs/kernel_project_execution_profile_v1.md` remains `PROPOSED` until
full-profile operational surfaces and enforcement checks are complete.
