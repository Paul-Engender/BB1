import os
import unittest

try:
    from rdflib import Namespace
except ModuleNotFoundError:
    Namespace = None

try:
    from runtime.kernel_gate import get_kernel_graphs, validate_abox
except ModuleNotFoundError:
    get_kernel_graphs = None
    validate_abox = None


@unittest.skipIf(
    Namespace is None or validate_abox is None or get_kernel_graphs is None,
    "rdflib and runtime.kernel_gate are required",
)
class TestOntology(unittest.TestCase):
    KERN = Namespace("https://ontology.engender.co.za/kernel#") if Namespace is not None else None

    @staticmethod
    def _combined_examples() -> str:
        examples_dir = os.path.join(os.path.dirname(__file__), "..", "ontology", "examples")
        combined = []
        for example_file in sorted(os.listdir(examples_dir)):
            if example_file.endswith(".ttl"):
                file_path = os.path.join(examples_dir, example_file)
                with open(file_path, "r", encoding="utf-8") as f:
                    combined.append(f.read())
        return "\n".join(combined)

    def test_example_abox_conforms_to_shacl(self):
        conforms, _, results_text = validate_abox(self._combined_examples())
        self.assertTrue(conforms, f"Example ABox does not conform to SHACL shapes:\n{results_text}")

    def test_kernel_terms_are_in_kernel_namespace(self):
        tbox_graph, _ = get_kernel_graphs()

        owl = Namespace("http://www.w3.org/2002/07/owl#")
        rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        owl_class = owl.Class
        rdf_property = rdf.Property
        owl_object_property = owl.ObjectProperty
        owl_datatype_property = owl.DatatypeProperty

        violations = []

        for s, _, o in tbox_graph.triples((None, None, owl_class)):
            if not str(s).startswith(str(self.KERN)):
                violations.append(f"Class '{s}' is not in the '{self.KERN}' namespace.")

        for s, _, o in tbox_graph.triples((None, None, owl_object_property)):
            if not str(s).startswith(str(self.KERN)):
                violations.append(f"ObjectProperty '{s}' is not in the '{self.KERN}' namespace.")

        for s, _, o in tbox_graph.triples((None, None, owl_datatype_property)):
            if not str(s).startswith(str(self.KERN)):
                violations.append(f"DatatypeProperty '{s}' is not in the '{self.KERN}' namespace.")

        for s, _, o in tbox_graph.triples((None, None, rdf_property)):
            is_object_property = (s, None, owl_object_property) in tbox_graph
            is_datatype_property = (s, None, owl_datatype_property) in tbox_graph
            if not is_object_property and not is_datatype_property and not str(s).startswith(str(self.KERN)):
                violations.append(f"Generic Property '{s}' is not in the '{self.KERN}' namespace.")

        self.assertFalse(violations, "\n" + "\n".join(violations))


if __name__ == "__main__":
    unittest.main()

