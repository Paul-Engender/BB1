import csv
import json
import shutil
import unittest
from pathlib import Path

from tools.project_kernel_bundle_to_csv import project_bundle


class KernelBundleProjectionTests(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parent.parent
        self.bundle_path = (
            self.repo_root
            / "bootstrap"
            / "kernel_pm"
            / "bundles"
            / "open_frontier_kernel_project_bundle_v1.json"
        )
        self.tmp_dir = self.repo_root / "bootstrap" / "kernel_pm" / "_test_projection_output"
        shutil.rmtree(self.tmp_dir, ignore_errors=True)
        self.tmp_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def _read_csv(self, path: Path):
        with path.open("r", encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))

    def test_projection_writes_expected_files(self):
        bundle = json.loads(self.bundle_path.read_text(encoding="utf-8"))
        written = project_bundle(bundle, self.tmp_dir)

        names = sorted(path.name for path in written)
        self.assertEqual(
            names,
            [
                "evidence_register_projection.csv",
                "phase2_plan_items_projection.csv",
                "task_ledger_projection.csv",
            ],
        )

    def test_projection_contains_open_frontier_rows(self):
        bundle = json.loads(self.bundle_path.read_text(encoding="utf-8"))
        project_bundle(bundle, self.tmp_dir)

        plan_rows = self._read_csv(self.tmp_dir / "phase2_plan_items_projection.csv")
        task_rows = self._read_csv(self.tmp_dir / "task_ledger_projection.csv")
        evidence_rows = self._read_csv(self.tmp_dir / "evidence_register_projection.csv")

        plan_ids = {row["plan_item_id"] for row in plan_rows}
        self.assertTrue({"P2-004", "P2-005", "P2-006"}.issubset(plan_ids))

        task_ids = {row["task_id"] for row in task_rows}
        self.assertTrue({"TASK-30.1", "TASK-31.1", "TASK-32.1"}.issubset(task_ids))

        evidence_ids = {row["evidence_row_id"] for row in evidence_rows}
        self.assertTrue({"EP-30", "EP-31", "EP-32"}.issubset(evidence_ids))


if __name__ == "__main__":
    unittest.main()