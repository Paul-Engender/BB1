"""A packager tool to create release archives and product-boundary manifests."""

from __future__ import annotations

import datetime
import gzip
import hashlib
import io
import json
import mimetypes
import os
import tarfile
import uuid
from pathlib import Path
from typing import Any

from src.cid import mint_cid


def calculate_sha256(filepath: str) -> str:
    """Calculate the SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            sha256.update(chunk)
    return sha256.hexdigest()


def _normalize_arcname(file_path: str, base_dir: str, role: str) -> str:
    rel = os.path.relpath(file_path, base_dir).replace("\\", "/")
    if rel.startswith("../") or rel == ".." or rel.startswith("/"):
        rel = os.path.basename(file_path)

    if role == "evidence" and not rel.startswith("evidence/"):
        rel = f"evidence/{os.path.basename(rel)}"

    return rel


def _normalize_dependencies(dependencies: list[dict[str, Any]] | None) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    for dep in dependencies or []:
        normalized.append(
            {
                "dependency_artifact_id": str(dep["dependency_artifact_id"]),
                "dependency_artifact_type": str(dep["dependency_artifact_type"]),
                "dependency_artifact_version": str(dep["dependency_artifact_version"]),
            }
        )
    return normalized


def _stable_cid_from_digest(digest_hex: str, seed: str) -> str:
    """Create a deterministic UUIDv7-shaped CID from digest and seed."""
    basis = hashlib.sha256(f"{seed}:{digest_hex}".encode("utf-8")).hexdigest()
    timestamp_ms = int(basis[:12], 16) & ((1 << 48) - 1)
    random_bytes = bytes.fromhex(basis[12:32])

    raw = bytearray(16)
    raw[0:6] = timestamp_ms.to_bytes(6, byteorder="big")
    raw[6] = 0x70 | (random_bytes[0] & 0x0F)
    raw[7] = random_bytes[1]
    raw[8] = 0x80 | (random_bytes[2] & 0x3F)
    raw[9:] = random_bytes[3:10]
    stable_uuid = uuid.UUID(bytes=bytes(raw))

    return f"cid:{stable_uuid}-{digest_hex}"


def create_package(
    release_id: str,
    file_paths: list[str],
    output_dir: str,
    base_dir: str = ".",
    *,
    artifact_type: str = "SupportOntologyRelease",
    artifact_version: str = "0.1.0",
    tenant_scope: str = "global",
    tenant_id: str | None = None,
    dependencies: list[dict[str, Any]] | None = None,
    evidence_paths: list[str] | None = None,
    manifest_version: str = "2.0",
    deterministic: bool = False,
    issued_at: str | None = None,
    primary_file: str | None = None,
) -> tuple[str, str]:
    """
    Create a release package containing a manifest and a tar.gz archive.

    Args:
        release_id: Unique release name.
        file_paths: Payload files to include.
        output_dir: Directory where package artifacts are written.
        base_dir: Base directory used to derive in-archive paths.
        artifact_type: Boundary object type.
        artifact_version: Semantic release version.
        tenant_scope: "global" or "tenant".
        tenant_id: Required when tenant_scope="tenant".
        dependencies: Exact upstream dependency bindings.
        evidence_paths: Optional evidence files; stored under /evidence/.
        manifest_version: "2.0" (default) or "1.0" compatibility mode.
        deterministic: Emit deterministic archive metadata and IDs.
        issued_at: Optional timestamp override.
        primary_file: Explicit primary payload file path inside the archive.
    """
    if manifest_version not in {"1.0", "2.0"}:
        raise ValueError("manifest_version must be '1.0' or '2.0'")
    if tenant_scope not in {"global", "tenant"}:
        raise ValueError("tenant_scope must be 'global' or 'tenant'")
    if tenant_scope == "tenant" and not tenant_id:
        raise ValueError("tenant_id is required when tenant_scope='tenant'")
    if tenant_scope == "global" and tenant_id:
        raise ValueError("tenant_id must be omitted when tenant_scope='global'")

    os.makedirs(output_dir, exist_ok=True)

    archive_name = f"{release_id}.tar.gz"
    archive_path = os.path.join(output_dir, archive_name)

    if issued_at:
        issued_at_value = issued_at
    elif deterministic:
        issued_at_value = "1970-01-01T00:00:00+00:00"
    else:
        issued_at_value = datetime.datetime.now(datetime.timezone.utc).isoformat()

    entries: list[tuple[str, str, str]] = []
    for path in file_paths:
        entries.append((path, _normalize_arcname(path, base_dir, "payload"), "payload"))
    for path in evidence_paths or []:
        entries.append((path, _normalize_arcname(path, base_dir, "evidence"), "evidence"))

    seen_arcnames: set[str] = set()
    for _, arcname, _ in entries:
        if arcname in seen_arcnames:
            raise ValueError(f"Duplicate archive path generated: {arcname}")
        seen_arcnames.add(arcname)

    if deterministic:
        entries = sorted(entries, key=lambda x: x[1])

    files_meta: list[dict[str, Any]] = []
    legacy_contents: list[dict[str, str]] = []

    def _append_entry_to_tar(tar: tarfile.TarFile, src_path: str, arcname: str, role: str) -> None:
        src_bytes = Path(src_path).read_bytes()
        digest = hashlib.sha256(src_bytes).hexdigest()

        if deterministic:
            file_cid = _stable_cid_from_digest(digest, arcname)
        else:
            file_cid = mint_cid(src_bytes)

        mime_type = mimetypes.guess_type(src_path)[0] or "application/octet-stream"

        if deterministic:
            info = tarfile.TarInfo(name=arcname)
            info.size = len(src_bytes)
            info.mode = 0o644
            info.mtime = 0
            info.uid = 0
            info.gid = 0
            info.uname = ""
            info.gname = ""
            tar.addfile(info, fileobj=io.BytesIO(src_bytes))
        else:
            tar.add(src_path, arcname=arcname)

        files_meta.append(
            {
                "path": arcname,
                "sha256": digest,
                "cid": file_cid,
                "mime_type": mime_type,
                "role": role,
                "size_bytes": len(src_bytes),
            }
        )
        legacy_contents.append(
            {
                "path": arcname,
                "cid": file_cid,
                "mime_type": mime_type,
            }
        )

    if deterministic:
        with open(archive_path, "wb") as raw_file:
            with gzip.GzipFile(filename="", mode="wb", fileobj=raw_file, mtime=0) as gz_file:
                with tarfile.open(fileobj=gz_file, mode="w", format=tarfile.USTAR_FORMAT) as tar:
                    for src_path, arcname, role in entries:
                        _append_entry_to_tar(tar, src_path, arcname, role)
    else:
        with tarfile.open(archive_path, "w:gz") as tar:
            for src_path, arcname, role in entries:
                _append_entry_to_tar(tar, src_path, arcname, role)

    with open(archive_path, "rb") as f:
        archive_bytes = f.read()
    archive_digest = hashlib.sha256(archive_bytes).hexdigest()

    if deterministic:
        release_cid = _stable_cid_from_digest(archive_digest, release_id)
    else:
        release_cid = mint_cid(archive_bytes)

    manifest: dict[str, Any] = {
        "manifest_version": manifest_version,
        "release_id": release_id,
        "release_cid": release_cid,
    }

    if manifest_version == "1.0":
        manifest.update(
            {
                "issued_at": issued_at_value,
                "contents": legacy_contents,
            }
        )
    else:
        payload_paths = [f["path"] for f in files_meta if f["role"] == "payload"]
        if primary_file is None:
            primary_file_value = payload_paths[0] if payload_paths else None
        else:
            if primary_file not in payload_paths:
                raise ValueError("primary_file must match one of the packaged payload paths")
            primary_file_value = primary_file
            role_rank = {"payload": 0, "evidence": 1}
            files_meta.sort(
                key=lambda item: (
                    role_rank.get(str(item.get("role")), 99),
                    0 if item.get("path") == primary_file_value else 1,
                    str(item.get("path")),
                )
            )
            legacy_contents.sort(
                key=lambda item: (
                    0 if item.get("path") == primary_file_value else 1,
                    str(item.get("path")),
                )
            )
        manifest.update(
            {
                "artifact_type": artifact_type,
                "artifact_version": artifact_version,
                "tenant_scope": tenant_scope,
                "released_at": issued_at_value,
                "primary_file": primary_file_value,
                "dependencies": _normalize_dependencies(dependencies),
                "files": files_meta,
                "contents": legacy_contents,
                "build_deterministic": deterministic,
                "content_digest_sha256": archive_digest,
            }
        )

        artifact_seed = f"{release_id}:{artifact_type}:{artifact_version}:{archive_digest}"
        if deterministic:
            artifact_digest = hashlib.sha256(artifact_seed.encode("utf-8")).hexdigest()
            manifest["artifact_id"] = _stable_cid_from_digest(artifact_digest, artifact_seed)
        else:
            manifest["artifact_id"] = mint_cid(artifact_seed.encode("utf-8"))

        if tenant_scope == "tenant":
            manifest["tenant_id"] = tenant_id

    manifest_path = os.path.join(output_dir, "release_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"Package created at {output_dir}")
    return manifest_path, archive_path


if __name__ == "__main__":
    print("This is a library module. Example usage:")
    print(
        "create_package('v0.1.0', ['src/cid.py'], 'dist/test_package', "
        "base_dir='.', artifact_type='SupportOntologyRelease')"
    )


