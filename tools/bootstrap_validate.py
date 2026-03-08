#!/usr/bin/env python3
"""Bootstrap ledger validation and Phase-0 gate checks."""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

TASK_STATUSES = {"TO_DO", "IN_PROGRESS", "BLOCKED", "COMPLETED", "DONE", "DID_NOT_DO"}
ARTIFACT_STATUSES = {"TO_DO", "COMPLETED", "DONE", "VERIFIED", "BLOCKED"}
EVIDENCE_STATUSES = {"TO_DO", "COMPLETED", "DONE", "VERIFIED", "BLOCKED"}
PLAN_ITEM_STATUSES = {"PLANNED", "ACTIVE", "BLOCKED", "DONE", "ARCHIVED"}


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
EXEC_CMD_RE = re.compile(r"^(python|python3|pytest|pwsh|powershell|bash)\b.+")
TASK_ID_RE = re.compile(r"^(BPL|BR|TASK)-[A-Za-z0-9_.-]+$")
BPL_ID_RE = re.compile(r"^BPL-[A-Za-z0-9_.-]+$")
ART_ID_RE = re.compile(r"^ART-[A-Za-z0-9_.-]+$")
EP_ID_RE = re.compile(r"^EP-[A-Za-z0-9_.-]+$")
PLAN_ID_RE = re.compile(r"^P[0-9]+-[0-9]{3}$")
PHASE0_EVIDENCE_IDS = {"EP-01", "EP-02", "EP-03", "EP-04", "EP-05"}



