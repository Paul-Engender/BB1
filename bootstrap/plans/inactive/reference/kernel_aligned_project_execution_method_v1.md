# Kernel-Aligned Project Execution Method v1

Status: SUPERSEDED
Owner: paul
Date: 2026-03-08
Plane: implementation
Role: reference guidance

## Purpose

Define how project planning and execution are represented against the kernel
ontology without allowing prose, naming, placement, or document presence to
imply governance force or execution truth.

## Boundary Notice

This document is implementation-plane guidance.

It does not create governance authority, admissibility, eligibility, execution
permission, or execution commitment.

## Scope

This method covers representation of:
- planning structures
- execution records
- dependencies
- validation requirements
- accountability bindings
- risk, issue, mitigation, and change structures

This method does not define runtime authority events, runtime execution events,
or canonical governance contracts.

## Core Principle

A project is not instantiated by narrative description.

A project is instantiated only by explicit, typed kernel constructs with
identity, boundaries, and declared relations.

## Kind Separation Rules

- A `Plan` is not an execution record.
- A `TaskExecutionRecord` is not a `TaskExecutionActivity`.
- A `ValidationSpecification` is not evidence.
- A `RoleAssignment` is not authority.
- A `RiskRecord` is not an `IssueRecord`.
- A `ChangeRequest` is not an approved change.

## Instantiation Pattern

1. Create planning objects (`ProgramPlan`, `WorkstreamPlan`,
   `WorkPackagePlan`, `TaskSpecification`, `CheckpointSpecification`).
2. Bind plan hierarchy with `kern:hasSubPlan`.
3. Bind dependencies explicitly via `DependencyRelation` using:
   - `kern:dependencySource`
   - `kern:dependencyTarget`
   - `kern:hasDependencyKind`
4. Bind accountability through `RoleAssignment` relations.
5. Define `ValidationSpecification` before execution.
6. Record execution with `TaskExecutionActivity` plus `TaskExecutionRecord`.
7. Link records back using:
   - `kern:recordsExecutionOf`
   - `kern:evidencesActivity`

## IS / OUGHT / UNKNOWN Rule

- If evidenced, treat as `IS`.
- If intended but not evidenced, treat as `OUGHT`.
- If state cannot be established, treat as `UNKNOWN`.

Never silently promote `OUGHT` to `IS`.

## Corrected Worked Example (Kernel-Aligned)

```turtle
@prefix kern: <https://ontology.engender.co.za/kernel#> .
@prefix ex:   <https://example.org/project/> .

ex:prog1 a kern:ProgramPlan ;
  kern:hasSubPlan ex:ws1 .

ex:ws1 a kern:WorkstreamPlan ;
  kern:hasSubPlan ex:wp1 .

ex:wp1 a kern:WorkPackagePlan ;
  kern:hasSubPlan ex:task1, ex:task2 .

ex:cp1 a kern:CheckpointSpecification .

ex:task1 a kern:TaskSpecification ;
  kern:hasValidationSpecification ex:val1 .

ex:task2 a kern:TaskSpecification ;
  kern:hasValidationSpecification ex:val2 .

ex:dep1 a kern:DependencyRelation ;
  kern:dependencySource ex:task1 ;
  kern:dependencyTarget ex:task2 ;
  kern:hasDependencyKind kern:PredecessorDependency .

ex:agent1 a kern:HumanAgent .
ex:role1 a kern:ResponsibleRole .

ex:ra1 a kern:RoleAssignment ;
  kern:assignsAgent ex:agent1 ;
  kern:assignsRole ex:role1 ;
  kern:assignmentScopePlan ex:task1 .

ex:val1 a kern:ValidationSpecification ;
  kern:validationMethod "python -m unittest tests.test_bootstrap_validate -v" ;
  kern:passCondition "exit code 0" ;
  kern:expectsEvidenceRecord ex:rec1 .

ex:act1 a kern:TaskExecutionActivity .

ex:rec1 a kern:TaskExecutionRecord ;
  kern:recordsExecutionOf ex:task1 ;
  kern:evidencesActivity ex:act1 .
```

## Review Checklist

- Does each object have one primary kind?
- Are plan, activity, and record separated?
- Are dependencies explicit via dependency relations?
- Are roles explicit as role-assignment records?
- Are validation specifications explicit and separate from evidence?
- Are IS/OUGHT/UNKNOWN states explicit?
- Is any prose being treated as authority or execution truth?

## Final Note

If representation requires contextual guessing, the project is not correctly
instantiated against the kernel.


## Merged Into

- `specs/kernel_project_execution_profile_v1.md`
- `schemas/kernel_project_bundle.schema.json`
- `schemas/kernel_project_validation_rules_v1.json`
- `tools/validate_kernel_project_bundle.py`
