# Wave-2 Spec Contract Validation Matrix v1

Status: IS
Owner: paul
Plan Item: P1-010
Task: TASK-10.3
Date: 2026-03-06

## Purpose

Define executable contract checks for wave-2 deltas and closure criteria.

## Validation Matrix

| Matrix ID | Contract/Delta | Command | Expected Result | Evidence Artifact |
| --- | --- | --- | --- | --- |
| W2-M01 | W2-D01 strict stability | `python tools/bootstrap_validate.py --execute-validation-methods strict` | strict mode passes without persistent command failures | validator output + task ledger |
| W2-M02 | W2-D02 non-recursive validator calls | `python tools/bootstrap_validate.py` | no validator recursion timeout conditions | task ledger command set |
| W2-M03 | W2-D03 snapshot backlog priority | `python tools/bootstrap_snapshot.py` | recommendation matches open/closed backlog state | daily state snapshot |
| W2-M04 | W2-D04 phase gate scoping | `python tools/bootstrap_validate.py --require-phase0-closed --execute-validation-methods strict` | phase-0 remains closed when later-phase EP rows exist | validator output + evidence register |
| W2-M05 | W2-D05 canonical source integrity | `python tools/bootstrap_validate.py` | protocol/plan control files remain internally consistent | protocols + plan index + validator pass |

## Closure Rule

Wave-2 closes when W2-M01..W2-M05 are reproducibly satisfiable with hash-bound artifacts.