def _split_multi(value: str) -> list[str]:
    value = (value or "").strip()
    if not value:
        return []
    return [p.strip() for p in value.split(";") if p.strip()]


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_plan_items(path: Path) -> tuple[set[str], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if not path.exists():
        return set(), [f"plan items file missing: {path}"], warnings

    rows = _read_csv(path)
    ids: set[str] = set()

    for i, row in enumerate(rows, start=2):
        pid = (row.get("plan_item_id") or "").strip()
        status = (row.get("status") or "").strip()
        title = (row.get("title") or "").strip()

        if not PLAN_ID_RE.match(pid):
            errors.append(f"{path.name}:{i}: invalid plan_item_id '{pid}'")
        if pid in ids:
            errors.append(f"{path.name}:{i}: duplicate plan_item_id '{pid}'")
        ids.add(pid)

        if not title:
            errors.append(f"{path.name}:{i}: title is required")

        if status not in PLAN_ITEM_STATUSES:
            errors.append(f"{path.name}:{i}: invalid status '{status}'")

    return ids, errors, warnings


def _execute_validation_methods(
    task_rows: list[dict[str, str]],
    repo_root: Path,
    mode: str,
) -> tuple[list[str], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    reports: list[str] = []

    if mode == "none":
        return errors, warnings, reports

    for i, row in enumerate(task_rows, start=2):
        tid = (row.get("task_id") or "").strip()
        status = (row.get("status") or "").strip()
        method = (row.get("validation_method") or "").strip()

        if not tid.startswith("TASK-") or status != "DONE":
            continue

        if mode == "dry-run":
            reports.append(f"{tid}: would run `{method}`")
            continue

        completed = subprocess.run(
            method,
            cwd=str(repo_root),
            shell=True,
            capture_output=True,
            text=True,
        )
        if completed.returncode == 0:
            reports.append(f"{tid}: PASS `{method}`")
            continue

        out = (completed.stdout or "").strip()
        err = (completed.stderr or "").strip()
        out_tail = out[-400:] if out else ""
        err_tail = err[-400:] if err else ""
        detail = (
            f"task_ledger.csv:{i}: validation_method failed for {tid} "
            f"(exit={completed.returncode}): `{method}`"
        )
        if out_tail:
            detail += f"\n  stdout_tail: {out_tail}"
        if err_tail:
            detail += f"\n  stderr_tail: {err_tail}"
        errors.append(detail)

    return errors, warnings, reports


def validate(
    task_rows: list[dict[str, str]],
    artifact_rows: list[dict[str, str]],
    evidence_rows: list[dict[str, str]],
    plan_item_ids: set[str],
    repo_root: Path,
    require_phase0_closed: bool,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    task_ids: set[str] = set()
    done_tasks: set[str] = set()

    for i, row in enumerate(task_rows, start=2):
        tid = (row.get("task_id") or "").strip()
        plan_item_id = (row.get("plan_item_id") or "").strip()
        task_name = (row.get("task_name") or "").strip()
        status = (row.get("status") or "").strip()
        notes = (row.get("notes") or "").strip().lower()
        ev_ids = _split_multi(row.get("evidence_row_ids", ""))
        deps = _split_multi(row.get("dependencies", ""))
        outputs = _split_multi(row.get("output_paths", ""))

        if not TASK_ID_RE.match(tid):
            errors.append(f"task_ledger.csv:{i}: invalid task_id '{tid}'")
        if tid in task_ids:
            errors.append(f"task_ledger.csv:{i}: duplicate task_id '{tid}'")
        task_ids.add(tid)

        if not PLAN_ID_RE.match(plan_item_id):
            errors.append(f"task_ledger.csv:{i}: missing or invalid plan_item_id '{plan_item_id}'")
        elif plan_item_id not in plan_item_ids:
            errors.append(f"task_ledger.csv:{i}: plan_item_id '{plan_item_id}' not found in plan index")

        if status not in TASK_STATUSES:
            errors.append(f"task_ledger.csv:{i}: invalid status '{status}'")

        if status == "DONE":
            done_tasks.add(tid)
            if not (row.get("validation_method") or "").strip():
                errors.append(f"task_ledger.csv:{i}: DONE task must include validation_method")
            if not (row.get("validation_evidence") or "").strip():
                errors.append(f"task_ledger.csv:{i}: DONE task must include validation_evidence")
            if "ought" in notes:
                errors.append(f"task_ledger.csv:{i}: DONE task cannot be marked as OUGHT in notes")
            if not outputs:
                errors.append(f"task_ledger.csv:{i}: DONE task must declare at least one output path")
            for output in outputs:
                output_path = repo_root / output
                if not output_path.exists():
                    errors.append(f"task_ledger.csv:{i}: DONE task output path does not exist: '{output}'")

        for dep in deps:
            if dep and not TASK_ID_RE.match(dep):
                errors.append(f"task_ledger.csv:{i}: invalid dependency id '{dep}'")

        # Work Decomposition Protocol constraints for TASK-* rows.
        if tid.startswith("TASK-"):
            bootstrap_task_id = (row.get("bootstrap_task_id") or "").strip()
            if not BPL_ID_RE.match(bootstrap_task_id):
                errors.append(
                    f"task_ledger.csv:{i}: TASK-* rows must include bootstrap_task_id mapped to BPL-*"
                )
            if not ev_ids:
                errors.append(f"task_ledger.csv:{i}: TASK-* rows must include evidence_row_ids")
            if len(deps) > 2:
                errors.append(f"task_ledger.csv:{i}: TASK-* rows may declare at most 2 dependencies")
            if len(outputs) != 1:
                errors.append(f"task_ledger.csv:{i}: TASK-* rows must declare exactly one output path")
            if " and " in task_name.lower():
                errors.append(f"task_ledger.csv:{i}: TASK-* name has mixed intent (contains ' and '): '{task_name}'")
            if status == "DONE":
                validation_method = (row.get("validation_method") or "").strip()
                if not EXEC_CMD_RE.match(validation_method):
                    errors.append(
                        "task_ledger.csv:"
                        f"{i}: DONE TASK-* rows must set validation_method to an executable command "
                        "(e.g., 'python -m unittest ...' or 'pytest ...')"
                    )

    artifact_ids: set[str] = set()
    artifacts_by_task: dict[str, list[dict[str, str]]] = {}

    for i, row in enumerate(artifact_rows, start=2):
        aid = (row.get("artifact_id") or "").strip()
        produced_by = (row.get("produced_by_task_id") or "").strip()
        path_value = (row.get("path") or "").strip()
        integrity_type = (row.get("integrity_type") or "").strip()
        integrity_value = (row.get("integrity_value") or "").strip().lower()
        vstatus = (row.get("validation_status") or "").strip()

        if not ART_ID_RE.match(aid):
            errors.append(f"artifact_registry.csv:{i}: invalid artifact_id '{aid}'")
        if aid in artifact_ids:
            errors.append(f"artifact_registry.csv:{i}: duplicate artifact_id '{aid}'")
        artifact_ids.add(aid)

        if produced_by not in task_ids:
            errors.append(
                f"artifact_registry.csv:{i}: produced_by_task_id '{produced_by}' not found in task ledger"
            )

        if vstatus not in ARTIFACT_STATUSES:
            errors.append(f"artifact_registry.csv:{i}: invalid validation_status '{vstatus}'")

        if integrity_type == "SHA256":
            if not SHA256_RE.match(integrity_value):
                errors.append(
                    f"artifact_registry.csv:{i}: SHA256 integrity_value must be 64 lowercase hex chars"
                )
        elif integrity_type != "NONE":
            errors.append(f"artifact_registry.csv:{i}: integrity_type must be SHA256 or NONE")

        if vstatus in {"DONE", "VERIFIED"}:
            if not (row.get("validation_evidence") or "").strip():
                errors.append(
                    f"artifact_registry.csv:{i}: {vstatus} artifact must include validation_evidence"
                )
            if integrity_type != "SHA256" or not SHA256_RE.match(integrity_value):
                errors.append(
                    f"artifact_registry.csv:{i}: {vstatus} artifact must include valid SHA256 hash"
                )

        if path_value:
            file_path = repo_root / path_value
            if file_path.exists() and integrity_type == "SHA256" and SHA256_RE.match(integrity_value):
                actual_hash = _file_sha256(file_path)
                if actual_hash != integrity_value:
                    errors.append(
                        f"artifact_registry.csv:{i}: integrity hash mismatch for '{path_value}' (expected {integrity_value}, got {actual_hash})"
                    )
            elif vstatus in {"DONE", "VERIFIED"}:
                warnings.append(f"artifact_registry.csv:{i}: path '{path_value}' does not exist in repo")

        artifacts_by_task.setdefault(produced_by, []).append(row)

    evidence_ids: set[str] = set()

    for i, row in enumerate(evidence_rows, start=2):
        evid = (row.get("evidence_row_id") or row.get("evidence_id") or "").strip()
        status = (row.get("status") or "").strip()
        source_tasks = _split_multi(row.get("source_task_ids", ""))

        if not EP_ID_RE.match(evid):
            errors.append(f"evidence_register.csv:{i}: invalid evidence_row_id '{evid}'")
        if evid in evidence_ids:
            errors.append(f"evidence_register.csv:{i}: duplicate evidence_row_id '{evid}'")
        evidence_ids.add(evid)

        if status not in EVIDENCE_STATUSES:
            errors.append(f"evidence_register.csv:{i}: invalid status '{status}'")

        if not source_tasks:
            errors.append(f"evidence_register.csv:{i}: source_task_ids cannot be empty")

        for tid in source_tasks:
            if tid not in task_ids:
                errors.append(f"evidence_register.csv:{i}: source task '{tid}' missing from task ledger")

        if status in {"DONE", "VERIFIED"} and not (row.get("validation_evidence") or "").strip():
            errors.append(f"evidence_register.csv:{i}: {status} row must include validation_evidence")

        if status == "VERIFIED":
            for tid in source_tasks:
                if tid not in done_tasks:
                    errors.append(
                        f"evidence_register.csv:{i}: VERIFIED row requires source task '{tid}' to be DONE"
                    )
                related_artifacts = artifacts_by_task.get(tid, [])
                if not related_artifacts:
                    errors.append(
                        f"evidence_register.csv:{i}: VERIFIED row source task '{tid}' has no artifacts recorded"
                    )
                for art in related_artifacts:
                    if (art.get("integrity_type") or "").strip() != "SHA256" or not SHA256_RE.match(
                        (art.get("integrity_value") or "").strip().lower()
                    ):
                        errors.append(
                            f"evidence_register.csv:{i}: VERIFIED row source task '{tid}' has artifact without valid SHA256 integrity"
                        )

    # Governance rule: completed implementation work must record artifact hashes.
    for tid in done_tasks:
        related = artifacts_by_task.get(tid, [])
        if not related:
            warnings.append(f"DONE task '{tid}' has no artifact rows in artifact_registry.csv")
            continue
        for art in related:
            if (art.get("integrity_type") or "").strip() != "SHA256" or not SHA256_RE.match(
                (art.get("integrity_value") or "").strip().lower()
            ):
                errors.append(f"DONE task '{tid}' has artifact without valid SHA256 integrity hash")

    if require_phase0_closed:
        not_verified = [
            (row.get("evidence_row_id") or row.get("evidence_id") or "").strip()
            for row in evidence_rows
            if (row.get("evidence_row_id") or row.get("evidence_id") or "").strip() in PHASE0_EVIDENCE_IDS
            and (row.get("status") or "").strip() != "VERIFIED"
        ]
        if not_verified:
            errors.append(
                "Phase-0 gate not closed: all evidence rows must be VERIFIED. "
                + f"Non-VERIFIED rows: {', '.join(not_verified)}"
            )

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate bootstrap ledgers and Phase-0 gate rules")
    parser.add_argument("--task-ledger", default="bootstrap/task_ledger.csv")
    parser.add_argument("--artifact-registry", default="bootstrap/artifact_registry.csv")
    parser.add_argument("--evidence-register", default="bootstrap/evidence_register.csv")
    parser.add_argument("--plan-items", default="bootstrap/plans/phase1_plan_items.csv")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--require-phase0-closed", action="store_true")
    parser.add_argument(
        "--execute-validation-methods",
        choices=("none", "dry-run", "strict"),
        default="none",
        help="Execute validation_method commands for DONE TASK-* rows.",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    task_rows = _read_csv(repo_root / args.task_ledger)
    artifact_rows = _read_csv(repo_root / args.artifact_registry)
    evidence_rows = _read_csv(repo_root / args.evidence_register)
    plan_item_ids, plan_errors, plan_warnings = _load_plan_items(repo_root / args.plan_items)

    errors, warnings = validate(
        task_rows,
        artifact_rows,
        evidence_rows,
        plan_item_ids,
        repo_root,
        args.require_phase0_closed,
    )

    errors = plan_errors + errors
    warnings = plan_warnings + warnings
    exec_errors, exec_warnings, exec_reports = _execute_validation_methods(
        task_rows, repo_root, args.execute_validation_methods
    )
    errors.extend(exec_errors)
    warnings.extend(exec_warnings)

    task_counts = Counter((r.get("status") or "").strip() for r in task_rows)
    art_counts = Counter((r.get("validation_status") or "").strip() for r in artifact_rows)
    ev_counts = Counter((r.get("status") or "").strip() for r in evidence_rows)

    print("Bootstrap validation summary")
    print(f"- tasks: {len(task_rows)} rows, status counts: {dict(task_counts)}")
    print(f"- artifacts: {len(artifact_rows)} rows, status counts: {dict(art_counts)}")
    print(f"- evidence: {len(evidence_rows)} rows, status counts: {dict(ev_counts)}")
    print(f"- plan items: {len(plan_item_ids)}")
    print(f"- validation method execution mode: {args.execute_validation_methods}")

    if exec_reports:
        print("Validation method run summary:")
        for line in exec_reports:
            print(f"- {line}")

    for warning in warnings:
        print(f"WARNING: {warning}")

    if errors:
        print("\nValidation errors:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("All bootstrap validations passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

