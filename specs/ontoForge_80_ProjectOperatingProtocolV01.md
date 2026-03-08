# Project Operating Protocol

### Purpose

This protocol defines the operational rules for managing work, updating project artifacts, and reporting progress during project execution. It operates strictly on the implementation and coordination plane. It does not create or modify binding project governance contracts.

### Scope

Applies to:

- Project plans

- Design and architecture documents

- Sprint/cycle execution

- Operational communication

Note: This protocol does not change the meaning or authority of canonical governance documents.

### 1. IS vs. OUGHT Discipline (Anti-Ambiguity Rule)

This project distinguishes explicitly between:

- IS: A proven operational state (verified by tangible evidence).

- OUGHT: An intended or planned state (a target).

Hard Rules:

- Do not assert an IS-state without evidence.

- If something is unknown, explicitly state UNKNOWN.

- If something is planned (a target), label it OUGHT or TARGET.

Examples:

- “/docs/specs exists” is an IS-claim and requires evidence (e.g., repo tree listing, commit hash, CI check).

- “/docs/specs will be the canonical location” is an OUGHT-claim (a convention) and must be implemented via a separate work item.

Protocol Consequence: Any work item that references a file path or system state MUST state whether it is an IS (exists now) or an OUGHT (to be created). If OUGHT, include a dependency that creates it and a DONE check that proves it exists.

### 2. Document Classes

Three distinct document classes exist within this project:

#### A. Canonical Governance Documents

- Examples: Core Security Policy, System Architecture Specification, Decisions Register.

- Properties: Binding meaning, authoritative for system governance, heavily controlled modification.

- Update Rule: Propose → Review → Decision → Canonical Update → Version Increment.

- (A canonical document cannot change through casual project-plan edits).

#### B. Directional Design Documents

- Examples: Product specification drafts, architecture exploration documents.

- Properties: Non-binding, may evolve dynamically during the design phase.

- Update Rule: Proposal → Review → Update → Version Increment.

- (A decision record becomes required only when the design becomes binding architecture).

#### C. Implementation-Plane Documents

- Examples: Project plans, sprint backlogs, operational runbooks.

- Properties: Used for operational coordination, frequently updated, holds no governance authority.

- Update Rule: Working Update → Acknowledgement → Commit.

### 3. Change Record Protocol

Every modification to Canonical or Design documents should be accompanied by a minimal change record.

- Change Type: Proposal, Update, Decision, or Correction.

- Required Fields:

  - Document & Section affected

  - Reason for change

  - Impact Assessment (Governance impact, Architecture impact, Execution impact)

- Status: Pending Review, Accepted, or Rejected.

### 4. Project Communication & Status Protocol

All work reporting must follow a fixed status structure. This structure strictly separates work production from correctness verification.

- DONE: Validated and accepted work.

- COMPLETED: Work finished but not yet validated.

- DID NOT DO: Planned work not executed.

- TO DO: Committed work for the next cycle.

- NEXT RECOMMENDED ACTION: The single best next step to unblock progress.

### 5. Completed vs. Done

#### Completed

- Meaning: The work artifact exists, but correctness has not yet been verified.

- Examples: Code written, schema drafted, UI built, infrastructure provisioned.

- Status Label: COMPLETED

#### Done

- Meaning: Work has passed all explicitly defined validation checks.

- Examples of Validation:

  - Database: Migrations and transactional integrity tests pass.

  - API / Backend: Negative tests and contract tests pass.

  - Release Package: Cryptographic digest verification passes.

  - Frontend: E2E user flows and accessibility checks pass.

- Status Label: DONE

Core Principle: Completed does not equal Done.

Formally: DONE = COMPLETED + VERIFIED + VALIDATED

### 6. Task Validation Rule

Every task must define its validation conditions before execution begins.

- Example Task: Implement secure user authentication.

- Validation Criteria: Invalid token rejection test passes; session timeout test passes; rate-limiting triggers correctly.

A task cannot be marked DONE without passing its predefined validation conditions.

### 7. Decision Protocol

When a proposed change affects system architecture or governance, the following sequence must apply:

Issue → Analysis → Decision → Record in Decisions Register.

Only recorded decisions become binding.

### 8. Sprint Checkpoint Protocol

At the end of each sprint/cycle, the project produces a checkpoint report containing:

- DONE: [List items]

- COMPLETED: [List items awaiting validation]

- DID NOT DO: [List items]

- TO DO: [List items]

- NEXT RECOMMENDED ACTION: [Single focus item]

- RISKS / BLOCKERS: [List items]

(This checkpoint ensures progress reporting never hides the true validation status of a project).
