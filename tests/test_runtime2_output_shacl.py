import os
import unittest

try:
    from runtime.kernel_gate import validate_abox
except ModuleNotFoundError:
    validate_abox = None


@unittest.skipIf(validate_abox is None, "runtime.kernel_gate not available in this workspace")
class Runtime2OutputShaclTests(unittest.TestCase):
    @staticmethod
    def _read_fixture(folder: str, filename: str) -> str:
        file_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "ontology",
            folder,
            filename,
        )
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def test_compiled_output_positive_fixture_conforms(self):
        data = self._read_fixture("examples", "example-runtime2-compiled-output.ttl")
        conforms, _, results_text = validate_abox(data)
        self.assertTrue(conforms, f"Expected compiled output fixture to conform:\n{results_text}")

    def test_compiledprimitive_missing_support_release_ref_fails(self):
        data = self._read_fixture("negative_examples", "compiledprimitive_missing_support_release_ref.ttl")
        conforms, _, results_text = validate_abox(data)
        self.assertFalse(conforms, f"Expected validation failure, got success:\n{results_text}")
        self.assertIn("kern:supportReleaseRef", results_text)

    def test_compilepolicy_missing_reason_category_fails(self):
        data = self._read_fixture("negative_examples", "compilepolicy_missing_reason_category.ttl")
        conforms, _, results_text = validate_abox(data)
        self.assertFalse(conforms, f"Expected validation failure, got success:\n{results_text}")
        self.assertIn("kern:reasonCodeCategoryRef", results_text)

    def test_tenantworkflow_with_constraints_fails(self):
        data = self._read_fixture("negative_examples", "tenantworkflow_with_constraints.ttl")
        conforms, _, results_text = validate_abox(data)
        self.assertFalse(conforms, f"Expected validation failure, got success:\n{results_text}")
        self.assertIn("kern:constraints", results_text)

    def test_compiledprimitive_with_constraints_fails(self):
        data = self._read_fixture("negative_examples", "compiledprimitive_with_constraints.ttl")
        conforms, _, results_text = validate_abox(data)
        self.assertFalse(conforms, f"Expected validation failure, got success:\n{results_text}")
        self.assertIn("kern:constraints", results_text)


if __name__ == "__main__":
    unittest.main()
