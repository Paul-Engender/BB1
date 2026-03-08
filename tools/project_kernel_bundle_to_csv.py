#!/usr/bin/env python3
"""Project kernel project bundle objects into CSV view surfaces."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _refs(obj: dict[str, Any], predicate: str) -> list[str]:
    refs = obj.get("refs") or []
    out: list[str] = []
    for ref in refs:
        if isinstance(ref, dict) and ref.get("predicate") == predicate and isinstance(ref.get("target_id"), str):
            out.append(ref["target_id"])
    return out


def _status_map_plan(status: str) -> str:
    return {"IS": "DONE", "OUGHT": "PLANNED", "UNKNOWN": "BLOCKED"}.get(status, "BLOCKED")


def _status_map_task(status: str) -> str:
    return {"IS": "DONE", "OUGHT": "TO_DO", "UNKNOWN": "BLOCKED"}.get(status, "BLOCKED")


def _status_map_evidence(status: str) -> str:
    return {"IS": "VERIFIED", "OUGHT": "TO_DO", "UNKNOWN": "BLOCKED"}.get(status, "BLOCKED")


def project_bundle(bundle: dict[str, Any], out_dir: Path) -> list[Path]:
    objects = bundle.get("objects", [])
    by_id: dict[str, dict[str, Any]] = {
        obj["id"]: obj
        for obj in objects
        if isinstance(obj, dict) and isinstance(obj.get("id"), str)
    }

    dependencies_by_source: dict[str, list[str]] = {}
    for obj in objects:
        if obj.get("kind") != "DependencyRelation":
            continue
        for source_id in _refs(obj, "dependencySource"):
            target_ids = _refs(obj, "dependencyTarget")
            if not target_ids:
                continue
            dependencies_by_source.setdefault(source_id, []).extend(target_ids)

    evidence_to_tasks: dict[str, list[str]] = {}

    plan_rows: list[dict[str, str]] = []
    task_rows: list[dict[str, str]] = []
    evidence_rows: list[dict[str, str]] = []

    for obj in objects:
        kind = obj.get("kind")
        status = str(obj.get("status", "UNKNOWN"))
        attrs = obj.get("attributes") if isinstance(obj.get("attributes"), dict) else {}

        if kind == "WorkstreamPlan" and isinstance(attrs.get("plan_item_id"), str):
            plan_rows.append(
                {
                    "plan_item_id": str(attrs.get("plan_item_id", "")),
                    "title": str(attrs.get("title", "")),
                    "status": _status_map_plan(status),
                    "owner": str(attrs.get("owner", "")),
                    "notes": str(attrs.get("notes", "")),
                    "source_object_id": str(obj.get("id", "")),
                }
            )

        if kind == "TaskSpecification" and isinstance(attrs.get("task_id"), str):
            obj_id = str(obj.get("id", ""))
            task_id = str(attrs.get("task_id", ""))
            validation_ids = _refs(obj, "hasValidationSpecification")
            validation = by_id.get(validation_ids[0]) if validation_ids else None
            validation_attrs = (
                validation.get("attributes")
                if isinstance(validation, dict) and isinstance(validation.get("attributes"), dict)
                else {}
            )
            evidence_targets = _refs(validation, "expectsEvidenceRecord") if isinstance(validation, dict) else []
            evidence_row_ids: list[str] = []
            for evidence_id in evidence_targets:
                ev_obj = by_id.get(evidence_id)
                ev_attrs = ev_obj.get("attributes") if isinstance(ev_obj, dict) and isinstance(ev_obj.get("attributes"), dict) else {}
                evidence_row_id = str(ev_attrs.get("evidence_row_id") or evidence_id)
                evidence_row_ids.append(evidence_row_id)
                evidence_to_tasks.setdefault(evidence_id, []).append(task_id)

            dependency_ids: list[str] = []
            for target_obj_id in dependencies_by_source.get(obj_id, []):
                target_obj = by_id.get(target_obj_id)
                target_attrs = target_obj.get("attributes") if isinstance(target_obj, dict) and isinstance(target_obj.get("attributes"), dict) else {}
                dependency_ids.append(str(target_attrs.get("task_id") or target_obj_id))

            task_rows.append(
                {
                    "task_id": task_id,
                    "plan_item_id": str(attrs.get("plan_item_id", "")),
                    "status": _status_map_task(status),
                    "owner": str(attrs.get("owner", "")),
                    "validation_method": str(validation_attrs.get("validationMethod", "")),
                    "evidence_row_ids": ";".join(evidence_row_ids),
                    "dependencies": ";".join(sorted(set(dependency_ids))),
                    "output_path": str(attrs.get("output_path", "")),
                    "notes": str(attrs.get("notes", "")),
                    "source_object_id": obj_id,
                }
            )

    for obj in objects:
        kind = obj.get("kind")
        if kind != "EvidenceRecord":
            continue
        attrs = obj.get("attributes") if isinstance(obj.get("attributes"), dict) else {}
        evidence_id = str(obj.get("id", ""))
        evidence_row_id = str(attrs.get("evidence_row_id") or evidence_id)
        evidence_rows.append(
            {
                "evidence_row_id": evidence_row_id,
                "status": _status_map_evidence(str(obj.get("status", "UNKNOWN"))),
                "gate_criterion": str(attrs.get("gate_criterion", "")),
                "source_task_ids": ";".join(sorted(set(evidence_to_tasks.get(evidence_id, [])))),
                "notes": str(attrs.get("notes", "")),
                "source_object_id": evidence_id,
            }
        )

    plan_rows.sort(key=lambda r: r["plan_item_id"])
    task_rows.sort(key=lambda r: r["task_id"])
    evidence_rows.sort(key=lambda r: r["evidence_row_id"])

    out_dir.mkdir(parents=True, exist_ok=True)

    files: list[tuple[str, list[str], list[dict[str, str]]]] = [
        (
            "phase2_plan_items_projection.csv",
            ["plan_item_id", "title", "status", "owner", "notes", "source_object_id"],
            plan_rows,
        ),
        (
            "task_ledger_projection.csv",
            [
                "task_id",
                "plan_item_id",
                "status",
                "owner",
                "validation_method",
                "evidence_row_ids",
                "dependencies",
                "output_path",
                "notes",
                "source_object_id",
            ],
            task_rows,
        ),
        (
            "evidence_register_projection.csv",
            ["evidence_row_id", "status", "gate_criterion", "source_task_ids", "notes", "source_object_id"],
            evidence_rows,
        ),
    ]

    written: list[Path] = []
    for filename, fieldnames, rows in files:
        target = out_dir / filename
        with target.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        written.append(target)

    return written


def main() -> int:
    parser = argparse.ArgumentParser(description="Project kernel PM bundle into CSV views")
    parser.add_argument("--bundle", required=True, help="Path to kernel PM bundle JSON")
    parser.add_argument("--outdir", required=True, help="Projection output directory")
    args = parser.parse_args()

    bundle_path = Path(args.bundle)
    out_dir = Path(args.outdir)

    bundle = _read_json(bundle_path)
    written = project_bundle(bundle, out_dir)

    print("Projection files written:")
    for path in written:
        print(f"- {path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())