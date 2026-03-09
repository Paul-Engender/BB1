"""Tests for the packager tool."""

import json
import os
import shutil
import tarfile
import unittest
from pathlib import Path

try:
    from tools.packager import calculate_sha256, create_package
except ModuleNotFoundError:
    calculate_sha256 = None
    create_package = None


@unittest.skipIf(create_package is None, "tools.packager module not available in this workspace")
class TestPackager(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(__file__).resolve().parent / "_tmp_packager"
        shutil.rmtree(self.test_dir, ignore_errors=True)
        self.source_dir = self.test_dir / "source"
        self.output_dir = self.test_dir / "output"
        self.source_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.file1_path = self.source_dir / "file1.txt"
        self.file2_path = self.source_dir / "subdir" / "file2.log"
        self.file2_path.parent.mkdir(parents=True, exist_ok=True)

        self.file1_path.write_text("This is file 1.", encoding="utf-8")
        self.file2_path.write_text("This is file 2, in a subdirectory.", encoding="utf-8")

        self.evidence_path = self.source_dir / "compile_evidence.json"
        self.evidence_path.write_text('{"result":"ok"}', encoding="utf-8")

        self.files_to_package = [str(self.file1_path), str(self.file2_path)]

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_product_manifest_fields_and_evidence_hashes(self):
        release_id = "test-release-v2"

        manifest_path, archive_path = create_package(
            release_id,
            self.files_to_package,
            str(self.output_dir),
            base_dir=str(self.source_dir),
            artifact_type="SCR_TBox_Release",
            artifact_version="0.1.0",
            tenant_scope="tenant",
            tenant_id="cid:tenant-001-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            dependencies=[
                {
                    "dependency_artifact_id": "cid:support-001-bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
                    "dependency_artifact_type": "SupportOntologyRelease",
                    "dependency_artifact_version": "0.1.0",
                }
            ],
            evidence_paths=[str(self.evidence_path)],
            primary_file="file1.txt",
        )

        self.assertTrue(os.path.exists(manifest_path))
        self.assertTrue(os.path.exists(archive_path))

        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        self.assertEqual(manifest["manifest_version"], "2.0")
        self.assertEqual(manifest["release_id"], release_id)
        self.assertEqual(manifest["artifact_type"], "SCR_TBox_Release")
        self.assertEqual(manifest["tenant_scope"], "tenant")
        self.assertIn("tenant_id", manifest)
        self.assertEqual(manifest["primary_file"], "file1.txt")

        expected_archive_hash = calculate_sha256(archive_path)
        self.assertIn(expected_archive_hash, manifest["release_cid"])

        files = {item["path"]: item for item in manifest["files"]}
        self.assertIn("file1.txt", files)
        self.assertIn("subdir/file2.log", files)
        self.assertIn("evidence/compile_evidence.json", files)
        self.assertEqual(files["evidence/compile_evidence.json"]["role"], "evidence")

        expected_hashes = {
            "file1.txt": calculate_sha256(str(self.file1_path)),
            "subdir/file2.log": calculate_sha256(str(self.file2_path)),
            "evidence/compile_evidence.json": calculate_sha256(str(self.evidence_path)),
        }
        for path, digest in expected_hashes.items():
            self.assertEqual(files[path]["sha256"], digest)

    def test_archive_contents(self):
        release_id = "archive-test-v2"
        _, archive_path = create_package(
            release_id,
            self.files_to_package,
            str(self.output_dir),
            base_dir=str(self.source_dir),
            artifact_type="SupportOntologyRelease",
            artifact_version="0.1.0",
            tenant_scope="global",
            dependencies=[],
            evidence_paths=[str(self.evidence_path)],
        )

        with tarfile.open(archive_path, "r:gz") as tar:
            archived_files = tar.getnames()
            normalized = {p.replace("\\", "/") for p in archived_files}
            self.assertIn("file1.txt", normalized)
            self.assertIn("subdir/file2.log", normalized)
            self.assertIn("evidence/compile_evidence.json", normalized)

    def test_tenant_scope_requires_tenant_id(self):
        with self.assertRaises(ValueError):
            create_package(
                "invalid-tenant-pkg",
                self.files_to_package,
                str(self.output_dir),
                base_dir=str(self.source_dir),
                artifact_type="SCR_TBox_Release",
                tenant_scope="tenant",
            )


if __name__ == "__main__":
    unittest.main()


