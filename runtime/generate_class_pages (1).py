import os
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Set, Tuple, Union, Any

from rdflib import Graph, RDF, RDFS, OWL, URIRef, BNode, Literal, Namespace

# Namespaces
KERN = Namespace("https://ontology.engender.co.za/kernel#")
XSD  = Namespace("http://www.w3.org/2001/XMLSchema#")
SH   = Namespace("http://www.w3.org/ns/shacl#")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")

RDF_FIRST = RDF.first
RDF_REST = RDF.rest
RDF_NIL = RDF.nil


def qname(g: Graph, uri: Union[URIRef, BNode, Literal]) -> str:
    """Stable, readable identifier for a node."""
    if isinstance(uri, Literal):
        return str(uri)
    if isinstance(uri, BNode):
        return f"_:{uri}"
    try:
        return g.namespace_manager.normalizeUri(uri)
    except Exception:
        return str(uri)


# Visual style constants (purely presentational; does not affect ontology/contracts)
COLOR_CENTRAL = "#FFFFFF"
COLOR_SUPER = "#DDEEFF"
COLOR_SUB = "#DFFFE0"
COLOR_CLASS = "#F5F5F5"
COLOR_PROP = "#FFF2CC"
COLOR_DATATYPE = "#E1D5E7"
COLOR_CONTRACT = "#FFE6CC"
COLOR_LEGEND_BG = "#FAFAFA"


def wrap_text(text: str, max_chars: int = 60) -> str:
    """Word-wrap text for Graphviz labels to keep node widths bounded.

    Graphviz does not reliably enforce a *maximum* node width for plain labels.
    The most deterministic approach is to wrap long text ourselves.
    """
    text = (text or "").strip()
    if not text:
        return ""

    words = text.split()
    lines: List[str] = []
    cur: List[str] = []
    cur_len = 0

    for w in words:
        w_len = len(w)
        # If a single word is longer than max, hard-split it.
        if w_len > max_chars:
            if cur:
                lines.append(" ".join(cur))
                cur, cur_len = [], 0
            for i in range(0, w_len, max_chars):
                lines.append(w[i:i+max_chars])
            continue

        if cur_len == 0:
            cur.append(w)
            cur_len = w_len
        elif cur_len + 1 + w_len <= max_chars:
            cur.append(w)
            cur_len += 1 + w_len
        else:
            lines.append(" ".join(cur))
            cur = [w]
            cur_len = w_len

    if cur:
        lines.append(" ".join(cur))
    return "\\n".join(lines)


def gv_escape(s: str) -> str:
    """Escape characters that break Graphviz quoted labels."""
    return (s or "").replace('"', "'")


def to_left_justified_label(lines: List[str], wrap_at: int = 80, indent: str = "") -> str:
    """Create a Graphviz left-justified multi-line label (using \l) with wrapping."""
    out: List[str] = []
    for ln in lines:
        wrapped = wrap_text(gv_escape(ln), max_chars=wrap_at)
        for sub in wrapped.split("\\n") if wrapped else [""]:
            out.append(f"{indent}{sub}\\l")
    return "".join(out)


def is_kern(uri: URIRef) -> bool:
    return isinstance(uri, URIRef) and str(uri).startswith(str(KERN))


def safe_filename_from_qname(name: str) -> str:
    # e.g., "kern:Stipulation" -> "kern_Stipulation"
    return (
        name.replace("/", "_")
        .replace("#", "_")
        .replace(":", "_")
        .replace(".", "_")
        .replace(" ", "_")
    )


def render_dot_to_svg(dot_path: Path, svg_path: Path) -> None:
    subprocess.run(["dot", "-Tsvg", str(dot_path), "-o", str(svg_path)], check=True)


def first_literal(g: Graph, s: URIRef, p: URIRef) -> Optional[str]:
    for o in g.objects(s, p):
        if isinstance(o, Literal):
            return str(o)
    return None


