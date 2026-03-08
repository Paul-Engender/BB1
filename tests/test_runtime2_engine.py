import json
import shutil
import unittest
from pathlib import Path

from runtime.runtime2_engine import Runtime2CompileError, compile_tenant_workflow


class Runtime2EngineTests(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parent.parent
        self.tmp_root = Path(__file__).resolve().parent / "_tmp_runtime2"
        shutil.rmtree(self.tmp_root, ignore_errors=True)
        self.tmp_root.mkdir(parents=True, exist_ok=True)

        self.support_manifest = self.repo_root / "dist" / "SupportOntologyRelease-v0.2.0" / "release_manifest.json"
        self.support_archive = self.repo_root / "dist" / "SupportOntologyRelease-v0.2.0" / "SupportOntologyRelease-v0.2.0.tar.gz"

    def tearDown(self):
        shutil.rmtree(self.tmp_root, ignore_errors=True)

    def test_compile_smoke(self):
        result = compile_tenant_workflow(
            tenant_input_path=str(self.repo_root / "ontology" / "examples" / "example-runtime2-input.ttl"),
            support_release_manifest_path=str(self.support_manifest),
            support_release_archive_path=str(self.support_archive),
            requested_release_version="0.1.0-smoke",
            deterministic=True,
            output_root=str(self.tmp_root),
        )

        self.assertTrue(result["accepted"])
        self.assertTrue(Path(result["manifest_path"]).exists())
        self.assertTrue(Path(result["archive_path"]).exists())
        self.assertTrue(Path(result["compiled_payload_path"]).exists())
        self.assertTrue(Path(result["evidence_payload_path"]).exists())

    def test_rejects_non_admissible_input(self):
        with self.assertRaises(Runtime2CompileError) as ctx:
            compile_tenant_workflow(
                tenant_input_path=str(self.repo_root / "ontology" / "negative_examples" / "tenantworkflow_missing_aioperable.ttl"),
                support_release_manifest_path=str(self.support_manifest),
                support_release_archive_path=str(self.support_archive),
                requested_release_version="0.1.0-deny",
                deterministic=True,
                output_root=str(self.tmp_root),
            )

        err = ctx.exception
        self.assertIn(err.outcome, {"ABORT", "DENY", "QUARANTINE"})
        self.assertIn("AI_OPERABLE", err.reason_code)

    def test_compile_emits_scr_tbox_release_manifest(self):
        result = compile_tenant_workflow(
            tenant_input_path=str(self.repo_root / "ontology" / "examples" / "example-runtime2-input.ttl"),
            support_release_manifest_path=str(self.support_manifest),
            support_release_archive_path=str(self.support_archive),
            requested_release_version="0.1.0-manifest",
            deterministic=True,
            output_root=str(self.tmp_root),
        )

        manifest = json.loads(Path(result["manifest_path"]).read_text(encoding="utf-8"))
        support_manifest = json.loads(self.support_manifest.read_text(encoding="utf-8"))

        self.assertEqual(manifest["manifest_version"], "2.0")
        self.assertEqual(manifest["artifact_type"], "SCR_TBox_Release")
        self.assertEqual(manifest["tenant_scope"], "tenant")
        self.assertTrue(str(manifest.get("tenant_id", "")).startswith("cid:"))
        self.assertEqual(len(manifest["dependencies"]), 1)
        self.assertEqual(
            manifest["dependencies"][0]["dependency_artifact_id"],
            support_manifest["artifact_id"],
        )

        roles = [item.get("role") for item in manifest["files"]]
        self.assertIn("payload", roles)
        self.assertIn("evidence", roles)


if __name__ == "__main__":
    unittest.main()