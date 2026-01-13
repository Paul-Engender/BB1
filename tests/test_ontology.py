import pytest
from rdflib import Graph, Namespace
import os

from runtime.kernel_gate import validate_abox, get_kernel_graphs

# Define the expected kernel namespace
KERN = Namespace("https://ontology.engender.co.za/kernel#")

@pytest.fixture(scope="module")
def example_abox_payload():
    """
    Combines all example ABox files into a single Turtle string for validation.
    """
    examples_dir = os.path.join(os.path.dirname(__file__), '..', 'ontology', 'examples')
    combined_abox_content = ""
    for example_file in sorted(os.listdir(examples_dir)): # Sort for consistent order
        if example_file.endswith(".ttl"):
            file_path = os.path.join(examples_dir, example_file)
            with open(file_path, 'r', encoding='utf-8') as f:
                combined_abox_content += f.read() + "\n"
    return combined_abox_content

def test_example_abox_conforms_to_shacl(example_abox_payload):
    """
    Tests that the combined example ABox conforms to the kernel SHACL shapes.
    """
    conforms, _, results_text = validate_abox(example_abox_payload)
    assert conforms is True, f"Example ABox does not conform to SHACL shapes:\n{results_text}"

def test_kernel_terms_are_in_kernel_namespace():
    """
    Tests that all defined classes and properties in kernel.ttl are within the kern: namespace.
    """
    tbox_graph, _ = get_kernel_graphs()

    # Define common RDF/OWL types for classes and properties
    OWL_CLASS = Namespace("http://www.w3.org/2002/07/owl#").Class
    RDF_PROPERTY = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#").Property
    OWL_OBJECT_PROPERTY = Namespace("http://www.w3.org/2002/07/owl#").ObjectProperty
    OWL_DATATYPE_PROPERTY = Namespace("http://www.w3.org/2002/07/owl#").DatatypeProperty

    violations = []

    # Check classes
    for s, p, o in tbox_graph.triples((None, None, OWL_CLASS)):
        if not str(s).startswith(str(KERN)):
            violations.append(f"Class '{s}' is not in the '{KERN}' namespace.")
            
    # Check properties (ObjectProperty, DatatypeProperty, and generic rdf:Property)
    for s, p, o in tbox_graph.triples((None, None, OWL_OBJECT_PROPERTY)):
        if not str(s).startswith(str(KERN)):
            violations.append(f"ObjectProperty '{s}' is not in the '{KERN}' namespace.")

    for s, p, o in tbox_graph.triples((None, None, OWL_DATATYPE_PROPERTY)):
        if not str(s).startswith(str(KERN)):
            violations.append(f"DatatypeProperty '{s}' is not in the '{KERN}' namespace.")

    # Generic properties (for those not explicitly declared as owl:ObjectProperty or owl:DatatypeProperty)
    # This might catch some rdfs:subClassOf if not careful, so will check if subject is also a property type
    for s, p, o in tbox_graph.triples((None, None, RDF_PROPERTY)):
        # Ensure it's not already covered by OWL_OBJECT_PROPERTY or OWL_DATATYPE_PROPERTY
        is_object_property = (s, None, OWL_OBJECT_PROPERTY) in tbox_graph
        is_datatype_property = (s, None, OWL_DATATYPE_PROPERTY) in tbox_graph
        if not is_object_property and not is_datatype_property and not str(s).startswith(str(KERN)):
             violations.append(f"Generic Property '{s}' is not in the '{KERN}' namespace.")
    
    assert not violations, "\n" + "\n".join(violations)