def walk_rdf_list(g: Graph, head: Union[URIRef, BNode]) -> List[Union[URIRef, BNode, Literal]]:
    """Walk an RDF list starting at head, returning members."""
    out: List[Union[URIRef, BNode, Literal]] = []
    cur = head
    visited = set()
    while cur and cur != RDF_NIL and cur not in visited:
        visited.add(cur)
        first = next(g.objects(cur, RDF_FIRST), None)
        rest = next(g.objects(cur, RDF_REST), None)
        if first is not None:
            out.append(first)
        cur = rest
    return out


def collect_kernel_paths(repo_root: Path) -> Tuple[Path, Path]:
    """Find kernel.ttl and kernel.shacl.ttl in standard repo layout or current directory."""
    candidates = [
        (repo_root / "ontology" / "kernel.ttl", repo_root / "ontology" / "kernel.shacl.ttl"),
        (repo_root / "kernel.ttl", repo_root / "kernel.shacl.ttl"),
    ]
    for tbox, shacl in candidates:
        if tbox.exists() and shacl.exists():
            return tbox, shacl
    raise FileNotFoundError(
        "Could not find kernel.ttl and kernel.shacl.ttl. Expected either ./ontology/ or current directory."
    )


def collect_properties(tbox: Graph) -> Set[URIRef]:
    obj_props = set(tbox.subjects(RDF.type, OWL.ObjectProperty))
    dt_props = set(tbox.subjects(RDF.type, OWL.DatatypeProperty))
    return {p for p in (obj_props | dt_props) if is_kern(p)}


def direct_taxonomy(tbox: Graph, cls: URIRef) -> Tuple[List[URIRef], List[URIRef]]:
    supers = sorted(
        {o for o in tbox.objects(cls, RDFS.subClassOf) if isinstance(o, URIRef) and is_kern(o)},
        key=lambda u: qname(tbox, u),
    )
    subs = sorted(
        {s for s in tbox.subjects(RDFS.subClassOf, cls) if isinstance(s, URIRef) and is_kern(s)},
        key=lambda u: qname(tbox, u),
    )
    return supers, subs


def structure_edges(tbox: Graph, cls: URIRef, props: Set[URIRef]) -> Tuple[List[Tuple[URIRef, URIRef]], List[Tuple[URIRef, URIRef]]]:
    """Return (outgoing prop->range, incoming domain->prop) for this class."""
    outgoing: List[Tuple[URIRef, URIRef]] = []
    incoming: List[Tuple[URIRef, URIRef]] = []

    for p in props:
        domains = [d for d in tbox.objects(p, RDFS.domain) if isinstance(d, URIRef)]
        ranges = [r for r in tbox.objects(p, RDFS.range) if isinstance(r, URIRef)]

        if cls in domains:
            if ranges:
                for r in ranges:
                    outgoing.append((p, r))
            else:
                outgoing.append((p, URIRef("urn:missing-range")))

        if cls in ranges:
            if domains:
                for d in domains:
                    incoming.append((d, p))
            else:
                incoming.append((URIRef("urn:missing-domain"), p))

    outgoing.sort(key=lambda t: (qname(tbox, t[0]), qname(tbox, t[1])))
    incoming.sort(key=lambda t: (qname(tbox, t[0]), qname(tbox, t[1])))
    return outgoing, incoming


def parse_property_constraint(shacl: Graph, prop_node: Union[BNode, URIRef]) -> Dict[str, Any]:
    def one(p):
        return next(shacl.objects(prop_node, p), None)

    out: Dict[str, Any] = {
        "path": one(SH.path),
        "minCount": one(SH.minCount),
        "maxCount": one(SH.maxCount),
        "class": one(SH["class"]),
        "datatype": one(SH.datatype),
        "hasValue": one(SH.hasValue),
        "in": None,
    }

    in_list = one(SH["in"])
    if in_list is not None:
        out["in"] = walk_rdf_list(shacl, in_list)

    return out


