# Kernel Project Execution Profile v1

Status: PROPOSED
Owner: paul
Date: 2026-03-08
Plane: implementation

## Purpose

Define a machine-checkable kernel-native project-management profile for forward
work instantiation after cutover `C0`.

This profile is implementation-plane guidance. It does not create governance
authority or execution truth by prose.

## Profile Scope

The profile defines canonical object kinds, required relations, and validation
rules for:
- planning hierarchy
- dependency modeling
- role assignment
- validation specifications
- execution/activity recording
- evidence linkage
- risk/issue/mitigation/change structures

## Object Kinds

Mandatory kind vocabulary for the first profile:
- `ProgramPlan`
- `WorkstreamPlan`
- `WorkPackagePlan`
- `TaskSpecification`
- `CheckpointSpecification`
- `DependencyRelation`
- `DependencyKind`
- `ValidationSpecification`
- `RoleAssignment`
- `HumanAgent`
- `SystemAgent`
- `Role`
- `TaskExecutionActivity`
- `TaskExecutionRecord`
- `CheckpointRecord`
- `EvidenceRecord`
- `RiskRecord`
- `IssueRecord`
- `MitigationPlan`
- `ChangeRequest`
- `ImpactAssessment`

## Status Model

Allowed status values:
- `IS`
- `OUGHT`
- `UNKNOWN`

`IS` must not be used without supporting evidence on execution-bearing records.

## Required Relation Rules (v1)

- `ProgramPlan` MUST use `hasSubPlan` to at least one `WorkstreamPlan`.
- `WorkstreamPlan` MUST use `hasSubPlan` to at least one `WorkPackagePlan`.
- `WorkPackagePlan` MUST use `hasSubPlan` to at least one `TaskSpecification`.
- `TaskSpecification` MUST reference exactly one `ValidationSpecification` via
  `hasValidationSpecification`.
- `DependencyRelation` MUST reference exactly one source and one target task via
  `dependencySource` and `dependencyTarget`, and exactly one `DependencyKind`
  via `hasDependencyKind`.
- `RoleAssignment` MUST reference exactly one agent via `assignsAgent`, exactly
  one role via `assignsRole`, and at least one scoped plan via
  `assignmentScopePlan`.
- `ValidationSpecification` MUST reference at least one `EvidenceRecord` via
  `expectsEvidenceRecord`.
- `TaskExecutionRecord` MUST reference exactly one `TaskSpecification` via
  `recordsExecutionOf` and exactly one `TaskExecutionActivity` via
  `evidencesActivity`.

## Machine Artifacts

This profile is implemented by:
- `schemas/kernel_project_bundle.schema.json`
- `schemas/kernel_project_validation_rules_v1.json`
- `tools/validate_kernel_project_bundle.py`

## Authority Note

This profile defines how to represent and validate project objects. It does not
replace canonical doctrine, lifecycle, product, or decisions-register authority.