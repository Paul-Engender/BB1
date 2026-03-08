import json
import unittest
from pathlib import Path

from tools.validate_kernel_project_bundle import validate_bundle


class KernelProjectBundleValidatorTests(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parent.parent
        self.examples = self.repo_root / "bootstrap" / "kernel_pm" / "examples"

    def _load(self, name: str) -> dict:
        path = self.examples / name
        return json.loads(path.read_text(encoding="utf-8"))

    def test_minimal_bundle_passes(self):
        bundle = self._load("kernel_project_bundle_minimal.json")
        errors = validate_bundle(bundle)
        self.assertEqual([], errors)

    def test_missing_assigns_agent_fails(self):
        bundle = self._load("kernel_project_bundle_invalid_missing_assigns_agent.json")
        errors = validate_bundle(bundle)
        self.assertTrue(any("assignsAgent" in error for error in errors), errors)

    def test_execution_record_is_without_evidence_fails(self):
        bundle = self._load("kernel_project_bundle_minimal.json")
        for obj in bundle["objects"]:
            if obj.get("kind") == "TaskExecutionRecord":
                obj["evidence_refs"] = []
                break

        errors = validate_bundle(bundle)
        self.assertTrue(any("status IS requires non-empty evidence_refs" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()