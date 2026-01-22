import sys
import hashlib
import textwrap
import html
from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict

try:
    from graphviz import Digraph
except ImportError:
    print("Error: pip install graphviz")
    sys.exit(1)

from rdflib import Graph, RDF, RDFS, OWL, SH, SKOS, URIRef, Namespace, Literal

# --- CONFIGURATION ---
KERN = Namespace("https://ontology.engender.co.za/kernel#")
XSD  = Namespace("http://www.w3.org/2001/XMLSchema#")

COLORS = {
    "focus":     "#FFFFFF", 
    "super":     "#DDEEFF", 
    "sub":       "#DFFFE0", 
    "incoming":  "#F5F5F5", 
    "outgoing":  "#F5F5F5", 
    "datatype":  "#E1D5E7", 
    "contract":  "#FFE6CC",
    "text":      "#000000",
    "header_bg": "#EEEEEE",
    "sub_header": "#FFF0E0"
}

# --- UTILITIES ---
def qname(g: Graph, uri: URIRef) -> str:
    try:
        return g.namespace_manager.normalizeUri(uri)
    except:
        return str(uri).split("/")[-1].split("#")[-1]

def safe_wrap(text: str, width=50) -> str:
    if not text: return ""
    val = text.decode('utf-8') if isinstance(text, bytes) else str(text)
    safe_val = html.escape(val)
    return "<BR/>".join(textwrap.wrap(safe_val, width=width))

def get_id(uri: URIRef) -> str:
    return "node_" + hashlib.md5(str(uri).encode('utf-8')).hexdigest()[:8]

