import os
import subprocess
from pathlib import Path
from rdflib import Graph, RDF, RDFS, OWL, URIRef, Namespace

KERN = Namespace("https://ontology.engender.co.za/kernel#")
XSD  = Namespace("http://www.w3.org/2001/XMLSchema#")

def qname(g: Graph, uri: URIRef) -> str:
    """Stable human-readable name for a URI."""
    try:
        return g.namespace_manager.normalizeUri(uri)
    except Exception:
        return str(uri)

def is_kern(uri: URIRef) -> bool:
    return isinstance(uri, URIRef) and str(uri).startswith(str(KERN))

def render_dot_to_svg(dot_path: Path, svg_path: Path) -> None:
    subprocess.run(["dot", "-Tsvg", str(dot_path), "-o", str(svg_path)], check=True)

def generate_class_hierarchy(g: Graph, out_dir: Path) -> None:
    # Collect classes (limit to kern: classes for readability)
    classes = set(g.subjects(RDF.type, OWL.Class))
    # Also include anything in subClassOf triples
    for child, parent in g.subject_objects(RDFS.subClassOf):
        if isinstance(child, URIRef):
            classes.add(child)
        if isinstance(parent, URIRef):
            classes.add(parent)

    # Filter to kern only (optional, but recommended for kernel diagrams)
    classes = {c for c in classes if is_kern(c)}

    edges = set()
    for child, parent in g.subject_objects(RDFS.subClassOf):
        if is_kern(child) and is_kern(parent):
            edges.add((child, parent))

    dot_lines = [
        "digraph KernelClassHierarchy {",
        "  rankdir=LR;",
        "  node [shape=box];",
    ]

    for c in sorted(classes, key=lambda u: qname(g, u)):
        dot_lines.append(f'  "{qname(g, c)}";')

    for child, parent in sorted(edges, key=lambda e: (qname(g, e[0]), qname(g, e[1]))):
        dot_lines.append(f'  "{qname(g, child)}" -> "{qname(g, parent)}";')

    dot_lines.append("}")

    dot_path = out_dir / "kernel_class_hierarchy.dot"
    svg_path = out_dir / "kernel_class_hierarchy.svg"
    dot_path.write_text("\n".join(dot_lines), encoding="utf-8")
    render_dot_to_svg(dot_path, svg_path)

def generate_property_map(g: Graph, out_dir: Path) -> None:
    obj_props = set(g.subjects(RDF.type, OWL.ObjectProperty))
    dt_props  = set(g.subjects(RDF.type, OWL.DatatypeProperty))
    props = {p for p in (obj_props | dt_props) if is_kern(p)}

    dot_lines = [
        "digraph KernelProperties {",
        "  rankdir=LR;",
        "  node [shape=box];",
    ]

    # Track nodes we emit to avoid duplicates
    emitted = set()

    def emit_node(label: str, shape: str = "box"):
        if label in emitted:
            return
        dot_lines.append(f'  "{label}" [shape={shape}];')
        emitted.add(label)

    for p in sorted(props, key=lambda u: qname(g, u)):
        p_label = qname(g, p)
        # properties as ellipses to visually distinguish
        emit_node(p_label, shape="ellipse")

        domains = list(g.objects(p, RDFS.domain))
        ranges  = list(g.objects(p, RDFS.range))

        # If domain/range are missing, still show the property node
        if not domains:
            domains = [URIRef("urn:missing-domain")]
        if not ranges:
            ranges = [URIRef("urn:missing-range")]

        for d in domains:
            d_label = "MISSING_DOMAIN" if str(d) == "urn:missing-domain" else qname(g, d)
            emit_node(d_label, shape="box")
            dot_lines.append(f'  "{d_label}" -> "{p_label}" [label="domain"];')

        for r in ranges:
            if str(r) == "urn:missing-range":
                r_label = "MISSING_RANGE"
                emit_node(r_label, shape="box")
            else:
                r_label = qname(g, r)
                # datatypes as ovals
                if isinstance(r, URIRef) and str(r).startswith(str(XSD)):
                    emit_node(r_label, shape="oval")
                else:
                    emit_node(r_label, shape="box")
            dot_lines.append(f'  "{p_label}" -> "{r_label}" [label="range"];')

    dot_lines.append("}")

    dot_path = out_dir / "kernel_properties.dot"
    svg_path = out_dir / "kernel_properties.svg"
    dot_path.write_text("\n".join(dot_lines), encoding="utf-8")
    render_dot_to_svg(dot_path, svg_path)

def main():
    repo_root = Path(__file__).resolve().parent.parent
    ontology_path = repo_root / "ontology" / "kernel.ttl"
    out_dir = repo_root / "viz"
    out_dir.mkdir(exist_ok=True)

    g = Graph()
    g.parse(str(ontology_path), format="turtle")

    generate_class_hierarchy(g, out_dir)
    generate_property_map(g, out_dir)

    print(f"Generated: {out_dir / 'kernel_class_hierarchy.svg'}")
    print(f"Generated: {out_dir / 'kernel_properties.svg'}")

if __name__ == "__main__":
    main()