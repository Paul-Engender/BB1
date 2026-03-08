#!/usr/bin/env python3
"""Generate daily bootstrap state snapshot from ledgers."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

PHASE0_EVIDENCE_IDS = {"EP-01", "EP-02", "EP-03", "EP-04", "EP-05"}


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _task_lines(rows: list[dict[str, str]], status: str) -> list[str]:
    selected = [r for r in rows if (r.get("status") or "").strip() == status]
    return [f"- **{r.get('task_id', '').strip()}**: {r.get('task_name', '').strip()}" for r in selected]


def generate_snapshot(task_rows: list[dict[str, str]], artifact_rows: list[dict[str, str]], evidence_rows: list[dict[str, str]]) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    task_counts = Counter((r.get("status") or "").strip() for r in task_rows)
    artifact_counts = Counter((r.get("validation_status") or "").strip() for r in artifact_rows)
    evidence_counts = Counter((r.get("status") or "").strip() for r in evidence_rows)

    done_lines = _task_lines(task_rows, "DONE")
    active_lines = _task_lines(task_rows, "IN_PROGRESS")
    blocked_lines = _task_lines(task_rows, "BLOCKED")
    completed_lines = _task_lines(task_rows, "COMPLETED")

    evidence_table = ["| Evidence Row | Status | Owner | Validation Evidence |", "| --- | --- | --- | --- |"]
    for row in evidence_rows:
        evid = (row.get("evidence_row_id") or row.get("evidence_id") or "").strip()
        status = (row.get("status") or "").strip() or "UNKNOWN"
        owner = (row.get("verification_owner") or "").strip() or "-"
        ve = (row.get("validation_evidence") or "").strip() or "-"
        evidence_table.append(f"| {evid} | {status} | {owner} | {ve} |")

    phase0_rows = [
        r
        for r in evidence_rows
        if ((r.get("evidence_row_id") or r.get("evidence_id") or "").strip() in PHASE0_EVIDENCE_IDS)
    ]
    phase0_closed = all((r.get("status") or "").strip() == "VERIFIED" for r in phase0_rows)
    phase0_status = "CLOSED" if phase0_closed else "OPEN"

    def _or_none(lines: list[str]) -> list[str]:
        return lines if lines else ["*(None)*"]

    content = [
        "# Daily State Snapshot",
        "",
        f"*Generated on: {now}*",
        "",
        "---",
        "",
        "## Summary",
        "",
        f"- Phase-0 Gate: **{phase0_status}**",
        f"- Task Status Counts: {dict(task_counts)}",
        f"- Artifact Validation Counts: {dict(artifact_counts)}",
        f"- Evidence Status Counts: {dict(evidence_counts)}",
        "",
        "## DONE Tasks",
        "",
        *_or_none(done_lines),
        "",
        "## Active Tasks",
        "",
        *_or_none(active_lines),
        "",
        "## Blocked Tasks",
        "",
        *_or_none(blocked_lines),
        "",
        "## Completed (Awaiting Done Criteria)",
        "",
        *_or_none(completed_lines),
        "",
        "## Evidence Pack Status",
        "",
        *evidence_table,
        "",
        "## Recommended Next Action",
        "",
    ]

    open_tasks = [
        r for r in task_rows
        if (r.get("status") or "").strip() in {"TO_DO", "IN_PROGRESS", "BLOCKED", "COMPLETED"}
    ]

    if open_tasks:
        content.append("- Execute open task backlog with strict validation methods, starting from the highest-priority TO_DO item.")
    elif phase0_closed:
        content.append("- Archive bootstrap ledgers and start transition import into permanent ops platform.")
    else:
        content.append("- Move all non-VERIFIED evidence rows to VERIFIED with reproducible validation evidence and artifact integrity proofs.")

    content.extend(["", "## Notes", "", "- Snapshot generated from bootstrap ledgers only (no manual overrides).", ""])
    return "\n".join(content)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate daily snapshot from bootstrap ledgers")
    parser.add_argument("--task-ledger", default="bootstrap/task_ledger.csv")
    parser.add_argument("--artifact-registry", default="bootstrap/artifact_registry.csv")
    parser.add_argument("--evidence-register", default="bootstrap/evidence_register.csv")
    parser.add_argument("--output", default="bootstrap/reports/daily_state_snapshot.md")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    task_rows = _read_csv(repo_root / args.task_ledger)
    artifact_rows = _read_csv(repo_root / args.artifact_registry)
    evidence_rows = _read_csv(repo_root / args.evidence_register)

    snapshot = generate_snapshot(task_rows, artifact_rows, evidence_rows)
    out = repo_root / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(snapshot, encoding="utf-8-sig")
    print(f"Wrote snapshot: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