def summarize_prop_constraint(tbox: Graph, shacl: Graph, c: Dict[str, Any]) -> str:
    parts = []
    if c.get("path") is not None:
        parts.append(f"path={qname(tbox, c['path'])}")
    if c.get("minCount") is not None:
        parts.append(f"min={c['minCount']}")
    if c.get("maxCount") is not None:
        parts.append(f"max={c['maxCount']}")
    if c.get("class") is not None:
        parts.append(f"class={qname(tbox, c['class'])}")
    if c.get("datatype") is not None:
        parts.append(f"datatype={qname(tbox, c['datatype'])}")
    if c.get("hasValue") is not None:
        parts.append(f"hasValue={qname(tbox, c['hasValue'])}")
    if c.get("in"):
        items = ", ".join(qname(tbox, x) for x in c["in"])
        parts.append(f"in=({items})")
    return " ; ".join(parts) if parts else "(no parsed details)"


def parse_shape_contract(tbox: Graph, shacl: Graph, shape: URIRef) -> List[str]:
    """Return a list of lines describing constraints for a NodeShape."""
    lines: List[str] = []

    # Direct sh:property blocks
    prop_nodes = list(shacl.objects(shape, SH.property))
    for pn in prop_nodes:
        if isinstance(pn, (BNode, URIRef)):
            c = parse_property_constraint(shacl, pn)
            lines.append(f"- {summarize_prop_constraint(tbox, shacl, c)}")

    # sh:or blocks (each member is typically a shape-like node)
    for or_list in shacl.objects(shape, SH["or"]):
        branches = walk_rdf_list(shacl, or_list)
        for i, br in enumerate(branches, start=1):
            lines.append(f"- OR case {i}:")
            # Branch may contain sh:property constraints
            for pn in shacl.objects(br, SH.property):
                if isinstance(pn, (BNode, URIRef)):
                    c = parse_property_constraint(shacl, pn)
                    lines.append(f"    * {summarize_prop_constraint(tbox, shacl, c)}")

            # Some branches include direct sh:hasValue / sh:in etc nested under sh:property; above captures.
            # If a branch includes other nested constructs, we keep it minimal (no inference).

    # sh:not blocks
    for not_node in shacl.objects(shape, SH["not"]):
        lines.append("- NOT block:")
        # Try to surface any sh:property constraints inside the not node
        for pn in shacl.objects(not_node, SH.property):
            if isinstance(pn, (BNode, URIRef)):
                c = parse_property_constraint(shacl, pn)
                lines.append(f"    * {summarize_prop_constraint(tbox, shacl, c)}")

    if not lines:
        lines.append("(no constraints found)")

    return lines


def shapes_for_class(shacl: Graph, cls: URIRef) -> List[URIRef]:
    shapes = [s for s in shacl.subjects(SH.targetClass, cls) if isinstance(s, URIRef)]
    # Sort by qname if possible for determinism
    shapes.sort(key=lambda s: str(s))
    return shapes


