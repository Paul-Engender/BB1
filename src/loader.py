"""Verifier and loader for release packages with boundary-discipline enforcement."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tarfile
from pathlib import Path
from typing import Any, Tuple

try:
    from .cid import validate_cid
except ImportError:
    from cid import validate_cid


def _is_safe_member_path(member_name: str) -> bool:
    """Return True when tar member path is relative and traversal-safe."""
    if not member_name:
        return False

    member_path = Path(member_name)
    if member_path.is_absolute():
        return False

    normalized = os.path.normpath(member_name)
    if normalized.startswith(".."):
        return False

    drive, _ = os.path.splitdrive(normalized)
    if drive:
        return False

    return True


def _read_json(path: str) -> Tuple[bool, str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return (True, "ok", json.load(f))
    except (OSError, json.JSONDecodeError) as e:
        return (False, f"Failed to read or parse JSON: {e}", None)


def _validate_manifest_structure(manifest: Any) -> Tuple[bool, str, str]:
    """Validate manifest structure and return mode (v1/v2)."""
    if not isinstance(manifest, dict):
        return (False, "Manifest root must be a JSON object.", "")

    release_cid = manifest.get("release_cid")
    if not isinstance(release_cid, str):
        return (False, "Manifest field 'release_cid' must be a string.", "")

    version = manifest.get("manifest_version", "1.0")
    if version == "2.0":
        required = [
            "artifact_id",
            "artifact_type",
            "artifact_version",
            "tenant_scope",
            "files",
            "dependencies",
        ]
        for field in required:
            if field not in manifest:
                return (False, f"Manifest v2.0 missing required field: {field}", "")

        if manifest.get("artifact_type") not in {"SupportOntologyRelease", "SCR_TBox_Release"}:
            return (False, "Manifest v2.0 has invalid artifact_type.", "")

        tenant_scope = manifest.get("tenant_scope")
        if tenant_scope not in {"global", "tenant"}:
            return (False, "Manifest v2.0 has invalid tenant_scope.", "")
        if tenant_scope == "tenant" and not isinstance(manifest.get("tenant_id"), str):
            return (False, "Manifest v2.0 tenant scope requires tenant_id.", "")
        if tenant_scope == "global" and "tenant_id" in manifest:
            return (False, "Manifest v2.0 global scope must not include tenant_id.", "")

        files = manifest.get("files")
        if not isinstance(files, list) or not files:
            return (False, "Manifest v2.0 field 'files' must be a non-empty list.", "")

        seen_paths: set[str] = set()
        evidence_count = 0
        for idx, item in enumerate(files):
            if not isinstance(item, dict):
                return (False, f"Manifest files[{idx}] must be an object.", "")

            path_value = item.get("path")
            sha256_value = item.get("sha256")
            role_value = item.get("role")

            if not isinstance(path_value, str) or not path_value:
                return (False, f"Manifest files[{idx}].path must be a non-empty string.", "")
            if not _is_safe_member_path(path_value):
                return (False, f"Unsafe path in manifest files: {path_value}", "")
            if path_value in seen_paths:
                return (False, f"Duplicate path in manifest files: {path_value}", "")
            seen_paths.add(path_value)

            if not isinstance(sha256_value, str) or len(sha256_value) != 64:
                return (False, f"Manifest files[{idx}].sha256 must be a 64-char hex string.", "")
            try:
                int(sha256_value, 16)
            except ValueError:
                return (False, f"Manifest files[{idx}].sha256 must be hexadecimal.", "")

            if role_value == "evidence" or str(path_value).startswith("evidence/"):
                evidence_count += 1

        if manifest.get("artifact_type") == "SCR_TBox_Release" and evidence_count < 1:
            return (False, "SCR_TBox_Release manifest must include at least one evidence file.", "")

        deps = manifest.get("dependencies")
        if not isinstance(deps, list):
            return (False, "Manifest v2.0 field 'dependencies' must be a list.", "")
        for idx, dep in enumerate(deps):
            if not isinstance(dep, dict):
                return (False, f"Manifest dependencies[{idx}] must be an object.", "")
            for field in ("dependency_artifact_id", "dependency_artifact_type", "dependency_artifact_version"):
                if not isinstance(dep.get(field), str) or not dep.get(field):
                    return (False, f"Manifest dependencies[{idx}] missing field: {field}", "")

        return (True, "ok", "v2")

    contents = manifest.get("contents")
    if not isinstance(contents, list):
        return (False, "Manifest field 'contents' must be a list.", "")

    seen_paths: set[str] = set()
    for idx, item in enumerate(contents):
        if not isinstance(item, dict):
            return (False, f"Manifest contents[{idx}] must be an object.", "")

        path_value = item.get("path")
        cid_value = item.get("cid")
        if not isinstance(path_value, str) or not path_value:
            return (False, f"Manifest contents[{idx}].path must be a non-empty string.", "")
        if not isinstance(cid_value, str):
            return (False, f"Manifest contents[{idx}].cid must be a string.", "")

        if not _is_safe_member_path(path_value):
            return (False, f"Unsafe path in manifest: {path_value}", "")

        if path_value in seen_paths:
            return (False, f"Duplicate path in manifest: {path_value}", "")
        seen_paths.add(path_value)

    return (True, "ok", "v1")


def _validate_runtime_load_manifest(manifest: Any) -> Tuple[bool, str]:
    if not isinstance(manifest, dict):
        return (False, "Runtime load manifest must be a JSON object.")

    version = manifest.get("manifest_version")
    if version != "2.0":
        return (False, "Runtime load manifest must use manifest_version '2.0'.")

    required = [
        "manifest_id",
        "runtime_instance_id",
        "tenant_id",
        "tbox_release_id",
        "tbox_release_version",
        "support_release_id",
        "load_mode",
        "declared_at",
        "declared_by",
    ]
    for field in required:
        value = manifest.get(field)
        if not isinstance(value, str) or not value:
            return (False, f"Runtime load manifest missing required field: {field}")

    if manifest["load_mode"] not in {"active", "safe", "hold"}:
        return (False, "Runtime load manifest load_mode is invalid.")

    return (True, "ok")


def _verify_and_load_internal(
    manifest_path: str,
    archive_path: str,
    load_dir: str,
    runtime_load_manifest_path: str | None = None,
    *,
    runtime3_mode: bool = False,
) -> Tuple[bool, str]:
    """
    Verify a release package against its manifest and safely unpack it.

    Returns:
        A tuple of (success, message).
    """
    ok, msg, manifest = _read_json(manifest_path)
    if not ok:
        return (False, msg)

    ok, reason, mode = _validate_manifest_structure(manifest)
    if not ok:
        return (False, reason)

    release_cid = manifest["release_cid"]

    try:
        with open(archive_path, "rb") as f:
            archive_bytes = f.read()
    except OSError as e:
        return (False, f"Failed to read archive: {e}")

    if not validate_cid(release_cid, archive_bytes):
        return (False, "Archive integrity check failed. The .tar.gz file is tampered.")

    if runtime_load_manifest_path and not runtime3_mode:
        return (
            False,
            "Runtime load manifest binding must use verify_and_load_runtime3().",
        )

    if runtime3_mode and mode != "v2":
        return (False, "Runtime 3 load binding requires a v2 release manifest.")

    if mode == "v2":
        artifact_type = manifest.get("artifact_type")
        if runtime3_mode:
            if artifact_type != "SCR_TBox_Release":
                return (
                    False,
                    "Runtime 3 load binding only admits SCR_TBox_Release artifacts.",
                )
            if not runtime_load_manifest_path:
                return (
                    False,
                    "SCR_TBox_Release runtime loading requires SCR_Runtime_LoadManifest.",
                )
        elif artifact_type == "SCR_TBox_Release":
            return (
                False,
                "SCR_TBox_Release load requires verify_and_load_runtime3() with SCR_Runtime_LoadManifest.",
            )

    if mode == "v2" and runtime3_mode:
        ok, msg, load_manifest = _read_json(runtime_load_manifest_path)
        if not ok:
            return (False, msg)

        ok, reason = _validate_runtime_load_manifest(load_manifest)
        if not ok:
            return (False, reason)

        if load_manifest["tenant_id"] != manifest.get("tenant_id"):
            return (False, "Tenant mismatch between release manifest and runtime load manifest.")
        if load_manifest["tbox_release_id"] != manifest.get("artifact_id"):
            return (False, "Load manifest release ID does not match SCR_TBox_Release artifact_id.")
        if load_manifest["tbox_release_version"] != manifest.get("artifact_version"):
            return (False, "Load manifest release version does not match SCR_TBox_Release artifact_version.")

        expected_support = load_manifest["support_release_id"]
        dependencies = manifest.get("dependencies", [])
        if not any(
            dep.get("dependency_artifact_type") == "SupportOntologyRelease"
            and dep.get("dependency_artifact_id") == expected_support
            for dep in dependencies
        ):
            return (False, "Required SupportOntologyRelease dependency binding is missing.")

    try:
        with tarfile.open(archive_path, "r:gz") as tar:
            members = [m for m in tar.getmembers() if m.isfile()]

            for member in members:
                if not _is_safe_member_path(member.name):
                    return (False, f"Unsafe archive path detected: {member.name}")

            if mode == "v2":
                declared = manifest["files"]
                manifest_paths = {item["path"] for item in declared}
            else:
                declared = manifest["contents"]
                manifest_paths = {item["path"] for item in declared}

            archive_paths = {m.name for m in members}

            missing = manifest_paths - archive_paths
            if missing:
                return (False, f"Manifest file missing from archive: {sorted(missing)[0]}")

            unexpected = archive_paths - manifest_paths
            if unexpected:
                return (False, f"Archive contains unexpected file: {sorted(unexpected)[0]}")

            if mode == "v2":
                for item in declared:
                    file_info = tar.getmember(item["path"])
                    extracted_file = tar.extractfile(file_info)
                    if extracted_file is None:
                        return (False, f"File {item['path']} listed in manifest not found in archive.")

                    content_bytes = extracted_file.read()
                    digest = hashlib.sha256(content_bytes).hexdigest()
                    if digest != item["sha256"]:
                        return (False, f"Digest mismatch for file: {item['path']}")

                    cid_value = item.get("cid")
                    if isinstance(cid_value, str) and cid_value and not validate_cid(cid_value, content_bytes):
                        return (False, f"CID mismatch for file: {item['path']}")
            else:
                for item in declared:
                    file_info = tar.getmember(item["path"])
                    extracted_file = tar.extractfile(file_info)
                    if extracted_file is None:
                        return (False, f"File {item['path']} listed in manifest not found in archive.")

                    content_bytes = extracted_file.read()
                    if not validate_cid(item["cid"], content_bytes):
                        return (False, f"Tampering detected in file: {item['path']}. Hash mismatch.")
    except (OSError, KeyError, tarfile.TarError) as e:
        return (False, f"Error processing archive: {e}")

    load_path = Path(load_dir)

    try:
        if load_path.exists():
            if load_path.is_dir():
                shutil.rmtree(load_path)
            else:
                load_path.unlink()

        load_path.mkdir(parents=True, exist_ok=True)

        with tarfile.open(archive_path, "r:gz") as tar:
            for item in declared:
                member = tar.getmember(item["path"])
                if not _is_safe_member_path(member.name):
                    return (False, f"Unsafe archive path detected at extraction: {member.name}")
                extracted_file = tar.extractfile(member)
                if extracted_file is None:
                    return (False, f"File {item['path']} listed in manifest not found in archive.")
                target_path = load_path / item["path"]
                target_path.parent.mkdir(parents=True, exist_ok=True)
                with target_path.open("wb") as f:
                    shutil.copyfileobj(extracted_file, f)
    except (OSError, KeyError, tarfile.TarError) as e:
        return (False, f"Failed to unpack archive after verification: {e}")

    return (True, f"Package verified and loaded successfully into {load_dir}")



def verify_and_load(
    manifest_path: str,
    archive_path: str,
    load_dir: str,
) -> Tuple[bool, str]:
    """Generic package verification + extraction (non-Runtime-3)."""
    return _verify_and_load_internal(
        manifest_path=manifest_path,
        archive_path=archive_path,
        load_dir=load_dir,
        runtime_load_manifest_path=None,
        runtime3_mode=False,
    )


def verify_and_load_runtime3(
    manifest_path: str,
    archive_path: str,
    load_dir: str,
    runtime_load_manifest_path: str,
) -> Tuple[bool, str]:
    """Runtime-3 load-binding gate for tenant SCR_TBox releases."""
    return _verify_and_load_internal(
        manifest_path=manifest_path,
        archive_path=archive_path,
        load_dir=load_dir,
        runtime_load_manifest_path=runtime_load_manifest_path,
        runtime3_mode=True,
    )

