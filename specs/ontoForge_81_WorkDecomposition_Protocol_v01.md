# Work Decomposition Protocol

### Purpose

Define the “agent-executable” decomposition level so bounded-context agents can complete tasks within their attention and reliability constraints.

### Decomposition Rules

Decompose work iteratively until each task meets the following criteria:

- Single Output: Has exactly one primary deliverable (one artifact).

- Clear I/O: Has explicitly defined inputs and outputs.

- Bounded Dependencies: Relies on $\le2$ upstream artifacts.

- Verifiable: Has machine-checkable DONE criteria.

- Singular Intent: Contains no mixed intent (e.g., architectural decision-making and code implementation must be separated into distinct tasks).

### Sizing Heuristics

If any of the following are true, the task is too large and must be split:

- The task requires more than 10–15 lines to specify unambiguously.

- The validation/testing touches more than one subsystem boundary.

- The acceptance criteria cannot be written without requiring additional system design. (If so, split out a preceding "design" task).

### Work Item Template (Agent-Executable)

Use the following structure for all agent task tickets:

- Task: [Verb] + [Object].

- Context: 2–4 lines explaining the "why." Cite canonical documentation or architectural sections if needed.

- Inputs: Specific files, record types, or fixtures required to start.

- Outputs: Exact artifacts produced, including specific filenames and file paths.

- Constraints: Hard boundaries and restrictions the agent must respect (e.g., fail-closed requirements, performance limits, architectural invariants, forbidden actions).

- Dependencies: At most two upstream artifacts required before this task can begin.

- Non-goals: Explicit exclusions (what the agent should not do or worry about).

- Validation (DONE): Specific commands, test scripts, and the exact expected outcomes required to prove completion.

### Status Mapping

- COMPLETED: The outputs exist, but validation has not yet passed or been run.

- DONE: Validation has successfully passed, and evidence is available (e.g., CI logs, test outputs, cryptographic hashes).