def build_class_page_dot(tbox: Graph, shacl: Graph, cls: URIRef, props: Set[URIRef]) -> str:
    cls_qn = qname(tbox, cls)
    label = first_literal(tbox, cls, RDFS.label) or cls_qn
    definition = first_literal(tbox, cls, SKOS.definition) or ""

    supers, subs = direct_taxonomy(tbox, cls)
    outgoing, incoming = structure_edges(tbox, cls, props)

    # Contract
    shapes = shapes_for_class(shacl, cls)

    # DOT graph with two clusters
    dot: List[str] = []
    dot.append("digraph ClassPage {")
    dot.append("  rankdir=LR;")
    dot.append("  graph [fontsize=10];")
    dot.append("  node [fontsize=10];")
    dot.append("  edge [fontsize=9];")

    # Central node (wrapped to bound visual width)
    safe_label = wrap_text(gv_escape(label), max_chars=44)
    safe_def = wrap_text(gv_escape(definition), max_chars=72)
    central_label = safe_label
    if safe_def:
        central_label += f"\\n\\n{safe_def}"
    dot.append(
        f'  "{cls_qn}" [shape=box, style="rounded,filled", fillcolor="{COLOR_CENTRAL}", penwidth=2, label="{central_label}"];'
    )

    # --- Structure cluster ---
    dot.append("  subgraph cluster_structure {")
    dot.append('    label="STRUCTURE (TBox)";')
    dot.append("    color=gray50;")
    dot.append("    style=rounded;")

    # Taxonomy nodes
    for s in supers:
        s_qn = qname(tbox, s)
        dot.append(f'    "{s_qn}" [shape=box, style="filled", fillcolor="{COLOR_SUPER}"];')
        dot.append(f'    "{cls_qn}" -> "{s_qn}" [label="subClassOf"];')

    for s in subs:
        s_qn = qname(tbox, s)
        dot.append(f'    "{s_qn}" [shape=box, style="filled", fillcolor="{COLOR_SUB}"];')
        dot.append(f'    "{s_qn}" -> "{cls_qn}" [label="subClassOf"];')

    # Outgoing edges (domain=cls)
    for p, r in outgoing:
        p_qn = qname(tbox, p)
        dot.append(f'    "{p_qn}" [shape=ellipse, style="filled", fillcolor="{COLOR_PROP}"];')
        dot.append(f'    "{cls_qn}" -> "{p_qn}" [label="domain"];')

        if str(r) == "urn:missing-range":
            r_qn = "MISSING_RANGE"
            dot.append(f'    "{r_qn}" [shape=box, style="filled", fillcolor="{COLOR_CLASS}"];')
        else:
            r_qn = qname(tbox, r)
            if isinstance(r, URIRef) and str(r).startswith(str(XSD)):
                dot.append(f'    "{r_qn}" [shape=oval, style="filled", fillcolor="{COLOR_DATATYPE}"];')
            else:
                dot.append(f'    "{r_qn}" [shape=box, style="filled", fillcolor="{COLOR_CLASS}"];')
        dot.append(f'    "{p_qn}" -> "{r_qn}" [label="range"];')

    # Incoming edges (range=cls)
    for d, p in incoming:
        p_qn = qname(tbox, p)
        dot.append(f'    "{p_qn}" [shape=ellipse, style="filled", fillcolor="{COLOR_PROP}"];')

        if str(d) == "urn:missing-domain":
            d_qn = "MISSING_DOMAIN"
            dot.append(f'    "{d_qn}" [shape=box, style="filled", fillcolor="{COLOR_CLASS}"];')
        else:
            d_qn = qname(tbox, d)
            dot.append(f'    "{d_qn}" [shape=box, style="filled", fillcolor="{COLOR_CLASS}"];')

        dot.append(f'    "{d_qn}" -> "{p_qn}" [label="domain"];')
        dot.append(f'    "{p_qn}" -> "{cls_qn}" [label="range"];')

    dot.append("  }")

    # --- Contract cluster ---
    dot.append("  subgraph cluster_contract {")
    dot.append('    label="CONTRACT (SHACL)";')
    dot.append("    color=gray50;")
    dot.append("    style=rounded;")

    if not shapes:
        # No shapes target this class
        contract_node = f"contract::{cls_qn}"
        note = wrap_text(f"No SHACL NodeShape targets {cls_qn}.", max_chars=60)
        dot.append(f'    "{contract_node}" [shape=note, style="filled", fillcolor="{COLOR_CONTRACT}", label="{gv_escape(note)}"];')
        dot.append(f'    "{cls_qn}" -> "{contract_node}" [style=dashed, label="contract"];')
    else:
        for shape in shapes:
            shape_qn = qname(shacl, shape)
            lines = parse_shape_contract(tbox, shacl, shape)
            # Left-justified multi-line label uses \l; wrap long lines
            header = to_left_justified_label([shape_qn], wrap_at=80)
            body = to_left_justified_label(lines, wrap_at=96)
            text = header + body
            node_id = f"shape::{shape_qn}::{cls_qn}"
            dot.append(f'    "{node_id}" [shape=box, style="rounded,filled", fillcolor="{COLOR_CONTRACT}", label="{text}"];')
            dot.append(f'    "{cls_qn}" -> "{node_id}" [style=dashed, label="targets"];')

    dot.append("  }")

    # --- Legend (purely visual) ---
    dot.append("  subgraph cluster_legend {")
    dot.append('    label="LEGEND";')
    dot.append("    color=gray60;")
    dot.append('    style="rounded,filled";')
    dot.append(f'    fillcolor="{COLOR_LEGEND_BG}";')
    dot.append('    "LEG_CENTRAL" [shape=box, style="rounded,filled", fillcolor="%s", label="Class (focus)" ];' % COLOR_CENTRAL)
    dot.append('    "LEG_SUPER"   [shape=box, style="filled", fillcolor="%s", label="Superclass" ];' % COLOR_SUPER)
    dot.append('    "LEG_SUB"     [shape=box, style="filled", fillcolor="%s", label="Subclass" ];' % COLOR_SUB)
    dot.append('    "LEG_CLASS"   [shape=box, style="filled", fillcolor="%s", label="Related class" ];' % COLOR_CLASS)
    dot.append('    "LEG_PROP"    [shape=ellipse, style="filled", fillcolor="%s", label="Property" ];' % COLOR_PROP)
    dot.append('    "LEG_DTYPE"   [shape=oval, style="filled", fillcolor="%s", label="Datatype" ];' % COLOR_DATATYPE)
    dot.append('    "LEG_CON"     [shape=box, style="rounded,filled", fillcolor="%s", label="SHACL contract" ];' % COLOR_CONTRACT)
    dot.append("  }")

    dot.append("}")
    return "\n".join(dot)


