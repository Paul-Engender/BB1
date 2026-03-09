#!/usr/bin/env python3
"""Project kernel project bundle objects into CSV view surfaces."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

VALID_STATUSES = {"IS", "OUGHT", "UNKNOWN"}


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _refs(obj: dict[str, Any] | None, predicate: str) -> list[str]:
    if not isinstance(obj, dict):
        return []
    refs = obj.get("refs") or []
    out: list[str] = []
    for ref in refs:
        if isinstance(ref, dict) and ref.get("predicate") == predicate and isinstance(ref.get("target_id"), str):
            out.append(ref["target_id"])
    return out


def _attrs(obj: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(obj, dict):
        return {}
    attrs = obj.get("attributes")
    if isinstance(attrs, dict):
        return attrs
    return {}


def _status(status: str) -> str:
    return status if status in VALID_STATUSES else "UNKNOWN"


def _status_map_plan(status: str) -> str:
    return {"IS": "DONE", "OUGHT": "PLANNED", "UNKNOWN": "BLOCKED"}.get(_status(status), "BLOCKED")


def _status_map_task(status: str) -> str:
    return {"IS": "DONE", "OUGHT": "TO_DO", "UNKNOWN": "BLOCKED"}.get(_status(status), "BLOCKED")


def _status_map_evidence(status: str) -> str:
    return {"IS": "VERIFIED", "OUGHT": "TO_DO", "UNKNOWN": "BLOCKED"}.get(_status(status), "BLOCKED")


def _join_unique(values: list[str]) -> str:
    return ";".join(sorted({v for v in values if v}))


def project_bundle(bundle: dict[str, Any], out_dir: Path) -> list[Path]:
    objects = bundle.get("objects", [])
    by_id: dict[str, dict[str, Any]] = {
        obj["id"]: obj
        for obj in objects
        if isinstance(obj, dict) and isinstance(obj.get("id"), str)
    }

    dependencies_by_source: dict[str, list[str]] = {}
    for obj in objects:
        if not isinstance(obj, dict) or obj.get("kind") != "DependencyRelation":
            continue
        for source_id in _refs(obj, "dependencySource"):
            target_ids = _refs(obj, "dependencyTarget")
            if not target_ids:
                continue
            dependencies_by_source.setdefault(source_id, []).extend(target_ids)

    evidence_to_tasks: dict[str, list[str]] = {}

    plan_rows: list[dict[str, str]] = []
    workpackage_rows: list[dict[str, str]] = []
    dependency_rows: list[dict[str, str]] = []
    task_rows: list[dict[str, str]] = []
    evidence_rows: list[dict[str, str]] = []

    role_assignment_rows: list[dict[str, str]] = []
    checkpoint_spec_rows: list[dict[str, str]] = []
    task_execution_record_rows: list[dict[str, str]] = []
    checkpoint_record_rows: list[dict[str, str]] = []

    risk_rows: list[dict[str, str]] = []
    issue_rows: list[dict[str, str]] = []
    mitigation_rows: list[dict[str, str]] = []
    change_rows: list[dict[str, str]] = []
    impact_rows: list[dict[str, str]] = []

    for obj in objects:
        if not isinstance(obj, dict):
            continue

        obj_id = str(obj.get("id", ""))
        kind = str(obj.get("kind", ""))
        status = _status(str(obj.get("status", "UNKNOWN")))
        attrs = _attrs(obj)

        if kind == "WorkstreamPlan" and isinstance(attrs.get("plan_item_id"), str):
            plan_rows.append(
                {
                    "plan_item_id": str(attrs.get("plan_item_id", "")),
                    "title": str(attrs.get("title", "")),
                    "status": _status_map_plan(status),
                    "owner": str(attrs.get("owner", "")),
                    "notes": str(attrs.get("notes", "")),
                    "source_object_id": obj_id,
                }
            )

        if kind == "WorkPackagePlan":
            subplan_ids = _refs(obj, "hasSubPlan")
            task_ids: list[str] = []
            for subplan_id in subplan_ids:
                target_obj = by_id.get(subplan_id)
                target_attrs = _attrs(target_obj)
                task_ids.append(str(target_attrs.get("task_id") or subplan_id))

            workpackage_rows.append(
                {
                    "workpackage_id": str(attrs.get("workpackage_id") or obj_id),
                    "status": _status_map_plan(status),
                    "task_spec_ids": _join_unique(task_ids),
                    "notes": str(attrs.get("notes", "")),
                    "source_object_id": obj_id,
                }
            )

        if kind == "TaskSpecification" and isinstance(attrs.get("task_id"), str):
            task_id = str(attrs.get("task_id", ""))
            validation_ids = _refs(obj, "hasValidationSpecification")
            validation = by_id.get(validation_ids[0]) if validation_ids else None
            validation_attrs = _attrs(validation)
            evidence_targets = _refs(validation, "expectsEvidenceRecord")
            evidence_row_ids: list[str] = []

            for evidence_id in evidence_targets:
                ev_obj = by_id.get(evidence_id)
                ev_attrs = _attrs(ev_obj)
                evidence_row_id = str(ev_attrs.get("evidence_row_id") or evidence_id)
                evidence_row_ids.append(evidence_row_id)
                evidence_to_tasks.setdefault(evidence_id, []).append(task_id)

            dependency_ids: list[str] = []
            for target_obj_id in dependencies_by_source.get(obj_id, []):
                target_obj = by_id.get(target_obj_id)
                target_attrs = _attrs(target_obj)
                dependency_ids.append(str(target_attrs.get("task_id") or target_obj_id))

            task_rows.append(
                {
                    "task_id": task_id,
                    "plan_item_id": str(attrs.get("plan_item_id", "")),
                    "status": _status_map_task(status),
                    "owner": str(attrs.get("owner", "")),
                    "validation_method": str(validation_attrs.get("validationMethod", "")),
                    "evidence_row_ids": _join_unique(evidence_row_ids),
                    "dependencies": _join_unique(dependency_ids),
                    "output_path": str(attrs.get("output_path", "")),
                    "notes": str(attrs.get("notes", "")),
                    "source_object_id": obj_id,
                }
            )

        if kind == "DependencyRelation":
            source_ids: list[str] = []
            for source_obj_id in _refs(obj, "dependencySource"):
                source_obj = by_id.get(source_obj_id)
                source_ids.append(str(_attrs(source_obj).get("task_id") or source_obj_id))

            target_ids: list[str] = []
            for target_obj_id in _refs(obj, "dependencyTarget"):
                target_obj = by_id.get(target_obj_id)
                target_ids.append(str(_attrs(target_obj).get("task_id") or target_obj_id))

            dependency_rows.append(
                {
                    "dependency_id": obj_id,
                    "status": _status_map_plan(status),
                    "source_task_ids": _join_unique(source_ids),
                    "target_task_ids": _join_unique(target_ids),
                    "dependency_kind_ids": _join_unique(_refs(obj, "hasDependencyKind")),
                    "source_object_id": obj_id,
                }
            )

        if kind == "RoleAssignment":
            role_assignment_rows.append(
                {
                    "role_assignment_id": str(attrs.get("role_assignment_id") or obj_id),
                    "status": _status_map_plan(status),
                    "agent_ids": _join_unique(_refs(obj, "assignsAgent")),
                    "role_ids": _join_unique(_refs(obj, "assignsRole")),
                    "scope_plan_ids": _join_unique(_refs(obj, "assignmentScopePlan")),
                    "source_object_id": obj_id,
                }
            )

        if kind == "CheckpointSpecification":
            checkpoint_spec_rows.append(
                {
                    "checkpoint_id": str(attrs.get("checkpoint_id") or obj_id),
                    "status": _status_map_task(status),
                    "title": str(attrs.get("title", "")),
                    "notes": str(attrs.get("notes", "")),
                    "source_object_id": obj_id,
                }
            )

        if kind == "TaskExecutionRecord":
            task_execution_record_rows.append(
                {
                    "task_execution_record_id": str(attrs.get("task_execution_record_id") or obj_id),
                    "status": _status_map_task(status),
                    "task_spec_ids": _join_unique(_refs(obj, "recordsExecutionOf")),
                    "activity_ids": _join_unique(_refs(obj, "evidencesActivity")),
                    "evidence_refs": _join_unique([str(v) for v in (obj.get("evidence_refs") or []) if isinstance(v, str)]),
                    "source_object_id": obj_id,
                }
            )

        if kind == "CheckpointRecord":
            checkpoint_record_rows.append(
                {
                    "checkpoint_record_id": str(attrs.get("checkpoint_record_id") or obj_id),
                    "status": _status_map_task(status),
                    "checkpoint_spec_ids": _join_unique(_refs(obj, "recordsCheckpointOf")),
                    "evidence_refs": _join_unique([str(v) for v in (obj.get("evidence_refs") or []) if isinstance(v, str)]),
                    "source_object_id": obj_id,
                }
            )

        if kind == "RiskRecord":
            risk_rows.append(
                {
                    "risk_id": str(attrs.get("risk_id") or obj_id),
                    "status": _status_map_task(status),
                    "severity": str(attrs.get("severity", "")),
                    "owner": str(attrs.get("owner", "")),
                    "notes": str(attrs.get("notes", "")),
                    "source_object_id": obj_id,
                }
            )

        if kind == "IssueRecord":
            issue_rows.append(
                {
                    "issue_id": str(attrs.get("issue_id") or obj_id),
                    "status": _status_map_task(status),
                    "severity": str(attrs.get("severity", "")),
                    "owner": str(attrs.get("owner", "")),
                    "notes": str(attrs.get("notes", "")),
                    "source_object_id": obj_id,
                }
            )

        if kind == "MitigationPlan":
            mitigation_rows.append(
                {
                    "mitigation_id": str(attrs.get("mitigation_id") or obj_id),
                    "status": _status_map_task(status),
                    "risk_ids": _join_unique(_refs(obj, "mitigatesRisk")),
                    "owner": str(attrs.get("owner", "")),
                    "notes": str(attrs.get("notes", "")),
                    "source_object_id": obj_id,
                }
            )

        if kind == "ChangeRequest":
            change_rows.append(
                {
                    "change_request_id": str(attrs.get("change_request_id") or obj_id),
                    "status": _status_map_task(status),
                    "title": str(attrs.get("title", "")),
                    "owner": str(attrs.get("owner", "")),
                    "notes": str(attrs.get("notes", "")),
                    "source_object_id": obj_id,
                }
            )

        if kind == "ImpactAssessment":
            impact_rows.append(
                {
                    "impact_assessment_id": str(attrs.get("impact_assessment_id") or obj_id),
                    "status": _status_map_task(status),
                    "change_request_ids": _join_unique(_refs(obj, "assessesChangeRequest")),
                    "notes": str(attrs.get("notes", "")),
                    "source_object_id": obj_id,
                }
            )

    for obj in objects:
        if not isinstance(obj, dict) or obj.get("kind") != "EvidenceRecord":
            continue
        attrs = _attrs(obj)
        evidence_id = str(obj.get("id", ""))
        evidence_row_id = str(attrs.get("evidence_row_id") or evidence_id)
        evidence_rows.append(
            {
                "evidence_row_id": evidence_row_id,
                "status": _status_map_evidence(str(obj.get("status", "UNKNOWN"))),
                "gate_criterion": str(attrs.get("gate_criterion", "")),
                "source_task_ids": _join_unique(evidence_to_tasks.get(evidence_id, [])),
                "notes": str(attrs.get("notes", "")),
                "source_object_id": evidence_id,
            }
        )

    plan_rows.sort(key=lambda r: r["plan_item_id"])
    workpackage_rows.sort(key=lambda r: r["workpackage_id"])
    dependency_rows.sort(key=lambda r: r["dependency_id"])
    task_rows.sort(key=lambda r: r["task_id"])
    evidence_rows.sort(key=lambda r: r["evidence_row_id"])

    role_assignment_rows.sort(key=lambda r: r["role_assignment_id"])
    checkpoint_spec_rows.sort(key=lambda r: r["checkpoint_id"])
    task_execution_record_rows.sort(key=lambda r: r["task_execution_record_id"])
    checkpoint_record_rows.sort(key=lambda r: r["checkpoint_record_id"])
    risk_rows.sort(key=lambda r: r["risk_id"])
    issue_rows.sort(key=lambda r: r["issue_id"])
    mitigation_rows.sort(key=lambda r: r["mitigation_id"])
    change_rows.sort(key=lambda r: r["change_request_id"])
    impact_rows.sort(key=lambda r: r["impact_assessment_id"])

    out_dir.mkdir(parents=True, exist_ok=True)

    files: list[tuple[str, list[str], list[dict[str, str]]]] = [
        (
            "phase2_plan_items_projection.csv",
            ["plan_item_id", "title", "status", "owner", "notes", "source_object_id"],
            plan_rows,
        ),
        (
            "work_packages_projection.csv",
            ["workpackage_id", "status", "task_spec_ids", "notes", "source_object_id"],
            workpackage_rows,
        ),
        (
            "dependency_relations_projection.csv",
            ["dependency_id", "status", "source_task_ids", "target_task_ids", "dependency_kind_ids", "source_object_id"],
            dependency_rows,
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
        (
            "role_assignments_projection.csv",
            ["role_assignment_id", "status", "agent_ids", "role_ids", "scope_plan_ids", "source_object_id"],
            role_assignment_rows,
        ),
        (
            "checkpoint_specifications_projection.csv",
            ["checkpoint_id", "status", "title", "notes", "source_object_id"],
            checkpoint_spec_rows,
        ),
        (
            "task_execution_records_projection.csv",
            ["task_execution_record_id", "status", "task_spec_ids", "activity_ids", "evidence_refs", "source_object_id"],
            task_execution_record_rows,
        ),
        (
            "checkpoint_records_projection.csv",
            ["checkpoint_record_id", "status", "checkpoint_spec_ids", "evidence_refs", "source_object_id"],
            checkpoint_record_rows,
        ),
        (
            "risk_register_projection.csv",
            ["risk_id", "status", "severity", "owner", "notes", "source_object_id"],
            risk_rows,
        ),
        (
            "issue_register_projection.csv",
            ["issue_id", "status", "severity", "owner", "notes", "source_object_id"],
            issue_rows,
        ),
        (
            "mitigation_plans_projection.csv",
            ["mitigation_id", "status", "risk_ids", "owner", "notes", "source_object_id"],
            mitigation_rows,
        ),
        (
            "change_requests_projection.csv",
            ["change_request_id", "status", "title", "owner", "notes", "source_object_id"],
            change_rows,
        ),
        (
            "impact_assessments_projection.csv",
            ["impact_assessment_id", "status", "change_request_ids", "notes", "source_object_id"],
            impact_rows,
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
