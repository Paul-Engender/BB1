import sys
import hashlib
import textwrap
from pathlib import Path
from typing import List

try:
    from graphviz import Digraph
except ImportError:
    print("Error: pip install graphviz")
    sys.exit(1)

from rdflib import Graph, RDF, RDFS, OWL, SH, SKOS, URIRef, Namespace

# --- Configuration ---
KERN = Namespace("https://ontology.engender.co.za/kernel#")

COLORS = {
    "focus": "#FFFFFF", 
    "super": "#DDEEFF", 
    "sub": "#DFFFE0", 
    "incoming": "#F5F5F5", 
    "outgoing": "#F5F5F5", 
    "datatype": "#E1D5E7", 
    "contract": "#FFE6CC",
    "contract_text": "#5d4037"
}

def qname(g: Graph, uri: URIRef) -> str:
    try:
        return g.namespace_manager.normalizeUri(uri)
    except:
        return str(uri).split("/")[-1].split("#")[-1]

def wrap(text: str, width=40) -> str:
    if not text: return ""
    return "\\n".join(textwrap.wrap(str(text), width=width))

def get_id(uri: URIRef) -> str:
    return "node_" + hashlib.md5(str(uri).encode('utf-8')).hexdigest()[:8]

class Visualizer:
    def __init__(self, tbox_path: Path, shacl_path: Path, out_dir: Path):
        print(f"Loading Ontology: {tbox_path.name}")
        self.tbox = Graph().parse(str(tbox_path), format="turtle")
        self.shacl = Graph().parse(str(shacl_path), format="turtle")
        self.out_dir = out_dir
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def get_related(self, focus: URIRef):
        supers = sorted([o for o in self.tbox.objects(focus, RDFS.subClassOf) if isinstance(o, URIRef)])
        subs = sorted([s for s in self.tbox.subjects(RDFS.subClassOf, focus) if isinstance(s, URIRef)])
        
        incoming = []
        outgoing_obj = []
        outgoing_data = []

        for p in self.tbox.subjects(RDF.type, None):
            ptype = self.tbox.value(p, RDF.type)
            if ptype not in [OWL.ObjectProperty, OWL.DatatypeProperty]: continue

            for d in self.tbox.objects(p, RDFS.domain):
                for r in self.tbox.objects(p, RDFS.range):
                    if not (isinstance(d, URIRef) and isinstance(r, URIRef)): continue
                    if d == focus:
                        if ptype == OWL.DatatypeProperty or str(r).startswith("http://www.w3.org/2001/XMLSchema"):
                            outgoing_data.append((p, r))
                        else:
                            outgoing_obj.append((p, r))
                    if r == focus:
                        incoming.append((d, p))
                        
        return supers, subs, incoming, outgoing_obj, outgoing_data

    def get_contracts(self, focus: URIRef) -> List[str]:
        shapes = list(self.shacl.subjects(SH.targetClass, focus))
        if not shapes: return ["No SHACL NodeShape targets this class."]
        results = []
        for s in shapes:
            props = list(self.shacl.objects(s, SH.property))
            s_name = qname(self.shacl, s)
            results.append(f"Shape: {s_name} ({len(props)} constraints defined)")
        return results

    def make_legend_html(self):
        return f"""<
        <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="10" CELLPADDING="8">
            <TR>
                <TD BGCOLOR="{COLORS['focus']}">Focus Class</TD>
                <TD BGCOLOR="{COLORS['super']}">Superclass</TD>
                <TD BGCOLOR="{COLORS['sub']}">Subclass</TD>
                <TD BGCOLOR="{COLORS['incoming']}">Incoming</TD>
                <TD BGCOLOR="{COLORS['outgoing']}">Outgoing</TD>
                <TD BGCOLOR="{COLORS['datatype']}">Datatype</TD>
            </TR>
        </TABLE>
        >"""

    def make_contract_html(self, contracts: List[str]):
        rows = ""
        for c in contracts:
            safe_c = c.replace("<", "&lt;").replace(">", "&gt;")
            rows += f'<TR><TD ALIGN="LEFT" BORDER="0">{safe_c}</TD></TR>'
            
        return f"""<
        <TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="10" BGCOLOR="{COLORS['contract']}">
            <TR><TD BORDER="0"><B><FONT COLOR="{COLORS['contract_text']}">SHACL CONTRACT</FONT></B></TD></TR>
            <HR/>
            {rows}
        </TABLE>
        >"""

    def generate(self, cls: URIRef):
        focus_id = get_id(cls)
        focus_label = qname(self.tbox, cls)
        supers, subs, inc, out_obj, out_data = self.get_related(cls)
        
        dot = Digraph(focus_label, format='svg')
        # newrank=True is CRITICAL for cross-cluster alignment
        dot.attr(rankdir='TB', splines='true', nodesep='0.5', ranksep='0.6', newrank='true') 
        dot.attr('node', fontname='Helvetica', fontsize='10')

        # --- 1. LEGEND (Global Top) ---
        # Rendered as a single HTML node to prevent drifting
        dot.node('LEGEND_BLOCK', label=self.make_legend_html(), shape='plain')

        # --- 2. STRUCTURE (Middle Cluster) ---
        with dot.subgraph(name='cluster_structure') as struc:
            struc.attr(label='Ontology Structure (TBox)', style='dashed', color='gray50', margin='30')

            # SCAFFOLD: Invisible Anchors for Top/Bottom of Structure
            struc.node('STRUCT_TOP', '', shape='point', style='invis', width='0')
            struc.node('STRUCT_BOTTOM', '', shape='point', style='invis', width='0')

            # Focus Node
            def_node = self.tbox.value(cls, SKOS.definition)
            desc = wrap(def_node, 50) if def_node else ""
            lbl = f"{focus_label}\n\n{desc}"
            struc.node(focus_id, label=lbl, shape='box', style='filled,rounded', 
                       fillcolor=COLORS['focus'], penwidth='3', fontsize='12', fontname='Helvetica-Bold')

            # Superclasses (Above Focus)
            for s in supers:
                sid = get_id(s)
                struc.node(sid, qname(self.tbox, s), shape='box', style='filled', fillcolor=COLORS['super'])
                struc.edge(focus_id, sid, label='subClassOf', dir='forward')
                # Force Superclass below Top Anchor
                struc.edge('STRUCT_TOP', sid, style='invis') 

            # Neighbors (Aligned Horizontally)
            align_nodes = [focus_id]
            
            # Incoming
            last_inc = None
            for d, p in inc:
                did = get_id(d)
                struc.node(did, qname(self.tbox, d), shape='box', style='filled', fillcolor=COLORS['incoming'])
                struc.edge(did, focus_id, label=qname(self.tbox, p))
                if last_inc: struc.edge(last_inc, did, style='invis')
                last_inc = did
            if inc: align_nodes.insert(0, get_id(inc[0][0]))

            # Outgoing
            last_out = None
            for p, r in out_obj:
                rid = get_id(r)
                struc.node(rid, qname(self.tbox, r), shape='box', style='filled', fillcolor=COLORS['outgoing'])
                struc.edge(focus_id, rid, label=qname(self.tbox, p))
                if last_out: struc.edge(last_out, rid, style='invis')
                last_out = rid
            if out_obj: align_nodes.append(get_id(out_obj[0][1]))

            # Force horizontal alignment
            with struc.subgraph() as align:
                align.attr(rank='same')
                for n in align_nodes: align.node(n)

            # Subclasses
            for s in subs:
                sid = get_id(s)
                struc.node(sid, qname(self.tbox, s), shape='box', style='filled', fillcolor=COLORS['sub'])
                struc.edge(sid, focus_id, label='subClassOf', dir='forward')
                # Force Subclass above Bottom Anchor
                struc.edge(sid, 'STRUCT_BOTTOM', style='invis')

            # Datatypes
            for p, t in out_data:
                tid = get_id(t) + "_dt"
                struc.node(tid, qname(self.tbox, t), shape='oval', style='filled', fillcolor=COLORS['datatype'])
                struc.edge(focus_id, tid, label=qname(self.tbox, p))
                # Force Datatype above Bottom Anchor
                struc.edge(tid, 'STRUCT_BOTTOM', style='invis')

        # --- 3. CONTRACT (Global Bottom) ---
        contracts = self.get_contracts(cls)
        dot.node('CONTRACT_BLOCK', label=self.make_contract_html(contracts), shape='plain')

        # --- 4. THE SCAFFOLD (Vertical Spine) ---
        # This is the secret sauce. High weight edges force verticality.
        
        # Legend -> Structure Top
        dot.edge('LEGEND_BLOCK', 'STRUCT_TOP', style='invis', weight='1000')
        
        # Structure Top -> Focus (Guarantees focus is central)
        dot.edge('STRUCT_TOP', focus_id, style='invis', weight='1000')
        
        # Focus -> Structure Bottom (Guarantees flow down)
        dot.edge(focus_id, 'STRUCT_BOTTOM', style='invis', weight='1000')
        
        # Structure Bottom -> Contract
        dot.edge('STRUCT_BOTTOM', 'CONTRACT_BLOCK', style='invis', weight='1000')

        # Render
        try:
            filename = focus_label.replace(":", "_").replace("/", "_")
            dot.render(filename, directory=self.out_dir, cleanup=True)
            print(f"Generated {filename}.svg")
        except Exception as e:
            print(f"Error rendering {focus_label}: {e}")

if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    
    candidates = [
        (root / "ontology" / "kernel.ttl", root / "ontology" / "kernel.shacl.ttl"),
        (Path("kernel.ttl"), Path("kernel.shacl.ttl"))
    ]
    
    tbox_path, shacl_path = None, None
    for t, s in candidates:
        if t.exists() and s.exists():
            tbox_path, shacl_path = t, s
            break

    if tbox_path:
        viz = Visualizer(tbox_path, shacl_path, root / "viz" / "classes")
        count = 0
        for s in viz.tbox.subjects(RDF.type, OWL.Class):
            if str(s).startswith(str(KERN)):
                viz.generate(s)
                count += 1
        print(f"Done. Processed {count} classes.")
    else:
        print("Ontology files not found.")