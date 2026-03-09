# Wave-2 Migration Delta Register v1

Status: IS
Owner: paul
Plan Item: P1-010
Task: TASK-10.2
Date: 2026-03-06

## Purpose

Capture wave-2 deltas based on wave-1 results and remaining operational hardening needs.

## Delta Register (Wave-2)

| Delta ID | Wave-1 Residual | Wave-2 Target State | Impact | Action |
| --- | --- | --- | --- | --- |
| W2-D01 | Strict validator can hit transient test IO contention | Stable strict execution policy with robust command selection | High | Use suite-level deterministic commands for loader/packager checks |
| W2-D02 | Recursive validator calls can cause timeout | Non-recursive validation methods for matrix/report tasks | High | Standardize `python tools/bootstrap_validate.py` for validator-owned tasks |
| W2-D03 | Snapshot recommendation previously ignored open backlog | Snapshot recommendations always prioritize open backlog execution | Medium | Preserve execution-aware recommendation logic |
| W2-D04 | New phase evidence rows can interfere with phase-0 gate semantics | Phase-0 gate explicitly scoped to EP-01..EP-05 | High | Keep phase-scope invariant under all future EP additions |
| W2-D05 | Governance-vs-operational mirror distinction can drift | Canonical source rule remains explicit in protocols/index | Medium | Keep canonical source headers and synchronize on changes |

## Outcome for Wave-2

Wave-2 deltas focus on repeatability hardening, ensuring migration can scale without introducing control regression.
