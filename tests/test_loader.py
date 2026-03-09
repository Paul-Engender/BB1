import hashlib
import io
import json
import shutil
import tarfile
import unittest
import uuid
from pathlib import Path

from src.cid import mint_cid
from src.loader import verify_and_load, verify_and_load_runtime3


_TMP_ROOT = Path(__file__).resolve().parent / "_tmp_loader_runs"


def _fresh_dir(name: str) -> Path:
    _TMP_ROOT.mkdir(parents=True, exist_ok=True)
    path = _TMP_ROOT / f"{name}-{uuid.uuid4().hex}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class LoaderSecurityTests(unittest.TestCase):
    def _write_archive(self, archive_path: Path, files: dict[str, bytes]) -> bytes:
        archive_path.parent.mkdir(parents=True, exist_ok=True)
        with tarfile.open(str(archive_path), "w:gz") as tar:
            for name, content in files.items():
                info = tarfile.TarInfo(name=name)
                info.size = len(content)
                tar.addfile(info, io.BytesIO(content))
        return archive_path.read_bytes()

    def _write_v2_manifest(
        self,
        manifest_path: Path,
        archive_bytes: bytes,
        files: dict[str, bytes],
        *,
        artifact_type: str = "SupportOntologyRelease",
        tenant_scope: str = "global",
        tenant_id: str | None = None,
        dependencies: list[dict[str, str]] | None = None,
    ) -> dict:
        file_entries = []
        for path, content in files.items():
            role = "evidence" if path.startswith("evidence/") else "payload"
            file_entries.append(
                {
                    "path": path,
                    "sha256": _sha256(content),
                    "cid": mint_cid(content),
                    "role": role,
                }
            )

        manifest = {
            "manifest_version": "2.0",
            "release_id": "release-v2",
            "release_cid": mint_cid(archive_bytes),
            "artifact_id": mint_cid(b"artifact-v2"),
            "artifact_type": artifact_type,
            "artifact_version": "0.1.0",
            "tenant_scope": tenant_scope,
            "released_at": "2026-03-07T00:00:00Z",
            "primary_file": next(iter(files.keys())),
            "dependencies": dependencies or [],
            "files": file_entries,
            "contents": [
                {
                    "path": p,
                    "cid": mint_cid(c),
                    "mime_type": "application/octet-stream",
                }
                for p, c in files.items()
            ],
        }
        if tenant_scope == "tenant":
            manifest["tenant_id"] = tenant_id or mint_cid(b"tenant")

        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        return manifest

    def test_rejects_unexpected_archive_file(self) -> None:
        base = _fresh_dir("unexpected")
        archive_path = base / "release.tar.gz"
        manifest_path = base / "manifest.json"
        load_dir = base / "out"

        files = {
            "good.txt": b"ok",
            "extra.txt": b"unexpected",
        }
        archive_bytes = self._write_archive(archive_path, files)

        self._write_v2_manifest(
            manifest_path,
            archive_bytes,
            {"good.txt": b"ok"},
        )

        ok, msg = verify_and_load(str(manifest_path), str(archive_path), str(load_dir))
        self.assertFalse(ok)
        self.assertIn("unexpected file", msg.lower())

    def test_rejects_traversal_path(self) -> None:
        base = _fresh_dir("traversal")
        archive_path = base / "release.tar.gz"
        manifest_path = base / "manifest.json"
        load_dir = base / "out"

        files = {
            "../escape.txt": b"bad",
        }
        archive_bytes = self._write_archive(archive_path, files)

        self._write_v2_manifest(manifest_path, archive_bytes, files)

        ok, msg = verify_and_load(str(manifest_path), str(archive_path), str(load_dir))
        self.assertFalse(ok)
        self.assertIn("unsafe path", msg.lower())

    def test_loads_valid_package_v2(self) -> None:
        base = _fresh_dir("valid")
        archive_path = base / "release.tar.gz"
        manifest_path = base / "manifest.json"
        runtime_load_manifest_path = base / "runtime_load_manifest.json"
        load_dir = base / "out"

        support_release_id = mint_cid(b"support-release")
        tenant_id = mint_cid(b"tenant-a")
        files = {
            "dir/a.txt": b"a",
            "dir/b.txt": b"b",
            "evidence/compile.json": b"{}",
        }
        archive_bytes = self._write_archive(archive_path, files)

        manifest = self._write_v2_manifest(
            manifest_path,
            archive_bytes,
            files,
            artifact_type="SCR_TBox_Release",
            tenant_scope="tenant",
            tenant_id=tenant_id,
            dependencies=[
                {
                    "dependency_artifact_id": support_release_id,
                    "dependency_artifact_type": "SupportOntologyRelease",
                    "dependency_artifact_version": "0.1.0",
                }
            ],
        )

        runtime_load_manifest = {
            "manifest_version": "2.0",
            "manifest_id": mint_cid(b"load-manifest"),
            "runtime_instance_id": "runtime-1",
            "tenant_id": tenant_id,
            "tbox_release_id": manifest["artifact_id"],
            "tbox_release_version": manifest["artifact_version"],
            "support_release_id": support_release_id,
            "load_mode": "active",
            "declared_at": "2026-03-07T00:00:00Z",
            "declared_by": "did:system:operator",
        }
        runtime_load_manifest_path.write_text(json.dumps(runtime_load_manifest), encoding="utf-8")

        ok, msg = verify_and_load_runtime3(
            str(manifest_path),
            str(archive_path),
            str(load_dir),
            str(runtime_load_manifest_path),
        )
        self.assertTrue(ok, msg)
        self.assertEqual((load_dir / "dir" / "a.txt").read_bytes(), b"a")
        self.assertEqual((load_dir / "dir" / "b.txt").read_bytes(), b"b")

    def test_replaces_stale_files_when_loading_valid_package_v2(self) -> None:
        base = _fresh_dir("stale_replace")
        archive_path = base / "release.tar.gz"
        manifest_path = base / "manifest.json"
        load_dir = base / "out"

        files = {
            "ontology/kernel.ttl": b"kernel",
            "evidence/release.json": b"{}",
        }
        archive_bytes = self._write_archive(archive_path, files)
        self._write_v2_manifest(manifest_path, archive_bytes, files)

        stale_file = load_dir / "ontology" / "support.ttl"
        stale_file.parent.mkdir(parents=True, exist_ok=True)
        stale_file.write_text("retired", encoding="utf-8")

        ok, msg = verify_and_load(str(manifest_path), str(archive_path), str(load_dir))
        self.assertTrue(ok, msg)
        self.assertFalse(stale_file.exists())
        self.assertEqual((load_dir / "ontology" / "kernel.ttl").read_bytes(), b"kernel")

    def test_rejects_scr_tbox_via_generic_loader(self) -> None:
        base = _fresh_dir("scr_via_generic")
        archive_path = base / "release.tar.gz"
        manifest_path = base / "manifest.json"
        load_dir = base / "out"

        tenant_id = mint_cid(b"tenant-generic")
        support_release_id = mint_cid(b"support-generic")
        files = {
            "payload/main.ttl": b"payload",
            "evidence/compile.json": b"{}",
        }
        archive_bytes = self._write_archive(archive_path, files)

        self._write_v2_manifest(
            manifest_path,
            archive_bytes,
            files,
            artifact_type="SCR_TBox_Release",
            tenant_scope="tenant",
            tenant_id=tenant_id,
            dependencies=[
                {
                    "dependency_artifact_id": support_release_id,
                    "dependency_artifact_type": "SupportOntologyRelease",
                    "dependency_artifact_version": "0.1.0",
                }
            ],
        )

        ok, msg = verify_and_load(str(manifest_path), str(archive_path), str(load_dir))
        self.assertFalse(ok)
        self.assertIn("verify_and_load_runtime3", msg)

    def test_rejects_support_release_via_runtime3_loader(self) -> None:
        base = _fresh_dir("support_via_runtime3")
        archive_path = base / "release.tar.gz"
        manifest_path = base / "manifest.json"
        runtime_load_manifest_path = base / "runtime_load_manifest.json"
        load_dir = base / "out"

        files = {
            "ontology/kernel.ttl": b"k",
        }
        archive_bytes = self._write_archive(archive_path, files)
        support_manifest = self._write_v2_manifest(
            manifest_path,
            archive_bytes,
            files,
            artifact_type="SupportOntologyRelease",
            tenant_scope="global",
        )

        runtime_load_manifest = {
            "manifest_version": "2.0",
            "manifest_id": mint_cid(b"load-manifest-support"),
            "runtime_instance_id": "runtime-1",
            "tenant_id": mint_cid(b"tenant-a"),
            "tbox_release_id": support_manifest["artifact_id"],
            "tbox_release_version": support_manifest["artifact_version"],
            "support_release_id": mint_cid(b"support-release"),
            "load_mode": "active",
            "declared_at": "2026-03-07T00:00:00Z",
            "declared_by": "did:system:operator",
        }
        runtime_load_manifest_path.write_text(json.dumps(runtime_load_manifest), encoding="utf-8")

        ok, msg = verify_and_load_runtime3(
            str(manifest_path),
            str(archive_path),
            str(load_dir),
            str(runtime_load_manifest_path),
        )
        self.assertFalse(ok)
        self.assertIn("scr_tbox_release", msg.lower())


if __name__ == "__main__":
    unittest.main()
