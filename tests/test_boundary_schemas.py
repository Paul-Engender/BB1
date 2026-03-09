import json
import unittest
from pathlib import Path


class BoundarySchemaTests(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parent.parent
        self.release_schema_path = self.repo_root / "schemas" / "release_manifest.schema.json"
        self.runtime_schema_path = self.repo_root / "schemas" / "runtime_load_manifest.schema.json"

    def test_release_schema_declares_v2_product_fields(self):
        schema = json.loads(self.release_schema_path.read_text(encoding="utf-8-sig"))
        props = schema["properties"]

        for field in (
            "artifact_id",
            "artifact_type",
            "artifact_version",
            "tenant_scope",
            "dependencies",
            "files",
        ):
            self.assertIn(field, props)

        self.assertIn("allOf", schema)
        self.assertTrue(any("if" in clause and "then" in clause for clause in schema["allOf"]))

    def test_runtime_load_schema_declares_v2_product_fields(self):
        schema = json.loads(self.runtime_schema_path.read_text(encoding="utf-8-sig"))
        props = schema["properties"]

        for field in (
            "manifest_id",
            "runtime_instance_id",
            "tenant_id",
            "tbox_release_id",
            "support_release_id",
            "load_mode",
            "declared_at",
            "declared_by",
        ):
            self.assertIn(field, props)

        self.assertIn("allOf", schema)

    def test_legacy_fixtures_remain_v1_compatible(self):
        release_fixture = json.loads((self.repo_root / "fixtures" / "release_manifest_fixture.json").read_text(encoding="utf-8-sig"))
        load_fixture = json.loads((self.repo_root / "fixtures" / "runtime_load_manifest_fixture.json").read_text(encoding="utf-8-sig"))

        self.assertEqual(release_fixture.get("manifest_version"), "1.0")
        self.assertEqual(load_fixture.get("manifest_version"), "1.0")


if __name__ == "__main__":
    unittest.main()
