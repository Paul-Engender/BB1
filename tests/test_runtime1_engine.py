import json
import shutil
import unittest
from pathlib import Path

from src.loader import verify_and_load

try:
    from runtime.runtime1_engine import build_support_ontology_release, evaluate_release_candidate
except ModuleNotFoundError:
    build_support_ontology_release = None
    evaluate_release_candidate = None


@unittest.skipIf(
    build_support_ontology_release is None or evaluate_release_candidate is None,
    "runtime.runtime1_engine dependencies unavailable",
)
class Runtime1EngineTests(unittest.TestCase):
    def setUp(self):
        self.tmp_root = Path(__file__).resolve().parent / "_tmp_runtime1"
        shutil.rmtree(self.tmp_root, ignore_errors=True)
        self.tmp_root.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.tmp_root, ignore_errors=True)

    def test_evaluate_release_candidate(self):
        report = evaluate_release_candidate()
        self.assertIn("accepted", report)
        self.assertIn("summary", report)
        self.assertGreater(report["summary"]["total_checks"], 0)
        self.assertEqual(report["summary"]["failed"], 0)
        self.assertTrue(report["accepted"])
        parse_paths = sorted(
            check["path"]
            for check in report["checks"]
            if check.get("kind") == "parse"
        )
        self.assertEqual(parse_paths, ["ontology/kernel.shacl.ttl", "ontology/kernel.ttl"])
        self.assertNotIn("ontology/support.ttl", parse_paths)

    def test_build_support_release_contains_evidence(self):
        result = build_support_ontology_release(
            release_version="0.2.0-test",
            output_root=str(self.tmp_root / "dist"),
        )

        manifest_path = Path(result["manifest_path"])
        archive_path = Path(result["archive_path"])
        self.assertTrue(manifest_path.exists())
        self.assertTrue(archive_path.exists())

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["manifest_version"], "2.0")
        self.assertEqual(manifest["artifact_type"], "SupportOntologyRelease")
        self.assertEqual(manifest["tenant_scope"], "global")
        self.assertEqual(manifest["primary_file"], "ontology/kernel.ttl")

        payload_files = [f["path"] for f in manifest["files"] if f["role"] == "payload"]
        self.assertEqual(payload_files, ["ontology/kernel.ttl", "ontology/kernel.shacl.ttl"])
        self.assertNotIn("ontology/support.ttl", payload_files)

        evidence_files = [f for f in manifest["files"] if f["role"] == "evidence"]
        self.assertGreaterEqual(len(evidence_files), 1)
        for item in evidence_files:
            self.assertTrue(item["path"].startswith("evidence/"))

    def test_loader_verifies_support_release_package(self):
        result = build_support_ontology_release(
            release_version="0.2.0-verify",
            output_root=str(self.tmp_root / "dist"),
        )
        load_dir = self.tmp_root / "loaded"

        ok, msg = verify_and_load(
            manifest_path=result["manifest_path"],
            archive_path=result["archive_path"],
            load_dir=str(load_dir),
        )
        self.assertTrue(ok, msg)
        self.assertTrue((load_dir / "ontology" / "kernel.ttl").exists())
        self.assertTrue((load_dir / "ontology" / "kernel.shacl.ttl").exists())
        self.assertFalse((load_dir / "ontology" / "support.ttl").exists())

        evidence_dir = load_dir / "evidence"
        self.assertTrue(evidence_dir.exists())
        self.assertGreater(len(list(evidence_dir.glob("*.json*"))), 0)

    def test_build_is_deterministic_when_requested(self):
        result_a = build_support_ontology_release(
            release_version="0.2.0-deterministic",
            output_root=str(self.tmp_root / "dist_a"),
            deterministic=True,
            run_promotion_gate=False,
        )
        result_b = build_support_ontology_release(
            release_version="0.2.0-deterministic",
            output_root=str(self.tmp_root / "dist_b"),
            deterministic=True,
            run_promotion_gate=False,
        )

        manifest_a = json.loads(Path(result_a["manifest_path"]).read_text(encoding="utf-8"))
        manifest_b = json.loads(Path(result_b["manifest_path"]).read_text(encoding="utf-8"))

        self.assertEqual(manifest_a["content_digest_sha256"], manifest_b["content_digest_sha256"])
        self.assertEqual(manifest_a["release_cid"], manifest_b["release_cid"])
        self.assertEqual(manifest_a["artifact_id"], manifest_b["artifact_id"])

    def test_writes_promotion_decision_file(self):
        result = build_support_ontology_release(
            release_version="0.2.0-promote",
            output_root=str(self.tmp_root / "dist_promote"),
            deterministic=True,
            run_promotion_gate=True,
        )

        promotion_path = Path(result["promotion_decision_path"])
        self.assertTrue(promotion_path.exists())

        decision = json.loads(promotion_path.read_text(encoding="utf-8"))
        self.assertEqual(decision["decision_type"], "Runtime1PromotionDecision")
        self.assertEqual(decision["decision"], "APPROVED")

    def test_promotion_gate_replaces_stale_verify_dir(self):
        output_root = self.tmp_root / "dist_reuse"
        release_version = "0.2.0-reuse"
        verify_dir = output_root / f"SupportOntologyRelease-v{release_version}" / "_promotion_verify"
        stale_file = verify_dir / "ontology" / "support.ttl"
        stale_file.parent.mkdir(parents=True, exist_ok=True)
        stale_file.write_text("stale", encoding="utf-8")

        build_support_ontology_release(
            release_version=release_version,
            output_root=str(output_root),
            deterministic=True,
            run_promotion_gate=True,
        )

        self.assertFalse(stale_file.exists())
        self.assertTrue((verify_dir / "ontology" / "kernel.ttl").exists())
        self.assertTrue((verify_dir / "ontology" / "kernel.shacl.ttl").exists())


if __name__ == "__main__":
    unittest.main()
