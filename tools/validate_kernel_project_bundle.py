#!/usr/bin/env python3
"""Validate kernel project bundle records against the v1 profile rules."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

VALID_KINDS = {
    "ProgramPlan",
    "WorkstreamPlan",
    "WorkPackagePlan",
    "TaskSpecification",
    "CheckpointSpecification",
    "DependencyRelation",
    "DependencyKind",
    "ValidationSpecification",
    "RoleAssignment",
    "HumanAgent",
    "SystemAgent",
    "Role",
    "TaskExecutionActivity",
    "TaskExecutionRecord",
    "CheckpointRecord",
    "EvidenceRecord",
    "RiskRecord",
    "IssueRecord",
    "MitigationPlan",
    "ChangeRequest",
    "ImpactAssessment",
}

VALID_STATUSES = {"IS", "OUGHT", "UNKNOWN"}

EXECUTION_KINDS_REQUIRE_EVIDENCE_IF_IS = {
    "TaskExecutionRecord",
    "CheckpointRecord",
    "EvidenceRecord",
}

REF_RULES: dict[str, dict[str, tuple[set[str], int, int | None]]] = {
    "ProgramPlan": {
        "hasSubPlan": ({"WorkstreamPlan"}, 1, None),
    },
    "WorkstreamPlan": {
        "hasSubPlan": ({"WorkPackagePlan"}, 1, None),
    },
    "WorkPackagePlan": {
        "hasSubPlan": ({"TaskSpecification", "CheckpointSpecification"}, 1, None),
    },
    "TaskSpecification": {
        "hasValidationSpecification": ({"ValidationSpecification"}, 1, 1),
    },
    "DependencyRelation": {
        "dependencySource": ({"TaskSpecification"}, 1, 1),
        "dependencyTarget": ({"TaskSpecification"}, 1, 1),
        "hasDependencyKind": ({"DependencyKind"}, 1, 1),
    },
    "RoleAssignment": {
        "assignsAgent": ({"HumanAgent", "SystemAgent"}, 1, 1),
        "assignsRole": ({"Role"}, 1, 1),
        "assignmentScopePlan": (
            {
                "ProgramPlan",
                "WorkstreamPlan",
                "WorkPackagePlan",
                "TaskSpecification",
                "CheckpointSpecification",
            },
            1,
            None,
        ),
    },
    "ValidationSpecification": {
        "expectsEvidenceRecord": ({"EvidenceRecord"}, 1, None),
    },
    "TaskExecutionRecord": {
        "recordsExecutionOf": ({"TaskSpecification"}, 1, 1),
        "evidencesActivity": ({"TaskExecutionActivity"}, 1, 1),
    },
    "CheckpointRecord": {
        "recordsCheckpointOf": ({"CheckpointSpecification"}, 1, 1),
    },
    "MitigationPlan": {
        "mitigatesRisk": ({"RiskRecord"}, 1, None),
    },
    "ImpactAssessment": {
        "assessesChangeRequest": ({"ChangeRequest"}, 1, None),
    },
}


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _iter_refs(obj: dict[str, Any], predicate: str) -> list[dict[str, Any]]:
    refs = obj.get("refs")
    if not isinstance(refs, list):
        return []
    return [ref for ref in refs if isinstance(ref, dict) and ref.get("predicate") == predicate]


def validate_bundle(bundle: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if not isinstance(bundle, dict):
        return ["Bundle must be a JSON object"]

    for field in ("bundle_id", "generated_at", "objects"):
        if field not in bundle:
            errors.append(f"Missing bundle field: {field}")

    objects = bundle.get("objects")
    if not isinstance(objects, list) or not objects:
        errors.append("Field 'objects' must be a non-empty list")
        return errors

    ids: set[str] = set()
    objects_by_id: dict[str, dict[str, Any]] = {}

    for idx, obj in enumerate(objects):
        if not isinstance(obj, dict):
            errors.append(f"objects[{idx}] must be an object")
            continue

        obj_id = obj.get("id")
        kind = obj.get("kind")
        status = obj.get("status")

        if not isinstance(obj_id, str) or not obj_id:
            errors.append(f"objects[{idx}] missing valid id")
            continue

        if obj_id in ids:
            errors.append(f"Duplicate object id: {obj_id}")
        ids.add(obj_id)
        objects_by_id[obj_id] = obj

        if kind not in VALID_KINDS:
            errors.append(f"{obj_id}: invalid kind '{kind}'")

        if status not in VALID_STATUSES:
            errors.append(f"{obj_id}: invalid status '{status}'")

        refs = obj.get("refs", [])
        if refs is not None and not isinstance(refs, list):
            errors.append(f"{obj_id}: refs must be a list when present")
            refs = []

        for ref_idx, ref in enumerate(refs):
            if not isinstance(ref, dict):
                errors.append(f"{obj_id}: refs[{ref_idx}] must be an object")
                continue
            if not isinstance(ref.get("predicate"), str) or not ref.get("predicate"):
                errors.append(f"{obj_id}: refs[{ref_idx}] missing predicate")
            if not isinstance(ref.get("target_id"), str) or not ref.get("target_id"):
                errors.append(f"{obj_id}: refs[{ref_idx}] missing target_id")

    for obj_id, obj in objects_by_id.items():
        for ref in obj.get("refs", []) or []:
            target_id = ref.get("target_id")
            if isinstance(target_id, str) and target_id not in objects_by_id:
                errors.append(f"{obj_id}: ref target does not exist: {target_id}")

    for obj_id, obj in objects_by_id.items():
        kind = obj.get("kind")
        kind_rules = REF_RULES.get(kind, {})
        for predicate, (allowed_kinds, min_count, max_count) in kind_rules.items():
            refs = _iter_refs(obj, predicate)
            count = len(refs)
            if count < min_count:
                errors.append(
                    f"{obj_id}: predicate '{predicate}' requires at least {min_count} reference(s)"
                )
            if max_count is not None and count > max_count:
                errors.append(
                    f"{obj_id}: predicate '{predicate}' allows at most {max_count} reference(s)"
                )
            for ref in refs:
                target = objects_by_id.get(ref.get("target_id"))
                if target and target.get("kind") not in allowed_kinds:
                    errors.append(
                        f"{obj_id}: predicate '{predicate}' target kind '{target.get('kind')}' is not allowed"
                    )

        if kind == "DependencyRelation":
            source_refs = _iter_refs(obj, "dependencySource")
            target_refs = _iter_refs(obj, "dependencyTarget")
            if source_refs and target_refs:
                if source_refs[0].get("target_id") == target_refs[0].get("target_id"):
                    errors.append(f"{obj_id}: dependencySource and dependencyTarget must not be identical")

        if kind in EXECUTION_KINDS_REQUIRE_EVIDENCE_IF_IS and obj.get("status") == "IS":
            evidence_refs = obj.get("evidence_refs")
            if not isinstance(evidence_refs, list) or not evidence_refs:
                errors.append(f"{obj_id}: status IS requires non-empty evidence_refs")

        if kind == "ValidationSpecification":
            attributes = obj.get("attributes")
            if not isinstance(attributes, dict):
                errors.append(f"{obj_id}: ValidationSpecification requires attributes object")
                continue
            for field in ("validationMethod", "passCondition"):
                value = attributes.get(field)
                if not isinstance(value, str) or not value.strip():
                    errors.append(f"{obj_id}: ValidationSpecification missing attribute '{field}'")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate kernel project bundle JSON")
    parser.add_argument("--bundle", required=True, help="Path to kernel project bundle JSON")
    args = parser.parse_args()

    bundle_path = Path(args.bundle)
    bundle = _read_json(bundle_path)
    errors = validate_bundle(bundle)

    if errors:
        print("Kernel project bundle validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Kernel project bundle validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())