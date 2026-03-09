# Kernel PM Audit 2026-03-08

Status: DRAFT
Owner: Codex
Date: 2026-03-08
Basis:
- `specs/kernel_project_execution_profile_v1.md`
- `bootstrap/` execution-plane controls and ledgers

## Executive Summary

The new kernel project-management method is partially implemented and already
active for forward work after cutover `C0`.

What is clearly in place:
- bundle-first authority for forward PM records is documented and active
- kernel PM schema, validation rules, validator, and CSV projector exist
- bridge ledgers remain consistent and validate cleanly
- cutover control documents exist
- progress through `P2-003` / `EP-29` is complete and verified
- the open frontier is defined as `P2-004` to `P2-006`

What is not complete yet:
- the full execution-profile object model is not surfaced operationally
- management views are only implemented for plan, task, and evidence subsets
- documentation has drifted in several places and no longer matches ledger truth
- user journeys for forward bundle-first operations are only partially explicit

## Validation Performed

On 2026-03-08 the following commands passed:

```bash
python tools/validate_kernel_project_bundle.py --bundle bootstrap/kernel_pm/bundles/open_frontier_kernel_project_bundle_v1.json
python tools/bootstrap_validate.py
```

Observed current validated state:
- tasks: 112 rows, `109 DONE`, `3 TO_DO`
- artifacts: 147 rows, `131 DONE`, `16 VERIFIED`
- evidence rows: 29 rows, `26 VERIFIED`, `3 TO_DO`
- open forward tasks: `TASK-30.1`, `TASK-31.1`, `TASK-32.1`
- open forward evidence rows: `EP-30`, `EP-31`, `EP-32`

## Reconstructed Progress

### Confirmed Done

1. Legacy bootstrap execution discipline is fully established:
   `phase1_plan_items.csv`, `task_ledger.csv`, `evidence_register.csv`,
   `artifact_registry.csv`, manifests, and archive structure all exist and pass
   validation.

2. Planning migration and cutover work is already done:
   - planning target operating model added
   - plan manifest added
   - active/reference/archive/program folder model added
   - archive placement normalized
   - cutover snapshot, transition, and authority-switch docs added

3. Kernel PM method scaffolding is in place:
   - execution profile spec exists in [kernel_project_execution_profile_v1.md](C:\Users\PaulWeber\Documents\BB1\specs\kernel_project_execution_profile_v1.md)
   - schema exists in [kernel_project_bundle.schema.json](C:\Users\PaulWeber\Documents\BB1\schemas\kernel_project_bundle.schema.json)
   - rules exist in [kernel_project_validation_rules_v1.json](C:\Users\PaulWeber\Documents\BB1\schemas\kernel_project_validation_rules_v1.json)
   - validator exists in [validate_kernel_project_bundle.py](C:\Users\PaulWeber\Documents\BB1\tools\validate_kernel_project_bundle.py)
   - projector exists in [project_kernel_bundle_to_csv.py](C:\Users\PaulWeber\Documents\BB1\tools\project_kernel_bundle_to_csv.py)

4. Forward PM authority has already switched:
   - [kernel_pm_authority_switch_policy_v1.md](C:\Users\PaulWeber\Documents\BB1\bootstrap\plans\active\kernel_pm_authority_switch_policy_v1.md)
   - [cutover_execution_transition_plan_v1.md](C:\Users\PaulWeber\Documents\BB1\bootstrap\plans\active\cutover_execution_transition_plan_v1.md)
   - [README.md](C:\Users\PaulWeber\Documents\BB1\bootstrap\README.md)

5. Completed program progress through the successor lanes is clear:
   - `P1-001` through `P1-026`: done
   - `P2-001`: done, `EP-27` verified
   - `P2-002`: done, `EP-28` verified
   - `P2-003`: done, `EP-29` verified

### Confirmed Current Frontier

Forward open work is now:
- `P2-004` Runtime 3 minimum viable tenant runtime
- `P2-005` Boundary objects and load discipline closure
- `P2-006` First complex vertical slice proof

Their current task/evidence entry points are:
- `TASK-30.1` -> `EP-30`
- `TASK-31.1` -> `EP-31`
- `TASK-32.1` -> `EP-32`

This is represented in:
- [open_frontier_kernel_project_bundle_v1.json](C:\Users\PaulWeber\Documents\BB1\bootstrap\kernel_pm\bundles\open_frontier_kernel_project_bundle_v1.json)
- [phase1_plan_items.csv](C:\Users\PaulWeber\Documents\BB1\bootstrap\plans\phase1_plan_items.csv)
- [task_ledger.csv](C:\Users\PaulWeber\Documents\BB1\bootstrap\bridge\task_ledger.csv)
- [evidence_register.csv](C:\Users\PaulWeber\Documents\BB1\bootstrap\bridge\evidence_register.csv)

