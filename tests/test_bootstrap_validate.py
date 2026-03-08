import csv
import importlib.util
import shutil
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "bootstrap_validate.py"
SPEC = importlib.util.spec_from_file_location("bootstrap_validate", MODULE_PATH)
bootstrap_validate = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(bootstrap_validate)


class PlanningControlsValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        base_tmp = Path(__file__).resolve().parent / "_tmp_bootstrap_validate"
        base_tmp.mkdir(parents=True, exist_ok=True)
        self.repo_root = base_tmp / self._testMethodName
        shutil.rmtree(self.repo_root, ignore_errors=True)
        self.repo_root.mkdir(parents=True, exist_ok=True)
        self.plans_root = self.repo_root / "bootstrap" / "plans"
        for rel_dir in (
            "bootstrap/plans/active",
            "bootstrap/plans/archive",
            "bootstrap/plans/manifests",
            "bootstrap/plans/programs",
            "bootstrap/plans/proposals_backlog",
            "bootstrap/plans/reference",
        ):
            (self.repo_root / rel_dir).mkdir(parents=True, exist_ok=True)

        (self.plans_root / "PLAN_INDEX.md").write_text("# index\n", encoding="utf-8")
        (self.plans_root / "phase1_execution_plan.md").write_text("# exec\n", encoding="utf-8")
        (self.plans_root / "phase1_plan_items.csv").write_text(
            'plan_item_id,title,status,owner,notes\nP1-001,Example,ACTIVE,paul,\n',
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.repo_root, ignore_errors=True)

    def _write_manifest(self, rows: list[dict[str, str]]) -> Path:
        path = self.repo_root / "bootstrap" / "plans" / "manifests" / "plans_manifest.csv"
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "doc_id",
                    "plane",
                    "scope",
                    "doc_type",
                    "lifecycle_state",
                    "operational_role",
                    "path",
                    "effective_date",
                    "supersedes",
                    "replaced_by",
                    "notes",
                ],
            )
            writer.writeheader()
            writer.writerows(rows)
        return path

    def _base_manifest_rows(self) -> list[dict[str, str]]:
        return [
            {
                "doc_id": "DOC-PLAN-INDEX",
                "plane": "implementation",
                "scope": "repo-planning",
                "doc_type": "index",
                "lifecycle_state": "ACTIVE",
                "operational_role": "ORIENTATION",
                "path": "bootstrap/plans/PLAN_INDEX.md",
                "effective_date": "2026-03-08",
                "supersedes": "",
                "replaced_by": "",
                "notes": "",
            },
            {
                "doc_id": "DOC-PHASE1-EXEC",
                "plane": "implementation",
                "scope": "repo-execution",
                "doc_type": "execution_plan",
                "lifecycle_state": "ACTIVE",
                "operational_role": "ACTIVE_CONTROL",
                "path": "bootstrap/plans/phase1_execution_plan.md",
                "effective_date": "2026-03-08",
                "supersedes": "",
                "replaced_by": "",
                "notes": "",
            },
            {
                "doc_id": "DOC-PHASE1-PLAN-ITEMS",
                "plane": "implementation",
                "scope": "repo-execution",
                "doc_type": "plan_items",
                "lifecycle_state": "ACTIVE",
                "operational_role": "ACTIVE_CONTROL",
                "path": "bootstrap/plans/phase1_plan_items.csv",
                "effective_date": "2026-03-08",
                "supersedes": "",
                "replaced_by": "",
                "notes": "",
            },
            {
                "doc_id": "DOC-PLANS-MANIFEST",
                "plane": "implementation",
                "scope": "repo-planning",
                "doc_type": "manifest",
                "lifecycle_state": "ACTIVE",
                "operational_role": "ACTIVE_CONTROL",
                "path": "bootstrap/plans/manifests/plans_manifest.csv",
                "effective_date": "2026-03-08",
                "supersedes": "",
                "replaced_by": "",
                "notes": "",
            },
        ]

    def test_planning_controls_accept_valid_layout(self) -> None:
        manifest_path = self._write_manifest(self._base_manifest_rows())

        errors, warnings, rows = bootstrap_validate._validate_planning_controls(
            self.repo_root,
            manifest_path,
        )

        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])
        self.assertEqual(len(rows), 4)

    def test_planning_controls_reject_unexpected_root_file(self) -> None:
        manifest_path = self._write_manifest(self._base_manifest_rows())
        (self.plans_root / "scratch_notes.md").write_text("temp\n", encoding="utf-8")

        errors, warnings, _ = bootstrap_validate._validate_planning_controls(
            self.repo_root,
            manifest_path,
        )

        self.assertEqual(warnings, [])
        self.assertTrue(
            any("unexpected root-level planning file 'scratch_notes.md'" in err for err in errors)
        )

    def test_planning_controls_reject_duplicate_active_control_scope_and_type(self) -> None:
        rows = self._base_manifest_rows()
        extra_path = self.repo_root / "bootstrap" / "plans" / "active" / "extra_execution_plan.md"
        extra_path.write_text("# duplicate\n", encoding="utf-8")
        rows.append(
            {
                "doc_id": "DOC-EXEC-DUPLICATE",
                "plane": "implementation",
                "scope": "repo-execution",
                "doc_type": "execution_plan",
                "lifecycle_state": "ACTIVE",
                "operational_role": "ACTIVE_CONTROL",
                "path": "bootstrap/plans/active/extra_execution_plan.md",
                "effective_date": "2026-03-08",
                "supersedes": "",
                "replaced_by": "",
                "notes": "",
            }
        )
        manifest_path = self._write_manifest(rows)

        errors, _, _ = bootstrap_validate._validate_planning_controls(
            self.repo_root,
            manifest_path,
        )

        self.assertTrue(
            any("duplicate ACTIVE_CONTROL for scope 'repo-execution' and doc_type 'execution_plan'" in err for err in errors)
        )


