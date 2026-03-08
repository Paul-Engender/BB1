import os
import unittest

try:
    from runtime.kernel_gate import validate_abox
except ModuleNotFoundError:
    validate_abox = None


@unittest.skipIf(validate_abox is None, "runtime.kernel_gate not available in this workspace")
class TestNegativeSHACL(unittest.TestCase):
    @staticmethod
    def _read_example(filename: str) -> str:
        file_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "ontology",
            "negative_examples",
            filename,
        )
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def test_targetref_missing_isaboutentity_fails(self):
        data = self._read_example("targetref_missing_isaboutentity.ttl")
        conforms, _, results_text = validate_abox(data)
        self.assertFalse(conforms, f"Expected validation failure, got success:\n{results_text}")
        self.assertIn("Less than 1 values on", results_text)
        self.assertIn("kern:isAboutEntity", results_text)

    def test_targetref_two_isaboutentity_fails(self):
        data = self._read_example("targetref_two_isaboutentity.ttl")
        conforms, _, results_text = validate_abox(data)
        self.assertFalse(conforms, f"Expected validation failure, got success:\n{results_text}")
        self.assertIn("More than 1 values on", results_text)
        self.assertIn("kern:isAboutEntity", results_text)

    def test_stipulation_two_stipulateson_fails(self):
        data = self._read_example("stipulation_two_stipulateson.ttl")
        conforms, _, results_text = validate_abox(data)
        self.assertFalse(conforms, f"Expected validation failure, got success:\n{results_text}")
        self.assertIn("More than 1 values on", results_text)
        self.assertIn("kern:stipulatesOn", results_text)

    def test_evaluator_missing_measurementspec_fails(self):
        data = self._read_example("evaluator_missing_measurementspec.ttl")
        conforms, _, results_text = validate_abox(data)
        self.assertFalse(conforms, f"Expected validation failure, got success:\n{results_text}")
        self.assertIn("ex:NegativeEvaluatorStipulation_1", results_text)

    def test_restriction_missing_ruleexpression_fails(self):
        data = self._read_example("restriction_missing_ruleexpression.ttl")
        conforms, _, results_text = validate_abox(data)
        self.assertFalse(conforms, f"Expected validation failure, got success:\n{results_text}")
        self.assertIn("ex:NegativeRestrictionStipulation_1", results_text)

    def test_promotionrecord_two_truthassertions_fails(self):
        data = self._read_example("promotionrecord_two_truthassertions.ttl")
        conforms, _, results_text = validate_abox(data)
        self.assertFalse(conforms, f"Expected validation failure, got success:\n{results_text}")
        self.assertIn("More than 1 values on", results_text)
        self.assertIn("kern:producesAcceptedAssertion", results_text)

    def test_targetset_missing_selection_basis_fails(self):
        data = self._read_example("targetset_missing_selection_basis.ttl")
        conforms, _, results_text = validate_abox(data)
        self.assertFalse(conforms, f"Expected validation failure, got success:\n{results_text}")
        self.assertIn("kern:targetSelectionBasis", results_text)

    def test_actioneffectbinding_missing_effect_ref_fails(self):
        data = self._read_example("actioneffectbinding_missing_effect_ref.ttl")
        conforms, _, results_text = validate_abox(data)
        self.assertFalse(conforms, f"Expected validation failure, got success:\n{results_text}")
        self.assertIn("kern:effectRef", results_text)

    def test_eligibilitysemantic_missing_status_fails(self):
        data = self._read_example("eligibilitysemantic_missing_status.ttl")
        conforms, _, results_text = validate_abox(data)
        self.assertFalse(conforms, f"Expected validation failure, got success:\n{results_text}")
        self.assertIn("kern:eligibilityStatusRef", results_text)

    def test_tenantworkflow_missing_aioperable_fails(self):
        data = self._read_example("tenantworkflow_missing_aioperable.ttl")
        conforms, _, results_text = validate_abox(data)
        self.assertFalse(conforms, f"Expected validation failure, got success:\n{results_text}")
        self.assertIn("kern:aiOperable", results_text)



    def test_roleassignment_missing_assignsagent_fails(self):
        data = self._read_example("roleassignment_missing_assignsagent.ttl")
        conforms, _, results_text = validate_abox(data)
        self.assertFalse(conforms, f"Expected validation failure, got success:\n{results_text}")
        self.assertIn("kern:assignsAgent", results_text)

    def test_validationspec_missing_method_fails(self):
        data = self._read_example("validationspec_missing_method.ttl")
        conforms, _, results_text = validate_abox(data)
        self.assertFalse(conforms, f"Expected validation failure, got success:\n{results_text}")
        self.assertIn("kern:validationMethod", results_text)
if __name__ == "__main__":
    unittest.main()

