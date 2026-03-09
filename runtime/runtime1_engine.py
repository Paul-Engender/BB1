"""Runtime 1 support-ontology release engine.

This module turns kernel validation substrate into a release-producing service
boundary with evidence outputs and promotion-gate checks.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from rdflib import Graph

try:
    from jsonschema import Draft7Validator
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    Draft7Validator = None

try:
    from .kernel_gate import validate_abox
except ImportError:
    from kernel_gate import validate_abox

from src.loader import verify_and_load
from tools.packager import create_package


class Runtime1EngineError(RuntimeError):
    """Raised when Runtime 1 release-candidate evaluation fails."""


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _combined_examples() -> str:
    examples_dir = _repo_root() / "ontology" / "examples"
    parts: list[str] = []
    for ttl_file in sorted(examples_dir.glob("*.ttl")):
        parts.append(ttl_file.read_text(encoding="utf-8"))
    return "\n".join(parts)


def evaluate_release_candidate(*, deterministic: bool = False) -> dict[str, Any]:
    """Evaluate support-ontology release candidate and return evidence payload."""
    root = _repo_root()
    ontology_dir = root / "ontology"

    checks: list[dict[str, Any]] = []

    core_files = [
        ontology_dir / "kernel.ttl",
        ontology_dir / "kernel.shacl.ttl",
    ]
    for path in core_files:
        check: dict[str, Any] = {
            "check_id": f"parse::{path.name}",
            "kind": "parse",
            "path": str(path.relative_to(root)).replace("\\", "/"),
        }
        try:
            graph = Graph()
            graph.parse(data=path.read_text(encoding="utf-8"), format="turtle")
            check["status"] = "PASS"
            check["triple_count"] = len(graph)
            check["sha256"] = _sha256_file(path)
        except Exception as exc:  # pragma: no cover - propagated in report
            check["status"] = "FAIL"
            check["error"] = str(exc)
        checks.append(check)

    positive_check: dict[str, Any] = {
        "check_id": "validate::positive_examples",
        "kind": "shacl_positive",
    }
    try:
        conforms, _, results_text = validate_abox(_combined_examples())
        positive_check["status"] = "PASS" if conforms else "FAIL"
        positive_check["conforms"] = bool(conforms)
        positive_check["report_excerpt"] = ("deterministic-mode-redacted" if deterministic else str(results_text)[:4000])
    except Exception as exc:  # pragma: no cover - propagated in report
        positive_check["status"] = "FAIL"
        positive_check["error"] = str(exc)
    checks.append(positive_check)

    negative_dir = ontology_dir / "negative_examples"
    for path in sorted(negative_dir.glob("*.ttl")):
        check = {
            "check_id": f"validate::negative::{path.name}",
            "kind": "shacl_negative",
            "path": str(path.relative_to(root)).replace("\\", "/"),
        }
        try:
            conforms, _, results_text = validate_abox(path.read_text(encoding="utf-8"))
            check["status"] = "PASS" if not conforms else "FAIL"
            check["conforms"] = bool(conforms)
            check["report_excerpt"] = ("deterministic-mode-redacted" if deterministic else str(results_text)[:2000])
        except Exception as exc:  # pragma: no cover - propagated in report
            check["status"] = "FAIL"
            check["error"] = str(exc)
        checks.append(check)

    passed = sum(1 for c in checks if c.get("status") == "PASS")
    failed = sum(1 for c in checks if c.get("status") != "PASS")
    accepted = failed == 0

    generated_at = (
        "1970-01-01T00:00:00+00:00"
        if deterministic
        else datetime.now(timezone.utc).isoformat()
    )

    return {
        "engine": "runtime1_support_ontology_engine",
        "generated_at": generated_at,
        "accepted": accepted,
        "summary": {
            "total_checks": len(checks),
            "passed": passed,
            "failed": failed,
        },
        "checks": checks,
    }


def _write_evidence_bundle(evidence_dir: Path, evaluation: dict[str, Any]) -> list[Path]:
    evidence_dir.mkdir(parents=True, exist_ok=True)

    summary_path = evidence_dir / "release_candidate_evaluation.json"
    summary_path.write_text(json.dumps(evaluation, indent=2, sort_keys=True), encoding="utf-8")

    checks_jsonl = evidence_dir / "release_candidate_checks.jsonl"
    with checks_jsonl.open("w", encoding="utf-8") as f:
        for check in evaluation["checks"]:
            f.write(json.dumps(check, sort_keys=True) + "\n")

    return [summary_path, checks_jsonl]


def _validate_release_manifest(manifest_path: Path) -> None:
    if Draft7Validator is None:
        return

    schema_path = _repo_root() / "schemas" / "release_manifest.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8-sig"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(manifest), key=lambda e: list(e.path))
    if errors:
        messages = [f"{'/'.join(str(x) for x in e.path) or '<root>'}: {e.message}" for e in errors]
        raise Runtime1EngineError("Manifest schema validation failed: " + " | ".join(messages))

    if manifest.get("manifest_version") != "2.0":
        raise Runtime1EngineError("Runtime 1 support release must emit manifest_version '2.0'.")
    if manifest.get("artifact_type") != "SupportOntologyRelease":
        raise Runtime1EngineError("Runtime 1 support release must emit artifact_type 'SupportOntologyRelease'.")


def _write_promotion_decision(
    out_dir: Path,
    *,
    release_id: str,
    manifest_path: Path,
    archive_path: Path,
    evaluation: dict[str, Any],
    loader_ok: bool,
    loader_message: str,
) -> Path:
    decision = {
        "decision_type": "Runtime1PromotionDecision",
        "release_id": release_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "candidate_accepted": bool(evaluation.get("accepted", False)),
        "loader_verification_ok": bool(loader_ok),
        "loader_verification_message": loader_message,
        "manifest_path": str(manifest_path),
        "archive_path": str(archive_path),
        "manifest_sha256": _sha256_file(manifest_path),
        "archive_sha256": _sha256_file(archive_path),
        "decision": "APPROVED" if loader_ok and evaluation.get("accepted", False) else "REJECTED",
    }

    decision_path = out_dir / "promotion_decision.json"
    decision_path.write_text(json.dumps(decision, indent=2, sort_keys=True), encoding="utf-8")
    return decision_path


def build_support_ontology_release(
    release_version: str = "0.2.0",
    output_root: str = "dist",
    *,
    deterministic: bool = True,
    run_promotion_gate: bool = True,
) -> dict[str, Any]:
    """Build an evidence-bound SupportOntologyRelease package."""
    evaluation = evaluate_release_candidate(deterministic=deterministic)
    if not evaluation.get("accepted", False):
        raise Runtime1EngineError("Release candidate rejected; evidence bundle contains failed checks.")

    root = _repo_root()
    output_root_path = (root / output_root).resolve()
    release_id = f"SupportOntologyRelease-v{release_version}"
    out_dir = output_root_path / release_id

    canonical_payload_paths = [
        root / "ontology" / "kernel.ttl",
        root / "ontology" / "kernel.shacl.ttl",
    ]

    evidence_source_dir = out_dir / "_evidence_src"
    evidence_files = _write_evidence_bundle(evidence_source_dir, evaluation)

    manifest_path_str, archive_path_str = create_package(
        release_id=release_id,
        file_paths=[str(path) for path in canonical_payload_paths],
        output_dir=str(out_dir),
        base_dir=str(root),
        artifact_type="SupportOntologyRelease",
        artifact_version=release_version,
        tenant_scope="global",
        dependencies=[],
        evidence_paths=[str(p) for p in evidence_files],
        manifest_version="2.0",
        deterministic=deterministic,
        issued_at=evaluation["generated_at"] if deterministic else None,
        primary_file="ontology/kernel.ttl",
    )

    manifest_path = Path(manifest_path_str)
    archive_path = Path(archive_path_str)

    _validate_release_manifest(manifest_path)

    loader_ok = True
    loader_message = "promotion gate skipped"
    if run_promotion_gate:
        verify_dir = out_dir / "_promotion_verify"
        loader_ok, loader_message = verify_and_load(
            manifest_path=str(manifest_path),
            archive_path=str(archive_path),
            load_dir=str(verify_dir),
        )
        if not loader_ok:
            raise Runtime1EngineError(f"Promotion gate failed: {loader_message}")

    promotion_decision_path = _write_promotion_decision(
        out_dir,
        release_id=release_id,
        manifest_path=manifest_path,
        archive_path=archive_path,
        evaluation=evaluation,
        loader_ok=loader_ok,
        loader_message=loader_message,
    )

    return {
        "release_id": release_id,
        "manifest_path": str(manifest_path),
        "archive_path": str(archive_path),
        "evidence_files": [str(p) for p in evidence_files],
        "promotion_decision_path": str(promotion_decision_path),
        "loader_verification_message": loader_message,
        "evaluation": evaluation,
    }