class KernelPmProjectionLockTests(unittest.TestCase):
    def setUp(self) -> None:
        base_tmp = Path(__file__).resolve().parent / "_tmp_bootstrap_validate"
        base_tmp.mkdir(parents=True, exist_ok=True)
        self.repo_root = base_tmp / self._testMethodName
        shutil.rmtree(self.repo_root, ignore_errors=True)
        self.repo_root.mkdir(parents=True, exist_ok=True)

        for rel_dir in (
            "bootstrap/plans/active",
            "bootstrap/kernel_pm/projections",
        ):
            (self.repo_root / rel_dir).mkdir(parents=True, exist_ok=True)

        (self.repo_root / "bootstrap/plans/active/kernel_pm_authority_switch_policy_v1.md").write_text(
            "active\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.repo_root, ignore_errors=True)

    def _write_csv(self, rel: str, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
        path = self.repo_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def _write_projection_set(self) -> None:
        self._write_csv(
            "bootstrap/kernel_pm/projections/phase2_plan_items_projection.csv",
            ["plan_item_id", "title", "status", "owner", "notes", "source_object_id"],
            [
                {
                    "plan_item_id": "P2-004",
                    "title": "Runtime 3 minimum viable tenant runtime (successor WS-04)",
                    "status": "PLANNED",
                    "owner": "paul",
                    "notes": "Tenant-scoped runtime baseline for first vertical slice",
                    "source_object_id": "workstream.p2-004",
                }
            ],
        )
        self._write_csv(
            "bootstrap/kernel_pm/projections/task_ledger_projection.csv",
            [
                "task_id",
                "plan_item_id",
                "status",
                "owner",
                "validation_method",
                "evidence_row_ids",
                "dependencies",
                "output_path",
                "notes",
                "source_object_id",
            ],
            [
                {
                    "task_id": "TASK-30.1",
                    "plan_item_id": "P2-004",
                    "status": "TO_DO",
                    "owner": "paul",
                    "validation_method": "python tools/bootstrap_validate.py --execute-validation-methods dry-run",
                    "evidence_row_ids": "EP-30",
                    "dependencies": "TASK-29.1",
                    "output_path": "bootstrap/plans/programs/p2_004_runtime3_baseline_decomposition_v1.md",
                    "notes": "Defines minimal Runtime 3 tenant runtime baseline decomposition for first slice.",
                    "source_object_id": "task.spec.30.1",
                }
            ],
        )
        self._write_csv(
            "bootstrap/kernel_pm/projections/evidence_register_projection.csv",
            ["evidence_row_id", "status", "gate_criterion", "source_task_ids", "notes", "source_object_id"],
            [
                {
                    "evidence_row_id": "EP-30",
                    "status": "TO_DO",
                    "gate_criterion": "M4 Runtime 3 executes deterministic tenant-scoped operational flow",
                    "source_task_ids": "TASK-30.1",
                    "notes": "",
                    "source_object_id": "evidence.ep30",
                }
            ],
        )

    def _authoritative_rows(self) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
        plan_rows = [
            {
                "plan_item_id": "P2-004",
                "title": "Runtime 3 minimum viable tenant runtime (successor WS-04)",
                "status": "PLANNED",
                "owner": "paul",
                "notes": "Tenant-scoped runtime baseline for first vertical slice",
            }
        ]
        task_rows = [
            {
                "task_id": "TASK-30.1",
                "plan_item_id": "P2-004",
                "bootstrap_task_id": "BPL-30",
                "task_name": "Define Runtime 3 baseline decomposition controls",
                "status": "TO_DO",
                "owner": "paul",
                "canonical_refs": "",
                "evidence_row_ids": "EP-30",
                "dependencies": "TASK-29.1",
                "input_refs": "",
                "output_paths": "bootstrap/plans/programs/p2_004_runtime3_baseline_decomposition_v1.md",
                "validation_method": "python tools/bootstrap_validate.py --execute-validation-methods dry-run",
                "validation_evidence": "",
                "notes": "Defines minimal Runtime 3 tenant runtime baseline decomposition for first slice.",
            }
        ]
        evidence_rows = [
            {
                "evidence_row_id": "EP-30",
                "gate_criterion": "M4 Runtime 3 executes deterministic tenant-scoped operational flow",
                "canonical_refs": "",
                "required_artifact": "",
                "location": "",
                "integrity": "",
                "validation_method": "",
                "validation_evidence": "",
                "status": "TO_DO",
                "verification_owner": "paul",
                "source_task_ids": "TASK-30.1",
                "notes": "",
            }
        ]
        return plan_rows, task_rows, evidence_rows

    def test_projection_lock_accepts_matching_forward_rows(self) -> None:
        self._write_projection_set()
        plan_rows, task_rows, evidence_rows = self._authoritative_rows()

        errors, warnings = bootstrap_validate._validate_kernel_pm_projection_lock(
            self.repo_root,
            plan_rows,
            task_rows,
            evidence_rows,
        )

        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_projection_lock_rejects_mismatched_forward_task_status(self) -> None:
        self._write_projection_set()
        plan_rows, task_rows, evidence_rows = self._authoritative_rows()
        task_rows[0]["status"] = "DONE"

        errors, _ = bootstrap_validate._validate_kernel_pm_projection_lock(
            self.repo_root,
            plan_rows,
            task_rows,
            evidence_rows,
        )

        self.assertTrue(any("field 'status'" in err for err in errors))


if __name__ == "__main__":
    unittest.main()

