"""Runtime 2 compiler baseline engine.

Implements a deterministic, fail-closed first-slice compile path from tenant
workflow input plus exact SupportOntologyRelease dependency binding into an
SCR_TBox_Release package with evidence.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from rdflib import Graph, Namespace
from rdflib.namespace import RDF

from src.cid import validate_cid
from tools.runtime2_packager import build_scr_tbox_release

KERN = Namespace("https://ontology.engender.co.za/kernel#")

REQUIRED_TENANT_FIELDS: list[tuple[str, Any]] = [
    ("tenant_id", KERN.tenantId),
    ("workflow_id", KERN.workflowId),
    ("workflow_version", KERN.workflowVersion),
    ("domain_id", KERN.domainId),
    ("routing_policy_id", KERN.routingPolicyId),
    ("target_set_ref", KERN.targetSetRef),
    ("scope_ref", KERN.scopeRef),
    ("action_ref", KERN.actionRef),
    ("effect_ref", KERN.effectRef),
    ("action_effect_binding_ref", KERN.actionEffectBindingRef),
    ("authorization_semantics_ref", KERN.authorizationSemanticsRef),
    ("eligibility_semantics_ref", KERN.eligibilitySemanticsRef),
    ("denial_semantics_ref", KERN.denialSemanticsRef),
    ("control_state_semantics_ref", KERN.controlStateSemanticsRef),
    ("ai_operable", KERN.aiOperable),
]

PRIMITIVE_FAMILIES: list[tuple[str, str]] = [
    ("TargetScopePrimitive", "TargetScopePrimitiveType"),
    ("ActionEffectPrimitive", "ActionEffectPrimitiveType"),
    ("AuthorizationPrimitive", "AuthorizationPrimitiveType"),
    ("EligibilityPrimitive", "EligibilityPrimitiveType"),
    ("DenialPrimitive", "DenialPrimitiveType"),
    ("ControlStatePrimitive", "ControlStatePrimitiveType"),
    ("TracePrimitive", "TracePrimitiveType"),
]


@dataclass(slots=True)
class CompileRequest:
    tenant_input_path: str
    support_release_manifest_path: str
    support_release_archive_path: str
    requested_release_version: str
    deterministic: bool


class Runtime2CompileError(RuntimeError):
    """Raised when Runtime 2 compile gating fails."""

    def __init__(self, *, outcome: str, reason_code: str, stage: str, detail: str):
        self.outcome = outcome
        self.reason_code = reason_code
        self.stage = stage
        self.detail = detail
        super().__init__(f"{outcome} {reason_code} ({stage}): {detail}")


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _slug(value: str) -> str:
    compact = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip())
    compact = compact.strip("-._")
    return compact or "tenant"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _require_file(path: Path, *, stage: str, reason_code: str, detail: str) -> None:
    if not path.exists() or not path.is_file():
        raise Runtime2CompileError(
            outcome="ABORT",
            reason_code=reason_code,
            stage=stage,
            detail=f"{detail}: {path}",
        )


def _parse_request(
    *,
    tenant_input_path: str,
    support_release_manifest_path: str,
    support_release_archive_path: str,
    requested_release_version: str,
    deterministic: bool,
) -> CompileRequest:
    request = CompileRequest(
        tenant_input_path=tenant_input_path,
        support_release_manifest_path=support_release_manifest_path,
        support_release_archive_path=support_release_archive_path,
        requested_release_version=requested_release_version,
        deterministic=bool(deterministic),
    )

    if not request.requested_release_version.strip():
        raise Runtime2CompileError(
            outcome="ABORT",
            reason_code="RC:S1:REQUEST:MISSING_RELEASE_VERSION",
            stage="S1",
            detail="requested_release_version is required",
        )

    _require_file(
        Path(request.tenant_input_path),
        stage="S1",
        reason_code="RC:S1:REQUEST:MISSING_TENANT_INPUT",
        detail="tenant input path not found",
    )
    _require_file(
        Path(request.support_release_manifest_path),
        stage="S1",
        reason_code="RC:S1:REQUEST:MISSING_SUPPORT_MANIFEST",
        detail="support release manifest path not found",
    )
    _require_file(
        Path(request.support_release_archive_path),
        stage="S1",
        reason_code="RC:S1:REQUEST:MISSING_SUPPORT_ARCHIVE",
        detail="support release archive path not found",
    )

    return request


def _validate_support_release_binding(request: CompileRequest) -> dict[str, Any]:
    manifest_path = Path(request.support_release_manifest_path)
    archive_path = Path(request.support_release_archive_path)

    try:
        manifest = _read_json(manifest_path)
    except Exception as exc:
        raise Runtime2CompileError(
            outcome="ABORT",
            reason_code="RC:S2:DEPENDENCY:INVALID_MANIFEST",
            stage="S2",
            detail=f"support release manifest parse failed: {exc}",
        ) from exc

    if manifest.get("manifest_version") != "2.0":
        raise Runtime2CompileError(
            outcome="ABORT",
            reason_code="RC:S2:DEPENDENCY:INVALID_SUPPORT_RELEASE",
            stage="S2",
            detail="support release manifest must be v2.0",
        )
    if manifest.get("artifact_type") != "SupportOntologyRelease":
        raise Runtime2CompileError(
            outcome="ABORT",
            reason_code="RC:S2:DEPENDENCY:INVALID_SUPPORT_RELEASE",
            stage="S2",
            detail="artifact_type must be SupportOntologyRelease",
        )
    if manifest.get("tenant_scope") != "global":
        raise Runtime2CompileError(
            outcome="ABORT",
            reason_code="RC:S2:DEPENDENCY:INVALID_SUPPORT_RELEASE",
            stage="S2",
            detail="support release tenant_scope must be global",
        )

    try:
        archive_bytes = archive_path.read_bytes()
    except OSError as exc:
        raise Runtime2CompileError(
            outcome="ABORT",
            reason_code="RC:S2:DEPENDENCY:INVALID_SUPPORT_RELEASE",
            stage="S2",
            detail=f"support release archive read failed: {exc}",
        ) from exc

    release_cid = manifest.get("release_cid")
    if not isinstance(release_cid, str) or not validate_cid(release_cid, archive_bytes):
        raise Runtime2CompileError(
            outcome="ABORT",
            reason_code="RC:S2:DEPENDENCY:INVALID_SUPPORT_RELEASE",
            stage="S2",
            detail="support release archive integrity check failed",
        )

    return manifest


def _parse_tenant_input(path: Path) -> tuple[dict[str, Any], str]:
    data = path.read_text(encoding="utf-8")
    graph = Graph()
    try:
        graph.parse(data=data, format="turtle")
    except Exception as exc:
        raise Runtime2CompileError(
            outcome="ABORT",
            reason_code="RC:S3:REQUEST:UNPARSABLE_TENANT_INPUT",
            stage="S3",
            detail=str(exc),
        ) from exc

    workflow_nodes = sorted({node for node in graph.subjects(RDF.type, KERN.TenantWorkflowInput)}, key=str)
    if not workflow_nodes:
        raise Runtime2CompileError(
            outcome="ABORT",
            reason_code="RC:S3:REQUEST:MISSING_TENANT_WORKFLOW_INPUT",
            stage="S3",
            detail="no kern:TenantWorkflowInput node found",
        )

    workflow_node = workflow_nodes[0]
    normalized: dict[str, Any] = {
        "workflow_node": str(workflow_node),
    }

    for field_name, predicate in REQUIRED_TENANT_FIELDS:
        values = list(graph.objects(workflow_node, predicate))
        if not values:
            raise Runtime2CompileError(
                outcome="ABORT",
                reason_code=f"RC:S3:REQUEST:MISSING_{field_name.upper()}",
                stage="S3",
                detail=f"required field missing: {field_name}",
            )
        normalized[field_name] = str(values[0])

    if list(graph.objects(workflow_node, KERN.constraints)):
        raise Runtime2CompileError(
            outcome="QUARANTINE",
            reason_code="RC:S3:DD-004:UNSUPPORTED_CONSTRAINT",
            stage="S3",
            detail="explicit constraints are forbidden in first-compile tenant input",
        )

    ai_operable_value = normalized["ai_operable"].strip().lower()
    if ai_operable_value not in {"true", "1"}:
        raise Runtime2CompileError(
            outcome="DENY",
            reason_code="RC:S4:ADMISSIBILITY:AI_OPERABLE_NOT_TRUE",
            stage="S4",
            detail="aiOperable must be explicitly true",
        )

    return normalized, data


def _emit_primitives(
    normalized: dict[str, Any],
    *,
    support_artifact_id: str,
    support_artifact_version: str,
    deterministic: bool,
) -> dict[str, Any]:
    generated_at = "1970-01-01T00:00:00+00:00" if deterministic else datetime.now(timezone.utc).isoformat()
    trace_id = f"compile-trace::{normalized['workflow_id']}"

    primitives: list[dict[str, Any]] = []
    for family_name, family_type in PRIMITIVE_FAMILIES:
        primitive_id = f"{family_name.lower()}::{normalized['workflow_id']}"
        primitives.append(
            {
                "primitive_id": primitive_id,
                "primitive_type": family_name,
                "primitive_type_ref": f"kern:{family_type}",
                "tenant_id": normalized["tenant_id"],
                "workflow_id": normalized["workflow_id"],
                "scope_ref": normalized["scope_ref"],
                "target_set_ref": normalized["target_set_ref"],
                "action_ref": normalized["action_ref"],
                "effect_ref": normalized["effect_ref"],
                "authorization_ref": normalized["authorization_semantics_ref"],
                "eligibility_ref": normalized["eligibility_semantics_ref"],
                "denial_ref": normalized["denial_semantics_ref"],
                "control_state_ref": normalized["control_state_semantics_ref"],
                "support_release_ref": support_artifact_id,
                "support_release_version": support_artifact_version,
                "source_input_ref": normalized["workflow_node"],
                "compile_reason_code_policy_ref": "RC:POLICY:DEFAULT",
                "compile_trace_ref": trace_id,
                "generated_at": generated_at,
            }
        )

    return {
        "generated_at": generated_at,
        "trace_id": trace_id,
        "tenant_id": normalized["tenant_id"],
        "workflow_id": normalized["workflow_id"],
        "primitive_families": [name for name, _ in PRIMITIVE_FAMILIES],
        "primitives": primitives,
    }


def _emit_evidence(
    normalized: dict[str, Any],
    *,
    support_manifest: dict[str, Any],
    compile_request: CompileRequest,
    deterministic: bool,
) -> dict[str, Any]:
    generated_at = "1970-01-01T00:00:00+00:00" if deterministic else datetime.now(timezone.utc).isoformat()

    return {
        "generated_at": generated_at,
        "compile_request": {
            "tenant_input_path": compile_request.tenant_input_path,
            "support_release_manifest_path": compile_request.support_release_manifest_path,
            "support_release_archive_path": compile_request.support_release_archive_path,
            "requested_release_version": compile_request.requested_release_version,
            "deterministic": compile_request.deterministic,
        },
        "admitted_summary": {
            "tenant_id": normalized["tenant_id"],
            "workflow_id": normalized["workflow_id"],
            "workflow_version": normalized["workflow_version"],
            "domain_id": normalized["domain_id"],
            "routing_policy_id": normalized["routing_policy_id"],
            "ai_operable": normalized["ai_operable"],
        },
        "support_release_binding": {
            "artifact_id": support_manifest.get("artifact_id"),
            "artifact_version": support_manifest.get("artifact_version"),
            "artifact_type": support_manifest.get("artifact_type"),
            "tenant_scope": support_manifest.get("tenant_scope"),
        },
        "gate_outcome": {
            "decision": "ACCEPT",
            "primary_reason_code": "RC:S4:ADMISSIBILITY:PASS",
            "stage": "S4",
        },
        "primitive_family_completeness": {
            "required": [name for name, _ in PRIMITIVE_FAMILIES],
            "emitted_count": len(PRIMITIVE_FAMILIES),
        },
    }


def compile_tenant_workflow(
    *,
    tenant_input_path: str,
    support_release_manifest_path: str,
    support_release_archive_path: str,
    requested_release_version: str,
    deterministic: bool = True,
    output_root: str = "dist",
) -> dict[str, Any]:
    """Compile tenant workflow input into an SCR_TBox_Release package."""
    request = _parse_request(
        tenant_input_path=tenant_input_path,
        support_release_manifest_path=support_release_manifest_path,
        support_release_archive_path=support_release_archive_path,
        requested_release_version=requested_release_version,
        deterministic=deterministic,
    )

    support_manifest = _validate_support_release_binding(request)
    normalized, _ = _parse_tenant_input(Path(request.tenant_input_path))

    support_artifact_id = str(support_manifest.get("artifact_id", ""))
    support_artifact_version = str(support_manifest.get("artifact_version", ""))
    if not support_artifact_id:
        raise Runtime2CompileError(
            outcome="ABORT",
            reason_code="RC:S2:I7:UNBOUND_REFERENCE",
            stage="S2",
            detail="support release artifact_id is missing",
        )

    release_id = f"SCR_TBox_Release-v{request.requested_release_version}-{_slug(normalized['tenant_id'])}"
    root = _repo_root()
    out_dir = (root / output_root / release_id).resolve()
    payload_dir = out_dir / "_payload"
    evidence_dir = out_dir / "_evidence"
    payload_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)

    compiled_payload = _emit_primitives(
        normalized,
        support_artifact_id=support_artifact_id,
        support_artifact_version=support_artifact_version,
        deterministic=request.deterministic,
    )
    evidence_payload = _emit_evidence(
        normalized,
        support_manifest=support_manifest,
        compile_request=request,
        deterministic=request.deterministic,
    )

    compiled_payload_path = payload_dir / "compiled_primitives.json"
    evidence_payload_path = evidence_dir / "compile_evidence.json"

    compiled_payload_path.write_text(
        json.dumps(compiled_payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    evidence_payload_path.write_text(
        json.dumps(evidence_payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    manifest_path, archive_path = build_scr_tbox_release(
        release_id=release_id,
        artifact_version=request.requested_release_version,
        output_dir=str(out_dir),
        tenant_id=normalized["tenant_id"],
        support_release_manifest_path=request.support_release_manifest_path,
        payload_paths=[str(compiled_payload_path)],
        evidence_paths=[str(evidence_payload_path)],
        deterministic=request.deterministic,
    )

    return {
        "accepted": True,
        "release_id": release_id,
        "manifest_path": manifest_path,
        "archive_path": archive_path,
        "compiled_payload_path": str(compiled_payload_path),
        "evidence_payload_path": str(evidence_payload_path),
        "support_release_artifact_id": support_artifact_id,
        "tenant_id": normalized["tenant_id"],
    }


__all__ = ["Runtime2CompileError", "compile_tenant_workflow"]