class ClassAssetBuilder:
    def __init__(self, tbox_graph: Graph, shacl_graph: Graph, out_dir: Path):
        self.tbox = tbox_graph
        self.shacl = shacl_graph
        self.out_dir = out_dir
        self.out_dir.mkdir(parents=True, exist_ok=True)

        # Pre-Index for O(1) performance
        print("  -> Indexing ontology...")
        self.idx_supers = defaultdict(set)
        self.idx_subs = defaultdict(set)
        self.idx_domain = defaultdict(list)
        self.idx_range = defaultdict(list)
        self._build_indexes()

    def _build_indexes(self):
        # Hierarchy
        for s, o in self.tbox.subject_objects(RDFS.subClassOf):
            if isinstance(s, URIRef) and isinstance(o, URIRef):
                self.idx_supers[s].add(o)
                self.idx_subs[o].add(s)
        for s, o in self.tbox.subject_objects(OWL.equivalentClass):
            if isinstance(s, URIRef) and isinstance(o, URIRef):
                self.idx_supers[s].add(o)

        # Properties
        for p in self.tbox.subjects(RDF.type, None):
            ptype = self.tbox.value(p, RDF.type)
            if ptype not in [OWL.ObjectProperty, OWL.DatatypeProperty]: continue
            for d in self.tbox.objects(p, RDFS.domain):
                if isinstance(d, URIRef): self.idx_domain[d].append(p)
            for r in self.tbox.objects(p, RDFS.range):
                if isinstance(r, URIRef): self.idx_range[r].append(p)

    def _get_data(self, focus: URIRef):
        supers = sorted(list(self.idx_supers.get(focus, [])))
        subs = sorted(list(self.idx_subs.get(focus, [])))
        
        incoming, outgoing_obj, outgoing_data = [], [], []

        # Outgoing
        for p in self.idx_domain.get(focus, []):
            ptype = self.tbox.value(p, RDF.type)
            for r in self.tbox.objects(p, RDFS.range):
                if not isinstance(r, URIRef): continue
                is_data = (ptype == OWL.DatatypeProperty) or str(r).startswith(str(XSD))
                if is_data: outgoing_data.append((p, r))
                else: outgoing_obj.append((p, r))

        # Incoming
        for p in self.idx_range.get(focus, []):
            for d in self.tbox.objects(p, RDFS.domain):
                if isinstance(d, URIRef): incoming.append((d, p))

        return supers, subs, incoming, outgoing_obj, outgoing_data

    def _get_contract(self, focus: URIRef):
        # (Same SHACL parsing logic as previous versions)
        outgoing = []
        for shape in self.shacl.subjects(SH.targetClass, focus):
            shape_name = qname(self.shacl, shape)
            constraints = []
            for prop in self.shacl.objects(shape, SH.property):
                path = self.shacl.value(prop, SH.path)
                min_c = self.shacl.value(prop, SH.minCount)
                max_c = self.shacl.value(prop, SH.maxCount)
                p_str = f"<b>{html.escape(qname(self.shacl, path))}</b>" if path else "<i>Node</i>"
                dets = []
                if min_c: dets.append(f"min:{min_c}")
                if max_c: dets.append(f"max:{max_c}")
                d_str = ", ".join(dets) if dets else "defined"
                constraints.append(f"{p_str} ({d_str})")
            outgoing.append({"name": shape_name, "constraints": constraints})
        
        incoming = [] # Simplified for brevity, add incoming logic if needed
        return {"outgoing": outgoing, "incoming": incoming}

    # --- GRAPH FACTORY ---
    def _new_graph(self, name: str) -> Digraph:
        """Creates a fresh, clean canvas for a single band."""
        dot = Digraph(name, format='svg')
        # Use polyline for stability. Rankdir TB is standard.
        dot.attr(rankdir='TB', splines='polyline', nodesep='0.5', ranksep='0.5', bgcolor='transparent')
        dot.attr('node', fontname='Helvetica', fontsize='10')
        dot.attr('edge', fontname='Helvetica', fontsize='9')
        return dot

    def _add_focus_node(self, dot: Digraph, focus: URIRef):
        """Adds the central node to the current band's graph."""
        lbl = qname(self.tbox, focus)
        # We assume the user knows the definition from the main page context
        dot.node('FOCUS', label=lbl, shape='box', style='filled,rounded', 
                 fillcolor=COLORS['focus'], penwidth='3', fontsize='12', fontname='Helvetica-Bold')

    # --- 6 INDEPENDENT RENDERERS ---

    def render_1_legend(self, cls_name: str):
        dot = self._new_graph("Legend")
        # Pure HTML Node
        rows = f"""<TR>
            <TD BGCOLOR="{COLORS['focus']}">Focus Class</TD>
            <TD BGCOLOR="{COLORS['super']}">Superclass</TD>
            <TD BGCOLOR="{COLORS['sub']}">Subclass</TD>
            <TD BGCOLOR="{COLORS['incoming']}">Incoming</TD>
            <TD BGCOLOR="{COLORS['outgoing']}">Outgoing</TD>
            <TD BGCOLOR="{COLORS['datatype']}">Datatype</TD>
        </TR>"""
        tbl = f"""<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="10" CELLPADDING="8" BGCOLOR="#FAFAFA">{rows}</TABLE>>"""
        dot.node('L', label=tbl, shape='plain')
        dot.render(str(self.out_dir / f"{cls_name}_1_Legend"), cleanup=True)

    def render_2a_supers(self, cls_name: str, focus: URIRef, supers: list):
        if not supers: return # Don't generate empty image
        dot = self._new_graph("Supers")
        self._add_focus_node(dot, focus)
        
        for s in supers:
            sid = get_id(s)
            dot.node(sid, qname(self.tbox, s), shape='box', style='filled', fillcolor=COLORS['super'])
            # Super -> Focus (visually up)
            dot.edge(sid, 'FOCUS', label='subClassOf', dir='back')
            
        dot.render(str(self.out_dir / f"{cls_name}_2a_Supers"), cleanup=True)

    def render_2b_subs(self, cls_name: str, focus: URIRef, subs: list):
        if not subs: return
        dot = self._new_graph("Subs")
        self._add_focus_node(dot, focus)
        
        for s in subs:
            sid = get_id(s)
            dot.node(sid, qname(self.tbox, s), shape='box', style='filled', fillcolor=COLORS['sub'])
            dot.edge(sid, 'FOCUS', label='subClassOf', dir='forward') # Arrow points to Parent (Focus)
            
        dot.render(str(self.out_dir / f"{cls_name}_2b_Subs"), cleanup=True)

    def render_3a_assoc(self, cls_name: str, focus: URIRef, inc: list, out: list):
        if not inc and not out: return
        dot = self._new_graph("Assoc")
        dot.attr(rankdir='LR') # Switch to Left-to-Right for this band!
        self._add_focus_node(dot, focus)
        
        for d, p in inc:
            did = get_id(d)
            dot.node(did, qname(self.tbox, d), shape='box', style='filled', fillcolor=COLORS['incoming'])
            dot.edge(did, 'FOCUS', label=qname(self.tbox, p))
            
        for p, r in out:
            rid = get_id(r)
            dot.node(rid, qname(self.tbox, r), shape='box', style='filled', fillcolor=COLORS['outgoing'])
            dot.edge('FOCUS', rid, label=qname(self.tbox, p))
            
        dot.render(str(self.out_dir / f"{cls_name}_3a_Assoc"), cleanup=True)

    def render_3b_data(self, cls_name: str, focus: URIRef, data: list):
        if not data: return
        dot = self._new_graph("Data")
        dot.attr(rankdir='LR') # Left-to-Right looks better for lists of attributes
        self._add_focus_node(dot, focus)
        
        for p, t in data:
            tid = get_id(t) + "_dt"
            dot.node(tid, qname(self.tbox, t), shape='oval', style='filled', fillcolor=COLORS['datatype'])
            dot.edge('FOCUS', tid, label=qname(self.tbox, p))
            
        dot.render(str(self.out_dir / f"{cls_name}_3b_Data"), cleanup=True)

    def render_4_contract(self, cls_name: str, focus: URIRef):
        data = self._get_contract(focus)
        # ... (HTML Table generation logic from previous steps) ...
        # Simplified for brevity here
        rows = ""
        if data['outgoing']:
            for s in data['outgoing']:
                rows += f"<TR><TD ALIGN='LEFT'><B>{s['name']}</B></TD></TR>"
                for c in s['constraints']: rows += f"<TR><TD ALIGN='LEFT'>&bull; {c}</TD></TR>"
        else:
            rows = "<TR><TD>No Constraints</TD></TR>"
            
        tbl = f"""<<TABLE BORDER="0" CELLBORDER="0" BGCOLOR="{COLORS['contract']}">{rows}</TABLE>>"""
        
        dot = self._new_graph("Contract")
        dot.node('C', label=tbl, shape='plain')
        dot.render(str(self.out_dir / f"{cls_name}_4_Contract"), cleanup=True)

    # --- MASTER BUILDER ---
    def generate_all_assets(self, cls: URIRef):
        cls_name = qname(self.tbox, cls).replace(":", "_")
        supers, subs, inc, out_obj, out_data = self._get_data(cls)
        
        # Call the 6 independent renderers
        # They don't know about each other. They don't share a canvas.
        self.render_1_legend(cls_name)
        self.render_2a_supers(cls_name, cls, supers)
        self.render_2b_subs(cls_name, cls, subs)
        self.render_3a_assoc(cls_name, cls, inc, out_obj)
        self.render_3b_data(cls_name, cls, out_data)
        self.render_4_contract(cls_name, cls)

# --- MAIN ---
if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    candidates = [(root / "ontology" / "kernel.ttl", root / "ontology" / "kernel.shacl.ttl"), (Path("kernel.ttl"), Path("kernel.shacl.ttl"))]
    tbox_path, shacl_path = None, None
    for t, s in candidates:
        if t.exists() and s.exists(): tbox_path, shacl_path = t, s; break

    if tbox_path:
        builder = ClassAssetBuilder(Graph().parse(str(tbox_path), format="turtle"), 
                                    Graph().parse(str(shacl_path), format="turtle"), 
                                    root / "viz" / "assets") # New folder for raw assets
        
        for s in builder.tbox.subjects(RDF.type, OWL.Class):
            if str(s).startswith(str(KERN)): 
                builder.generate_all_assets(s)
        print("Asset generation complete.")