### Still To Do

1. Decompose `WS-04`, `WS-05`, and `WS-06` beyond the single decomposition task
   currently recorded for each workstream.

2. Decide whether the full kernel profile is now the operational source of truth
   for all PM object classes, or only for the forward plan/task/evidence subset.

3. Add missing operational surfaces for the profile object classes that are
   named in the spec but not yet represented in repo workflows.

4. Repair documentation drift so narrative control docs match the ledgers and
   bundle state.

## Assessment Against Requested Questions

### 1. Do we have all the ledgers we need?

Answer: No, not for the full method described by the execution profile.

What we do have:
- plan items
- tasks
- evidence
- artifacts
- milestones
- work packages
- traceability map
- plans manifest
- kernel PM bundle
- kernel PM projections for plan/task/evidence

What is still missing for the full profile:
- checkpoint ledger or projection
- task execution activity / task execution record ledger or projection
- role-assignment view or ledger
- risk register
- issue register
- mitigation register
- change-request register
- impact-assessment register

Why this conclusion is justified:
- the profile explicitly includes `CheckpointSpecification`,
  `TaskExecutionActivity`, `TaskExecutionRecord`, `CheckpointRecord`,
  `RiskRecord`, `IssueRecord`, `MitigationPlan`, `ChangeRequest`, and
  `ImpactAssessment` in
  [kernel_project_execution_profile_v1.md](C:\Users\PaulWeber\Documents\BB1\specs\kernel_project_execution_profile_v1.md#L28)
- the current projector only emits `phase2_plan_items_projection.csv`,
  `task_ledger_projection.csv`, and `evidence_register_projection.csv` from
  workstream, task, dependency, validation, and evidence objects in
  [project_kernel_bundle_to_csv.py](C:\Users\PaulWeber\Documents\BB1\tools\project_kernel_bundle_to_csv.py#L38)

Practical interpretation:
- for the currently open frontier, the repo has enough ledgers to continue
- for the full kernel PM method, the ledger set is incomplete

### 2. Do we understand all the project-management jobs we need to do and do we have the tooling?

Answer: Partially.

Jobs that are understood and tool-supported:
- define bundle objects for forward work
- validate bundle shape and relation rules
- project forward bundle into bridge CSV views
- validate bootstrap ledgers and planning manifests
- track plan/task/evidence/artifact closure
- archive and classify planning documents

Jobs that are understood conceptually but not fully operationalized:
- role assignment maintenance
- checkpoint definition and checkpoint closure
- recording actual execution activity separately from task specification
- reconciling risk, issue, mitigation, change, and impact workflows
- maintaining work-package state so it reflects actual workstream completion

Jobs that are still missing clear tooling:
- authoring workflow for new bundle records beyond manual JSON editing
- dedicated tooling for risk/issue/change objects
- dedicated views for execution records and checkpoint records
- operator tooling for role-assignment inspection and update

Important nuance:
- the method is strong on validation
- it is weaker on authoring ergonomics and operator workflows

### 3. Do we have all the management views we need?

Answer: No.

Views that exist:
- plan index / orientation
- active plan control
- plan item list
- task ledger
- evidence register
- artifact registry
- milestone manifest
- work-package manifest
- traceability map
- daily snapshot
- kernel PM projections for forward plan/task/evidence

Views missing or weak:
- role assignment view
- dependency view across all forward work
- checkpoint view
- execution-history view
- risk / issue / mitigation / change / impact views
- unified forward-frontier dashboard that clearly distinguishes authoritative
  bundle state from bridge CSV state

Important drift problem:
- the work-package view is not being maintained consistently; `WP-09` to
  `WP-12` are still `PLANNED` even though `M3` and `P2-003` are already marked
  done in [phase2_work_packages.csv](C:\Users\PaulWeber\Documents\BB1\bootstrap\plans\manifests\phase2_work_packages.csv#L10)

### 4. Are all the guides and READMEs up to date?

Answer: No.

Confirmed documentation drift:
- [phase1_execution_plan.md](C:\Users\PaulWeber\Documents\BB1\bootstrap\plans\phase1_execution_plan.md#L70)
  still says `EP-28` is only ready for verification and `EP-29` remains open,
  but the ledgers show both verified.
- [post_p1_026_full_solution_program_plan_v1.md](C:\Users\PaulWeber\Documents\BB1\bootstrap\plans\programs\post_p1_026_full_solution_program_plan_v1.md#L74)
  still says `P2-002` and `P2-003` are active and `EP-29` remains gated.
- [phase2_work_packages.csv](C:\Users\PaulWeber\Documents\BB1\bootstrap\plans\manifests\phase2_work_packages.csv#L10)
  still leaves all `WS-03` work packages as `PLANNED` although the milestone is
  done.
- [daily_state_snapshot.md](C:\Users\PaulWeber\Documents\BB1\bootstrap\reports\daily_state_snapshot.md#L10)
  is stale relative to current validated counts and recommends archiving
  bootstrap ledgers into a permanent ops platform at
  [daily_state_snapshot.md](C:\Users\PaulWeber\Documents\BB1\bootstrap\reports\daily_state_snapshot.md#L152),
  which does not match the current bundle-first bridge state.
- folder README stubs in
  [active README](C:\Users\PaulWeber\Documents\BB1\bootstrap\plans\active\README.md#L7),
  [programs README](C:\Users\PaulWeber\Documents\BB1\bootstrap\plans\programs\README.md#L7),
  and [reference README](C:\Users\PaulWeber\Documents\BB1\bootstrap\plans\reference\README.md#L7)
  still say files remain in `bootstrap/plans/`, but files have already been
  moved into those folders.

### 5. Are we clear on the project-management user journeys needed?

Answer: Only partially.

Journeys that are reasonably clear today:
- inspect current planning state
- validate current ledgers
- validate current bundle
- project bundle into CSV bridge views
- add or update bridge records for legacy/historical work
- archive superseded planning docs

Journeys that are not yet fully clear or not fully documented:
- start a brand new forward workstream in bundle-first mode
- add work packages and decompose them into executable tasks
- assign people or systems to scopes in an auditable way
- record execution activity and execution records after work happens
- manage checkpoints and checkpoint closure
- raise and resolve risks, issues, and changes
- decide when the bundle is authoritative versus when a CSV view may be edited

Conclusion:
- the repo has a control model
- it does not yet have a fully documented operator playbook

## Key Findings

### Finding 1: Control docs are behind ledger truth

This is the highest-confidence problem because it creates confusion about what
is complete versus what is open.

Affected files:
- [phase1_execution_plan.md](C:\Users\PaulWeber\Documents\BB1\bootstrap\plans\phase1_execution_plan.md#L70)
- [post_p1_026_full_solution_program_plan_v1.md](C:\Users\PaulWeber\Documents\BB1\bootstrap\plans\programs\post_p1_026_full_solution_program_plan_v1.md#L74)
- [phase2_work_packages.csv](C:\Users\PaulWeber\Documents\BB1\bootstrap\plans\manifests\phase2_work_packages.csv#L10)
- [daily_state_snapshot.md](C:\Users\PaulWeber\Documents\BB1\bootstrap\reports\daily_state_snapshot.md#L10)

### Finding 2: The full kernel PM object model is declared but not operationalized

The spec names a richer PM ontology than the repo currently operates.

Evidence:
- full kind set in
  [kernel_project_execution_profile_v1.md](C:\Users\PaulWeber\Documents\BB1\specs\kernel_project_execution_profile_v1.md#L28)
- limited projection surfaces in
  [project_kernel_bundle_to_csv.py](C:\Users\PaulWeber\Documents\BB1\tools\project_kernel_bundle_to_csv.py#L143)

Impact:
- the repo can plan forward work
- it cannot yet manage the full profile as a first-class operating system

### Finding 3: Work-package state is not reliable enough as a management view

The work-package manifest is intended as an execution control, but at least one
closed workstream still has `PLANNED` work-package rows.

Evidence:
- `WP-09` through `WP-12` are `PLANNED` in
  [phase2_work_packages.csv](C:\Users\PaulWeber\Documents\BB1\bootstrap\plans\manifests\phase2_work_packages.csv#L10)
- `P2-003` and `EP-29` are `DONE` / `VERIFIED` in the validated ledgers

Impact:
- milestone/work-package reporting can mislead planning and review decisions

### Finding 4: Forward work is only decomposed one step deep

For `P2-004` to `P2-006`, the current task layer only contains one decomposition
task per workstream.

Impact:
- work packages exist conceptually
- they are not yet decomposed into executable implementation tasks
- this limits both management visibility and operational readiness

## Recommended Next Actions

1. Fix documentation drift first so the control story matches the validated
   data.
2. Decide the intended scope of kernel PM v1:
   bridge subset only, or full profile operations.
3. If full profile operations are intended, add missing ledgers or projections
   for checkpoints, execution records, role assignments, risks, issues,
   mitigations, changes, and impacts.
4. Decompose `WS-04`, `WS-05`, and `WS-06` from one placeholder task each into
   actual executable task sets aligned to `WP-13` through `WP-24`.
5. Write a forward-operations guide covering these user journeys:
   create bundle object, validate, project, reconcile, execute, evidence, close,
   archive.

## Bottom Line

The repo is not starting from zero.

The new method has already crossed the hard part: cutover happened, validation
exists, and forward authority has moved into kernel PM bundles for the open
frontier.

The remaining work is not foundational reinvention. It is:
- completing the operational surface area of the full method
- cleaning up documentation drift
- decomposing the remaining open work into actionable records
