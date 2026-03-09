import hashlib
import io
import json
import shutil
import tarfile
import unittest
from pathlib import Path

from src.cid import mint_cid
from src.loader import verify_and_load_runtime3


_TMP_ROOT = Path(__file__).resolve().parent / "_tmp_boundary"


def _fresh_dir(name: str) -> Path:
    path = _TMP_ROOT / name
    shutil.rmtree(path, ignore_errors=True)
    path.mkdir(parents=True, exist_ok=True)
    return path


class BoundaryLoadDisciplineTests(unittest.TestCase):
    def _write_archive(self, archive_path: Path, files: dict[str, bytes]) -> bytes:
        archive_path.parent.mkdir(parents=True, exist_ok=True)
        with tarfile.open(str(archive_path), "w:gz") as tar:
            for name, content in files.items():
                info = tarfile.TarInfo(name=name)
                info.size = len(content)
                tar.addfile(info, io.BytesIO(content))
        return archive_path.read_bytes()

    def _write_manifest(
        self,
        manifest_path: Path,
        archive_bytes: bytes,
        files: list[dict],
        *,
        tenant_id: str,
        support_release_id: str,
        with_support_dep: bool = True,
    ) -> dict:
        deps = []
        if with_support_dep:
            deps.append(
                {
                    "dependency_artifact_id": support_release_id,
                    "dependency_artifact_type": "SupportOntologyRelease",
                    "dependency_artifact_version": "0.1.0",
                }
            )

        manifest = {
            "manifest_version": "2.0",
            "release_id": "scr-tbox-v1",
            "release_cid": mint_cid(archive_bytes),
            "artifact_id": mint_cid(b"scr-tbox-artifact"),
            "artifact_type": "SCR_TBox_Release",
            "artifact_version": "0.1.0",
            "tenant_scope": "tenant",
            "tenant_id": tenant_id,
            "released_at": "2026-03-07T00:00:00Z",
            "primary_file": files[0]["path"],
            "dependencies": deps,
            "files": files,
        }
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        return manifest

    def _write_load_manifest(
        self,
        load_manifest_path: Path,
        *,
        tenant_id: str,
        tbox_release_id: str,
        support_release_id: str,
    ) -> None:
        load_manifest = {
            "manifest_version": "2.0",
            "manifest_id": mint_cid(b"load-manifest"),
            "runtime_instance_id": "runtime-1",
            "tenant_id": tenant_id,
            "tbox_release_id": tbox_release_id,
            "tbox_release_version": "0.1.0",
            "support_release_id": support_release_id,
            "load_mode": "active",
            "declared_at": "2026-03-07T00:00:00Z",
            "declared_by": "did:system:operator",
        }
        load_manifest_path.write_text(json.dumps(load_manifest), encoding="utf-8")

    def test_rejects_scr_tbox_missing_evidence(self) -> None:
        base = _fresh_dir("missing_evidence")
        archive_path = base / "release.tar.gz"
        manifest_path = base / "release_manifest.json"
        load_manifest_path = base / "runtime_load_manifest.json"
        load_dir = base / "out"

        payload = b"payload"
        archive_bytes = self._write_archive(archive_path, {"payload/main.ttl": payload})
        files = [
            {
                "path": "payload/main.ttl",
                "sha256": hashlib.sha256(payload).hexdigest(),
                "cid": mint_cid(payload),
                "role": "payload",
            }
        ]
        tenant_id = mint_cid(b"tenant-a")
        support_release_id = mint_cid(b"support")
        manifest = self._write_manifest(
            manifest_path,
            archive_bytes,
            files,
            tenant_id=tenant_id,
            support_release_id=support_release_id,
        )
        self._write_load_manifest(
            load_manifest_path,
            tenant_id=tenant_id,
            tbox_release_id=manifest["artifact_id"],
            support_release_id=support_release_id,
        )

        ok, msg = verify_and_load_runtime3(
            str(manifest_path),
            str(archive_path),
            str(load_dir),
            str(load_manifest_path),
        )
        self.assertFalse(ok)
        self.assertIn("evidence", msg.lower())

    def test_rejects_tenant_mismatch(self) -> None:
        base = _fresh_dir("tenant_mismatch")
        archive_path = base / "release.tar.gz"
        manifest_path = base / "release_manifest.json"
        load_manifest_path = base / "runtime_load_manifest.json"
        load_dir = base / "out"

        payload = b"payload"
        evidence = b"{}"
        archive_bytes = self._write_archive(
            archive_path,
            {
                "payload/main.ttl": payload,
                "evidence/compile.json": evidence,
            },
        )
        files = [
            {
                "path": "payload/main.ttl",
                "sha256": hashlib.sha256(payload).hexdigest(),
                "cid": mint_cid(payload),
                "role": "payload",
            },
            {
                "path": "evidence/compile.json",
                "sha256": hashlib.sha256(evidence).hexdigest(),
                "cid": mint_cid(evidence),
                "role": "evidence",
            },
        ]
        tenant_id = mint_cid(b"tenant-a")
        support_release_id = mint_cid(b"support")
        manifest = self._write_manifest(
            manifest_path,
            archive_bytes,
            files,
            tenant_id=tenant_id,
            support_release_id=support_release_id,
        )
        self._write_load_manifest(
            load_manifest_path,
            tenant_id=mint_cid(b"tenant-b"),
            tbox_release_id=manifest["artifact_id"],
            support_release_id=support_release_id,
        )

        ok, msg = verify_and_load_runtime3(
            str(manifest_path),
            str(archive_path),
            str(load_dir),
            str(load_manifest_path),
        )
        self.assertFalse(ok)
        self.assertIn("tenant mismatch", msg.lower())

    def test_rejects_missing_support_dependency_binding(self) -> None:
        base = _fresh_dir("missing_dependency")
        archive_path = base / "release.tar.gz"
        manifest_path = base / "release_manifest.json"
        load_manifest_path = base / "runtime_load_manifest.json"
        load_dir = base / "out"

        payload = b"payload"
        evidence = b"{}"
        archive_bytes = self._write_archive(
            archive_path,
            {
                "payload/main.ttl": payload,
                "evidence/compile.json": evidence,
            },
        )
        files = [
            {
                "path": "payload/main.ttl",
                "sha256": hashlib.sha256(payload).hexdigest(),
                "cid": mint_cid(payload),
                "role": "payload",
            },
            {
                "path": "evidence/compile.json",
                "sha256": hashlib.sha256(evidence).hexdigest(),
                "cid": mint_cid(evidence),
                "role": "evidence",
            },
        ]
        tenant_id = mint_cid(b"tenant-a")
        support_release_id = mint_cid(b"support")
        manifest = self._write_manifest(
            manifest_path,
            archive_bytes,
            files,
            tenant_id=tenant_id,
            support_release_id=support_release_id,
            with_support_dep=False,
        )
        self._write_load_manifest(
            load_manifest_path,
            tenant_id=tenant_id,
            tbox_release_id=manifest["artifact_id"],
            support_release_id=support_release_id,
        )

        ok, msg = verify_and_load_runtime3(
            str(manifest_path),
            str(archive_path),
            str(load_dir),
            str(load_manifest_path),
        )
        self.assertFalse(ok)
        self.assertIn("dependency", msg.lower())


if __name__ == "__main__":
    unittest.main()
