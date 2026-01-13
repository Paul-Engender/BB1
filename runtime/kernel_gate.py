from rdflib import Graph
from pyshacl import validate
import os
from functools import lru_cache

@lru_cache(maxsize=1)
def get_kernel_graphs():
    """
    Loads the kernel TBox and SHACL shapes from file.
    Uses lru_cache to ensure this is only done once.
    """
    # --- Load TBox (kernel ontology) ---
    kernel_tbox_path = os.path.join(os.path.dirname(__file__), '..', 'ontology', 'kernel.ttl')
    print(f"Loading TBox: {kernel_tbox_path}")
    tbox_graph = Graph()
    with open(kernel_tbox_path, 'r', encoding='utf-8') as f:
        tbox_graph.parse(data=f.read(), format="turtle")

    # --- Load SHACL shapes ---
    shacl_graph_path = os.path.join(os.path.dirname(__file__), '..', 'ontology', 'kernel.shacl.ttl')
    print(f"Loading SHACL shapes: {shacl_graph_path}")
    shacl_graph = Graph()
    with open(shacl_graph_path, 'r', encoding='utf-8') as f:
        shacl_graph.parse(data=f.read(), format="turtle")
        
    return tbox_graph, shacl_graph

def validate_abox(abox_turtle: str):
    """
    Validates a given ABox (in Turtle format) against the kernel TBox and SHACL shapes.

    :param abox_turtle: A string containing the ABox graph in Turtle format.
    :return: A tuple of (conforms: bool, results_graph: Graph, results_text: str)
    """
    tbox_graph, shacl_graph = get_kernel_graphs()

    # Create a new graph for the validation containing the TBox and the ABox
    data_graph = Graph()
    data_graph += tbox_graph
    data_graph.parse(data=abox_turtle, format="turtle")

    # --- Validate ---
    conforms, results_graph, results_text = validate(
        data_graph,
        shacl_graph=shacl_graph,
        ont_graph=None,
        inference='none',
        abort_on_first=False,
        allow_warnings=True,
        meta_shacl=False,
        advanced=False,
        js=False,
        debug=False
    )
    
    return conforms, results_graph, results_text