def write_index_html(out_dir: Path, class_entries: List[Tuple[str, str]]) -> None:
    # class_entries: (display_name, filename)
    rows = "\n".join([f'<li><a href="{fn}">{disp}</a></li>' for disp, fn in class_entries])
    html = f"""<!doctype html>
<html>
<head>
  <meta charset=\"utf-8\">
  <title>Kernel Class Pages</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; }}
    li {{ margin: 6px 0; }}
  </style>
</head>
<body>
  <h1>Kernel Class Pages</h1>
  <p>Each page contains two panels: Structure (TBox) and Contract (SHACL).</p>
  <ul>
    {rows}
  </ul>
</body>
</html>
"""
    (out_dir / "index.html").write_text(html, encoding="utf-8")


def main() -> None:
    # Repo root assumed to be parent of this script's directory.
    # If you keep this under runtime/, repo_root is ../
    script_path = Path(__file__).resolve()
    repo_root = script_path.parent.parent if script_path.parent.name == "runtime" else script_path.parent

    tbox_path, shacl_path = collect_kernel_paths(repo_root)

    out_dir = repo_root / "viz" / "classes"
    out_dir.mkdir(parents=True, exist_ok=True)

    tbox = Graph()
    tbox.parse(str(tbox_path), format="turtle")

    shacl = Graph()
    shacl.parse(str(shacl_path), format="turtle")

    props = collect_properties(tbox)

    # Collect kern classes (owl:Class + anything in subClassOf)
    classes: Set[URIRef] = {c for c in tbox.subjects(RDF.type, OWL.Class) if is_kern(c)}
    for child, parent in tbox.subject_objects(RDFS.subClassOf):
        if isinstance(child, URIRef) and is_kern(child):
            classes.add(child)
        if isinstance(parent, URIRef) and is_kern(parent):
            classes.add(parent)

    class_list = sorted(classes, key=lambda u: qname(tbox, u))

    index_entries: List[Tuple[str, str]] = []

    for cls in class_list:
        cls_qn = qname(tbox, cls)
        dot_text = build_class_page_dot(tbox, shacl, cls, props)
        base = safe_filename_from_qname(cls_qn)
        dot_path = out_dir / f"{base}.dot"
        svg_path = out_dir / f"{base}.svg"
        dot_path.write_text(dot_text, encoding="utf-8")
        render_dot_to_svg(dot_path, svg_path)
        index_entries.append((cls_qn, svg_path.name))

    write_index_html(out_dir, index_entries)
    print(f"Generated {len(index_entries)} class pages in: {out_dir}")
    print(f"Open: {out_dir / 'index.html'}")


if __name__ == "__main__":
    main()
