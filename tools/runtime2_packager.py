"""Runtime 2 SCR_TBox release packaging helpers."""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any

from tools.packager import create_package


class Runtime2PackagerError(RuntimeError):
    """Raised when Runtime 2 release packaging prerequisites are invalid."""


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize_tenant_id(tenant_id: str) -> str:
    if tenant_id.startswith("cid:"):
        return tenant_id

    digest = hashlib.sha256(tenant_id.encode("utf-8")).hexdigest()[:24]
    return f"cid:tenant-{digest}"


def _normalized_payload_path(path_value: str, base_dir: str) -> str:
    rel = os.path.relpath(path_value, base_dir).replace("\\", "/")
    if rel.startswith("../") or rel == ".." or rel.startswith("/"):
        rel = os.path.basename(path_value)
    return rel


def _load_support_release_manifest(path: Path) -> dict[str, Any]:
    manifest = _read_json(path)
    if manifest.get("manifest_version") != "2.0":
        raise Runtime2PackagerError("Support release manifest must use version 2.0")
    if manifest.get("artifact_type") != "SupportOntologyRelease":
        raise Runtime2PackagerError("Support release manifest artifact_type must be SupportOntologyRelease")
    if manifest.get("tenant_scope") != "global":
        raise Runtime2PackagerError("Support release manifest tenant_scope must be global")
    if not isinstance(manifest.get("artifact_id"), str) or not manifest.get("artifact_id"):
        raise Runtime2PackagerError("Support release manifest must include artifact_id")
    if not isinstance(manifest.get("artifact_version"), str) or not manifest.get("artifact_version"):
        raise Runtime2PackagerError("Support release manifest must include artifact_version")
    return manifest


def build_scr_tbox_release(
    *,
    release_id: str,
    artifact_version: str,
    output_dir: str,
    tenant_id: str,
    support_release_manifest_path: str,
    payload_paths: list[str],
    evidence_paths: list[str],
    deterministic: bool = True,
) -> tuple[str, str]:
    """Build a tenant-scoped SCR_TBox_Release package bound to support lineage."""
    if not payload_paths:
        raise Runtime2PackagerError("At least one payload path is required")
    if not evidence_paths:
        raise Runtime2PackagerError("At least one evidence path is required")

    support_manifest = _load_support_release_manifest(Path(support_release_manifest_path))

    dependencies = [
        {
            "dependency_artifact_id": support_manifest["artifact_id"],
            "dependency_artifact_type": "SupportOntologyRelease",
            "dependency_artifact_version": support_manifest["artifact_version"],
        }
    ]

    base_dir = str(_repo_root())
    primary_file = _normalized_payload_path(payload_paths[0], base_dir)

    issued_at = "1970-01-01T00:00:00+00:00" if deterministic else None

    return create_package(
        release_id=release_id,
        file_paths=payload_paths,
        output_dir=output_dir,
        base_dir=base_dir,
        artifact_type="SCR_TBox_Release",
        artifact_version=artifact_version,
        tenant_scope="tenant",
        tenant_id=_normalize_tenant_id(tenant_id),
        dependencies=dependencies,
        evidence_paths=evidence_paths,
        manifest_version="2.0",
        deterministic=deterministic,
        issued_at=issued_at,
        primary_file=primary_file,
    )


__all__ = ["Runtime2PackagerError", "build_scr_tbox_release"]