#!/usr/bin/env python3
"""
ENG Kernel Class Visualizer (Consolidated 4x2 Grid)
---------------------------------------------------

Generates one consolidated SVG per OWL class in the KERN namespace, laid out as a
4 (top-to-bottom) by 2 (left-to-right) grid of panels.

Panel layout (4 rows x 2 cols):
  R1C1: Hierarchy + Legend (merged)
  R1C2: Incoming Object Associations (range == focus)
  R2C1: Outgoing Object Associations (domain == focus)
  R2C2: Outgoing Datatype Properties (domain == focus; range is xsd:* or owl:DatatypeProperty)
  R3C1: Notes / Definition (no invention; uses label/definition/comment if present)
  R3C2: Contract (merged SHACL constraints for shapes targeting the focus class)
  R4C1: Diagnostics / Counts (derived counts + missing domain/range counts)
  R4C2: Reserved (placeholder panel to keep grid stable)

Engineering goals:
- Always emits an SVG per class (no missing output).
- Empty panels render a consistent "No data" placeholder (no collapsed grid).
- Deterministic ordering (sorted by QName).
- Proper property indexing (explicit object/datatype property sets).
- Robust Graphviz layout using clusters + anchor nodes + rank constraints (no SVG stitching).

Dependencies:
  pip install rdflib graphviz

Graphviz system binary required (dot):
  - Ubuntu/Debian: sudo apt-get install graphviz
  - macOS: brew install graphviz
  - Windows: choco install graphviz (or installer)

Usage:
  python visualize_kernel_classes.py --tbox kernel.ttl --shacl kernel.shacl.ttl --out ./viz/consolidated
  python visualize_kernel_classes.py --class kern:Stipulation
"""

from __future__ import annotations

import argparse
import hashlib
import html
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from graphviz import Digraph
from rdflib import Graph, RDF, RDFS, OWL, SH, SKOS, URIRef, Namespace, Literal

KERN = Namespace("https://ontology.engender.co.za/kernel#")
XSD  = Namespace("http://www.w3.org/2001/XMLSchema#")

# Visual theme (kept close to your palette, but panelized)
COLORS = {
    "panel_bg":      "#FFFFFF",
    "panel_border":  "#C9C9C9",
    "focus":         "#FFFFFF",
    "super":         "#DDEEFF",
    "sub":           "#DFFFE0",
    "incoming":      "#F5F5F5",
    "outgoing":      "#F5F5F5",
    "datatype":      "#E1D5E7",
    "contract":      "#FFE6CC",
    "notes":         "#FFFDF0",
    "diag":          "#F8F8FF",
    "reserved":      "#FAFAFA",
    "header_bg":     "#EFEFEF",
    "text":          "#000000",
    "muted":         "#555555",
}

FONTS = {
    "base": "Helvetica",
    "bold": "Helvetica-Bold",
}

def qname(g: Graph, uri: URIRef) -> str:
    try:
        return g.namespace_manager.normalizeUri(uri)
    except Exception:
        return str(uri).split("/")[-1].split("#")[-1]

def stable_node_id(uri: URIRef, prefix: str = "node") -> str:
    h = hashlib.md5(str(uri).encode("utf-8")).hexdigest()[:10]
    return f"{prefix}_{h}"

def wrap_html(s: str, width: int = 44) -> str:
    if not s:
        return ""
    val = s.decode("utf-8") if isinstance(s, (bytes, bytearray)) else str(s)
    val = html.escape(val)
    return "<BR/>".join(textwrap.wrap(val, width=width))

def lit_to_str(lit: Optional[Literal]) -> str:
    if lit is None:
        return ""
    return str(lit)

@dataclass(frozen=True)
class ConstraintLine:
    path: str
    details: str

@dataclass
class ClassViewModel:
    focus: URIRef
    focus_qname: str

    supers: List[URIRef]
    subs: List[URIRef]
    equivs: List[URIRef]

    incoming_obj: List[Tuple[URIRef, URIRef]]      # (domainClass, prop)
    outgoing_obj: List[Tuple[URIRef, URIRef]]      # (prop, rangeClass)
    outgoing_data: List[Tuple[URIRef, URIRef]]     # (prop, datatypeURI)

    shacl_constraints: Dict[str, List[ConstraintLine]]  # shapeQName -> constraints

    notes: Dict[str, str]                          # label/definition/comment/uri

    diag: Dict[str, int]                           # counts / missing stats

class OntologyIndex:
    def __init__(self, tbox: Graph):
        self.tbox = tbox

        # Classes
        self.classes: Set[URIRef] = set()

        # Hierarchy
        self.supers: Dict[URIRef, Set[URIRef]] = {}
        self.subs: Dict[URIRef, Set[URIRef]] = {}
        self.equivs: Dict[URIRef, Set[URIRef]] = {}

        # Properties
        self.object_props: Set[URIRef] = set()
        self.datatype_props: Set[URIRef] = set()
        self.domains: Dict[URIRef, Set[URIRef]] = {}  # prop -> domain classes
        self.ranges: Dict[URIRef, Set[URIRef]] = {}   # prop -> range classes/datatypes

        # Reverse indexes (class -> properties)
        self.by_domain: Dict[URIRef, Set[URIRef]] = {}
        self.by_range: Dict[URIRef, Set[URIRef]] = {}

        # Diagnostics
        self.props_missing_domain: Set[URIRef] = set()
        self.props_missing_range: Set[URIRef] = set()

        self._build()

    def _add_mapset(self, m: Dict[URIRef, Set[URIRef]], k: URIRef, v: URIRef):
        m.setdefault(k, set()).add(v)

    def _build(self):
        # Classes
        for c in self.tbox.subjects(RDF.type, OWL.Class):
            if isinstance(c, URIRef):
                self.classes.add(c)

        # Hierarchy
        for s, o in self.tbox.subject_objects(RDFS.subClassOf):
            if isinstance(s, URIRef) and isinstance(o, URIRef):
                self._add_mapset(self.supers, s, o)
                self._add_mapset(self.subs, o, s)

        for s, o in self.tbox.subject_objects(OWL.equivalentClass):
            if isinstance(s, URIRef) and isinstance(o, URIRef):
                self._add_mapset(self.equivs, s, o)
                self._add_mapset(self.equivs, o, s)

        # Properties: explicit, not "subjects(RDF.type, None)"
        for p in self.tbox.subjects(RDF.type, OWL.ObjectProperty):
            if isinstance(p, URIRef):
                self.object_props.add(p)
        for p in self.tbox.subjects(RDF.type, OWL.DatatypeProperty):
            if isinstance(p, URIRef):
                self.datatype_props.add(p)

        all_props = sorted(self.object_props | self.datatype_props, key=lambda u: qname(self.tbox, u))

        for p in all_props:
            # domain(s)
            ds = set(u for u in self.tbox.objects(p, RDFS.domain) if isinstance(u, URIRef))
            rs = set(u for u in self.tbox.objects(p, RDFS.range) if isinstance(u, URIRef))

            if ds:
                self.domains[p] = ds
                for d in ds:
                    self.by_domain.setdefault(d, set()).add(p)
            else:
                self.props_missing_domain.add(p)

            if rs:
                self.ranges[p] = rs
                for r in rs:
                    self.by_range.setdefault(r, set()).add(p)
            else:
                self.props_missing_range.add(p)

class ShaclIndex:
    def __init__(self, shacl: Graph, tbox: Graph):
        self.shacl = shacl
        self.tbox = tbox
        # targetClass -> shapes
        self.shapes_for_class: Dict[URIRef, List[URIRef]] = {}
        self._build()

    def _build(self):
        for shape, target in self.shacl.subject_objects(SH.targetClass):
            if isinstance(shape, URIRef) and isinstance(target, URIRef):
                self.shapes_for_class.setdefault(target, []).append(shape)

    def constraints_for_class(self, cls: URIRef) -> Dict[str, List[ConstraintLine]]:
        out: Dict[str, List[ConstraintLine]] = {}
        shapes = self.shapes_for_class.get(cls, [])
        for shape in sorted(shapes, key=lambda u: qname(self.shacl, u)):
            shape_name = qname(self.shacl, shape)
            lines: List[ConstraintLine] = []

            for prop_bnode in self.shacl.objects(shape, SH.property):
                path = self.shacl.value(prop_bnode, SH.path)
                if not isinstance(path, URIRef):
                    continue

                min_c = self.shacl.value(prop_bnode, SH.minCount)
                max_c = self.shacl.value(prop_bnode, SH.maxCount)
                datatype = self.shacl.value(prop_bnode, SH.datatype)
                clazz = self.shacl.value(prop_bnode, SH["class"])
                nodekind = self.shacl.value(prop_bnode, SH.nodeKind)
                msg = self.shacl.value(prop_bnode, SH.message)

                dets: List[str] = []
                if min_c is not None:
                    dets.append(f"min:{min_c}")
                if max_c is not None:
                    dets.append(f"max:{max_c}")
                if isinstance(datatype, URIRef):
                    dets.append(f"datatype:{qname(self.tbox, datatype)}")
                if isinstance(clazz, URIRef):
                    dets.append(f"class:{qname(self.tbox, clazz)}")
                if nodekind is not None:
                    dets.append(f"nodeKind:{qname(self.shacl, nodekind) if isinstance(nodekind, URIRef) else str(nodekind)}")
                if msg is not None:
                    dets.append(f"message:{lit_to_str(msg)}")

                details = ", ".join(dets) if dets else "defined"
                lines.append(ConstraintLine(path=qname(self.tbox, path), details=details))

            # Deterministic sort
            lines.sort(key=lambda x: (x.path, x.details))
            out[shape_name] = lines

        return out

class ClassModelBuilder:
    def __init__(self, tbox: Graph, shacl: Graph):
        self.tbox = tbox
        self.ont = OntologyIndex(tbox)
        self.shx = ShaclIndex(shacl, tbox)

    def build_for_class(self, cls: URIRef) -> ClassViewModel:
        fq = qname(self.tbox, cls)

        supers = sorted(self.ont.supers.get(cls, set()), key=lambda u: qname(self.tbox, u))
        subs   = sorted(self.ont.subs.get(cls, set()),   key=lambda u: qname(self.tbox, u))
        equivs = sorted(self.ont.equivs.get(cls, set()), key=lambda u: qname(self.tbox, u))

        # Outgoing properties (by domain)
        outgoing_obj: List[Tuple[URIRef, URIRef]] = []
        outgoing_data: List[Tuple[URIRef, URIRef]] = []

        for p in sorted(self.ont.by_domain.get(cls, set()), key=lambda u: qname(self.tbox, u)):
            p_is_dt = p in self.ont.datatype_props
            ranges = sorted(self.ont.ranges.get(p, set()), key=lambda u: qname(self.tbox, u))
            for r in ranges:
                r_is_xsd = str(r).startswith(str(XSD))
                if p_is_dt or r_is_xsd:
                    outgoing_data.append((p, r))
                else:
                    outgoing_obj.append((p, r))

        # Incoming object properties (by range)
        incoming_obj: List[Tuple[URIRef, URIRef]] = []
        for p in sorted(self.ont.by_range.get(cls, set()), key=lambda u: qname(self.tbox, u)):
            if p not in self.ont.object_props:
                # If it is datatype property but range == focus (unlikely), ignore in incoming_obj
                continue
            domains = sorted(self.ont.domains.get(p, set()), key=lambda u: qname(self.tbox, u))
            for d in domains:
                incoming_obj.append((d, p))

        incoming_obj.sort(key=lambda x: (qname(self.tbox, x[0]), qname(self.tbox, x[1])))
        outgoing_obj.sort(key=lambda x: (qname(self.tbox, x[0]), qname(self.tbox, x[1])))
        outgoing_data.sort(key=lambda x: (qname(self.tbox, x[0]), qname(self.tbox, x[1])))

        # SHACL constraints
        constraints = self.shx.constraints_for_class(cls)

        # Notes (no invention)
        lbl = self.tbox.value(cls, RDFS.label) or self.tbox.value(cls, SKOS.prefLabel)
        definition = self.tbox.value(cls, SKOS.definition) or self.tbox.value(cls, RDFS.comment)
        notes: Dict[str, str] = {
            "QName": fq,
            "URI": str(cls),
        }
        if lbl is not None:
            notes["Label"] = lit_to_str(lbl)
        if definition is not None:
            notes["Definition/Comment"] = lit_to_str(definition)

        # Diagnostics
        diag: Dict[str, int] = {
            "super_count": len(supers),
            "sub_count": len(subs),
            "equiv_count": len(equivs),
            "incoming_obj_count": len(incoming_obj),
            "outgoing_obj_count": len(outgoing_obj),
            "outgoing_data_count": len(outgoing_data),
            "shape_count": len(constraints),
            "constraint_line_count": sum(len(v) for v in constraints.values()),
        }

        # Missing domain/range counts (ontology-wide; also report if any of those touch focus)
        # Touch focus if focus is in domain/range sets, or if property is in by_domain/by_range.
        missing_domain_touch = 0
        for p in self.ont.props_missing_domain:
            # If focus appears as range for p, it touches focus in a relevant way.
            if cls in self.ont.ranges.get(p, set()):
                missing_domain_touch += 1

        missing_range_touch = 0
        for p in self.ont.props_missing_range:
            if cls in self.ont.domains.get(p, set()):
                missing_range_touch += 1

        diag["missing_domain_touch"] = missing_domain_touch
        diag["missing_range_touch"] = missing_range_touch

        return ClassViewModel(
            focus=cls,
            focus_qname=fq,
            supers=supers,
            subs=subs,
            equivs=equivs,
            incoming_obj=incoming_obj,
            outgoing_obj=outgoing_obj,
            outgoing_data=outgoing_data,
            shacl_constraints=constraints,
            notes=notes,
            diag=diag,
        )

class ConsolidatedRenderer:
    def __init__(self, tbox: Graph, out_dir: Path):
        self.tbox = tbox
        self.out_dir = out_dir
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def _new_master(self, name: str) -> Digraph:
        dot = Digraph(name, format="svg")

        # Global layout: stable, readable defaults
        dot.attr(
            rankdir="TB",
            splines="polyline",
            bgcolor="transparent",
            fontname=FONTS["base"],
            fontsize="10",
            nodesep="0.35",
            ranksep="0.45",
            newrank="true",
        )
        dot.attr("node", fontname=FONTS["base"], fontsize="10")
        dot.attr("edge", fontname=FONTS["base"], fontsize="9")
        return dot

    def _panel_cluster(self, dot: Digraph, panel_id: str, title: str, bgcolor: str) -> Digraph:
        """
        Returns a subgraph cluster representing a panel. Adds a required anchor node.
        """
        c = Digraph(name=f"cluster_{panel_id}")
        c.attr(
            label=title,
            labelloc="t",
            labeljust="l",
            style="rounded",
            color=COLORS["panel_border"],
            bgcolor=bgcolor,
            fontname=FONTS["bold"],
            fontsize="11",
            margin="10",
        )
        anchor = f"ANCH_{panel_id}"
        c.node(anchor, label="", shape="point", width="0.01", height="0.01", style="invis")
        dot.subgraph(c)
        return c

    def _add_placeholder(self, c: Digraph, panel_id: str, message: str):
        nid = f"EMPTY_{panel_id}"
        c.node(
            nid,
            label=f"<<TABLE BORDER='0' CELLBORDER='0' CELLPADDING='6'>"
                  f"<TR><TD><FONT COLOR='{COLORS['muted']}'><I>{html.escape(message)}</I></FONT></TD></TR>"
                  f"</TABLE>>",
            shape="plain",
        )

    def _focus_node(self, c: Digraph, panel_id: str, focus_label: str) -> str:
        nid = f"FOCUS_{panel_id}"
        c.node(
            nid,
            label=html.escape(focus_label),
            shape="box",
            style="filled,rounded",
            fillcolor=COLORS["focus"],
            penwidth="2",
            fontname=FONTS["bold"],
            fontsize="12",
        )
        return nid

    def _legend_table(self) -> str:
        rows = (
            f"<TR>"
            f"<TD BGCOLOR='{COLORS['focus']}'>Focus</TD>"
            f"<TD BGCOLOR='{COLORS['super']}'>Superclass</TD>"
            f"<TD BGCOLOR='{COLORS['sub']}'>Subclass</TD>"
            f"<TD BGCOLOR='{COLORS['incoming']}'>Incoming</TD>"
            f"<TD BGCOLOR='{COLORS['outgoing']}'>Outgoing</TD>"
            f"<TD BGCOLOR='{COLORS['datatype']}'>Datatype</TD>"
            f"</TR>"
        )
        return (
            f"<<TABLE BORDER='0' CELLBORDER='1' CELLSPACING='0' CELLPADDING='6' BGCOLOR='{COLORS['header_bg']}'>"
            f"{rows}</TABLE>>"
        )

    def _html_kv_table(self, items: List[Tuple[str, str]], bgcolor: str) -> str:
        tr = []
        for k, v in items:
            tr.append(
                "<TR>"
                f"<TD ALIGN='LEFT'><B>{html.escape(k)}</B></TD>"
                f"<TD ALIGN='LEFT'>{wrap_html(v, width=60) if v else ''}</TD>"
                "</TR>"
            )
        rows = "".join(tr) if tr else "<TR><TD>No data</TD><TD></TD></TR>"
        return (
            f"<<TABLE BORDER='0' CELLBORDER='1' CELLSPACING='0' CELLPADDING='6' BGCOLOR='{bgcolor}'>"
            f"{rows}</TABLE>>"
        )

    def _contract_table(self, vm: ClassViewModel) -> str:
        # Merge all shapes into one table
        if not vm.shacl_constraints or all(len(v) == 0 for v in vm.shacl_constraints.values()):
            return (
                f"<<TABLE BORDER='0' CELLBORDER='0' CELLSPACING='0' CELLPADDING='6' BGCOLOR='{COLORS['contract']}'>"
                f"<TR><TD><I>No constraints defined for this class.</I></TD></TR>"
                f"</TABLE>>"
            )

        rows = []
        for shape_name in sorted(vm.shacl_constraints.keys()):
            rows.append(
                f"<TR><TD ALIGN='LEFT' BGCOLOR='{COLORS['header_bg']}'><B>{html.escape(shape_name)}</B></TD></TR>"
            )
            lines = vm.shacl_constraints[shape_name]
            if not lines:
                rows.append(f"<TR><TD ALIGN='LEFT'><I>No property constraints.</I></TD></TR>")
            else:
                for ln in lines:
                    rows.append(
                        f"<TR><TD ALIGN='LEFT'>&bull; <B>{html.escape(ln.path)}</B> "
                        f"<FONT COLOR='{COLORS['muted']}'>({html.escape(ln.details)})</FONT></TD></TR>"
                    )

        body = "".join(rows)
        return (
            f"<<TABLE BORDER='0' CELLBORDER='0' CELLSPACING='0' CELLPADDING='6' BGCOLOR='{COLORS['contract']}'>"
            f"{body}</TABLE>>"
        )

    def _enforce_grid(self, dot: Digraph, panel_ids: List[List[str]]):
        """
        panel_ids is a 4x2 matrix of panel_id strings.
        Enforce:
          - Each row: anchors are same rank, left-to-right ordering
          - Each column: top-to-bottom ordering
        """
        # Row constraints
        for r in range(4):
            a1 = f"ANCH_{panel_ids[r][0]}"
            a2 = f"ANCH_{panel_ids[r][1]}"
            dot.body.append(f"{{rank=same; {a1}; {a2};}}")
            # Force left-to-right ordering within row
            dot.edge(a1, a2, style="invis", weight="10")

        # Column constraints (top-to-bottom)
        for c in range(2):
            for r in range(3):
                a_top = f"ANCH_{panel_ids[r][c]}"
                a_bot = f"ANCH_{panel_ids[r+1][c]}"
                dot.edge(a_top, a_bot, style="invis", weight="10")

    def render(self, vm: ClassViewModel, filename_base: str):
        dot = self._new_master(filename_base)

        # Define panel IDs in a 4x2 grid
        grid = [
            ["R1C1_HIER", "R1C2_INOBJ"],
            ["R2C1_OUTOBJ", "R2C2_OUTDT"],
            ["R3C1_NOTES", "R3C2_CONTRACT"],
            ["R4C1_DIAG", "R4C2_RESERVED"],
        ]

        # Create clusters
        p_hier     = self._panel_cluster(dot, grid[0][0], "Hierarchy + Legend", COLORS["panel_bg"])
        p_inobj    = self._panel_cluster(dot, grid[0][1], "Incoming Object Associations", COLORS["incoming"])
        p_outobj   = self._panel_cluster(dot, grid[1][0], "Outgoing Object Associations", COLORS["outgoing"])
        p_outdt    = self._panel_cluster(dot, grid[1][1], "Outgoing Datatype Properties", COLORS["datatype"])
        p_notes    = self._panel_cluster(dot, grid[2][0], "Notes / Definition", COLORS["notes"])
        p_contract = self._panel_cluster(dot, grid[2][1], "Contract (SHACL)", COLORS["contract"])
        p_diag     = self._panel_cluster(dot, grid[3][0], "Diagnostics", COLORS["diag"])
        p_res      = self._panel_cluster(dot, grid[3][1], "Reserved", COLORS["reserved"])

        # Enforce 4x2 grid
        self._enforce_grid(dot, grid)

        # -----------------------
        # Panel: Hierarchy+Legend
        # -----------------------
        focus_id = self._focus_node(p_hier, grid[0][0], vm.focus_qname)

        # Legend node
        legend_id = f"LEG_{grid[0][0]}"
        p_hier.node(legend_id, label=self._legend_table(), shape="plain")

        # Arrange: supers (top), focus, subs (bottom), legend to side (in same panel)
        # We use invisible edges to help layout within the panel.
        # Supers
        if vm.supers:
            for s in vm.supers:
                sid = stable_node_id(s, prefix=f"SUP_{grid[0][0]}")
                p_hier.node(sid, label=html.escape(qname(self.tbox, s)), shape="box", style="filled", fillcolor=COLORS["super"])
                p_hier.edge(sid, focus_id, label="subClassOf")
        else:
            # show placeholder for supers (but keep focus visible)
            pass

        # Subs
        if vm.subs:
            for s in vm.subs:
                sid = stable_node_id(s, prefix=f"SUB_{grid[0][0]}")
                p_hier.node(sid, label=html.escape(qname(self.tbox, s)), shape="box", style="filled", fillcolor=COLORS["sub"])
                p_hier.edge(focus_id, sid, label="subClassOf")
        else:
            pass

        # Equivalent classes (shown as a small note box, not misfiled as supers)
        if vm.equivs:
            eq_id = f"EQ_{grid[0][0]}"
            eq_lines = "<BR/>".join(html.escape(qname(self.tbox, e)) for e in vm.equivs[:12])
            if len(vm.equivs) > 12:
                eq_lines += "<BR/><I>…</I>"
            p_hier.node(
                eq_id,
                label=f"<<TABLE BORDER='0' CELLBORDER='1' CELLSPACING='0' CELLPADDING='6'>"
                      f"<TR><TD BGCOLOR='{COLORS['header_bg']}'><B>Equivalent Class</B></TD></TR>"
                      f"<TR><TD ALIGN='LEFT'>{eq_lines}</TD></TR>"
                      f"</TABLE>>",
                shape="plain",
            )
            p_hier.edge(focus_id, eq_id, style="dashed", arrowhead="none")

        # Gentle internal alignment hints
        p_hier.edge(focus_id, legend_id, style="invis", weight="1")

        # -----------------------
        # Panel: Incoming Obj
        # -----------------------
        f_in = self._focus_node(p_inobj, grid[0][1], vm.focus_qname)
        if vm.incoming_obj:
            for d, p in vm.incoming_obj:
                did = stable_node_id(d, prefix=f"IN_{grid[0][1]}")
                p_inobj.node(did, label=html.escape(qname(self.tbox, d)), shape="box", style="filled", fillcolor=COLORS["incoming"])
                p_inobj.edge(did, f_in, label=html.escape(qname(self.tbox, p)))
        else:
            self._add_placeholder(p_inobj, grid[0][1], "No incoming object associations.")

        # -----------------------
        # Panel: Outgoing Obj
        # -----------------------
        f_out = self._focus_node(p_outobj, grid[1][0], vm.focus_qname)
        if vm.outgoing_obj:
            for p, r in vm.outgoing_obj:
                rid = stable_node_id(r, prefix=f"OUT_{grid[1][0]}")
                p_outobj.node(rid, label=html.escape(qname(self.tbox, r)), shape="box", style="filled", fillcolor=COLORS["outgoing"])
                p_outobj.edge(f_out, rid, label=html.escape(qname(self.tbox, p)))
        else:
            self._add_placeholder(p_outobj, grid[1][0], "No outgoing object associations.")

        # -----------------------
        # Panel: Outgoing Datatype
        # -----------------------
        f_dt = self._focus_node(p_outdt, grid[1][1], vm.focus_qname)
        if vm.outgoing_data:
            for p, t in vm.outgoing_data:
                tid = stable_node_id(t, prefix=f"DT_{grid[1][1]}")
                p_outdt.node(tid, label=html.escape(qname(self.tbox, t)), shape="oval", style="filled", fillcolor=COLORS["datatype"])
                p_outdt.edge(f_dt, tid, label=html.escape(qname(self.tbox, p)))
        else:
            self._add_placeholder(p_outdt, grid[1][1], "No outgoing datatype properties.")

        # -----------------------
        # Panel: Notes / Definition
        # -----------------------
        # No invention: we only show what exists, plus URI/QName.
        notes_items = [(k, v) for k, v in vm.notes.items() if v]
        p_notes.node(
            f"NOTES_{grid[2][0]}",
            label=self._html_kv_table(notes_items, bgcolor=COLORS["notes"]),
            shape="plain",
        )
        if not notes_items:
            self._add_placeholder(p_notes, grid[2][0], "No notes available.")

        # -----------------------
        # Panel: Contract (SHACL)
        # -----------------------
        p_contract.node(
            f"CON_{grid[2][1]}",
            label=self._contract_table(vm),
            shape="plain",
        )

        # -----------------------
        # Panel: Diagnostics
        # -----------------------
        diag_items = [
            ("Superclasses", str(vm.diag.get("super_count", 0))),
            ("Subclasses", str(vm.diag.get("sub_count", 0))),
            ("Equivalent Classes", str(vm.diag.get("equiv_count", 0))),
            ("Incoming Obj Assoc", str(vm.diag.get("incoming_obj_count", 0))),
            ("Outgoing Obj Assoc", str(vm.diag.get("outgoing_obj_count", 0))),
            ("Outgoing Datatype Props", str(vm.diag.get("outgoing_data_count", 0))),
            ("SHACL Shapes", str(vm.diag.get("shape_count", 0))),
            ("SHACL Constraint Lines", str(vm.diag.get("constraint_line_count", 0))),
            ("Missing Domain Touch (focus)", str(vm.diag.get("missing_domain_touch", 0))),
            ("Missing Range Touch (focus)", str(vm.diag.get("missing_range_touch", 0))),
        ]
        p_diag.node(
            f"DIAG_{grid[3][0]}",
            label=self._html_kv_table(diag_items, bgcolor=COLORS["diag"]),
            shape="plain",
        )

        # -----------------------
        # Panel: Reserved (placeholder)
        # -----------------------
        self._add_placeholder(p_res, grid[3][1], "Reserved panel (intentionally blank).")

        # Render
        out_path = self.out_dir / f"{filename_base}.svg"
        dot.render(str(out_path.with_suffix("")), cleanup=True)
        return out_path

def _find_default_paths() -> Tuple[Optional[Path], Optional[Path]]:
    root = Path(__file__).resolve().parent
    candidates = [
        (root / "ontology" / "kernel.ttl", root / "ontology" / "kernel.shacl.ttl"),
        (Path("kernel.ttl"), Path("kernel.shacl.ttl")),
        (root.parent / "ontology" / "kernel.ttl", root.parent / "ontology" / "kernel.shacl.ttl"),
    ]
    for t, s in candidates:
        if t.exists() and s.exists():
            return t, s
    return None, None

def _parse_graph(path: Path) -> Graph:
    g = Graph()
    g.parse(str(path), format="turtle")
    return g

def main():
    ap = argparse.ArgumentParser(description="Generate consolidated 4x2 grid SVGs for kernel classes.")
    ap.add_argument("--tbox", type=str, default=None, help="Path to kernel TBox TTL (default: auto-detect).")
    ap.add_argument("--shacl", type=str, default=None, help="Path to kernel SHACL TTL (default: auto-detect).")
    ap.add_argument("--out", type=str, default="viz/consolidated", help="Output directory for SVGs.")
    ap.add_argument("--class", dest="one_class", type=str, default=None,
                    help="Render a single class (QName like 'kern:Stipulation' or full URI).")
    args = ap.parse_args()

    tbox_path: Optional[Path]
    shacl_path: Optional[Path]

    if args.tbox and args.shacl:
        tbox_path = Path(args.tbox)
        shacl_path = Path(args.shacl)
    else:
        tbox_path, shacl_path = _find_default_paths()

    if not tbox_path or not shacl_path or not tbox_path.exists() or not shacl_path.exists():
        print("Error: Could not locate TBox/SHACL TTL files. Provide --tbox and --shacl explicitly.", file=sys.stderr)
        sys.exit(2)

    tbox = _parse_graph(tbox_path)
    shacl = _parse_graph(shacl_path)

    # Bind namespaces for nicer QName output
    tbox.bind("kern", KERN)
    tbox.bind("xsd", XSD)
    shacl.bind("kern", KERN)
    shacl.bind("xsd", XSD)

    builder = ClassModelBuilder(tbox, shacl)
    renderer = ConsolidatedRenderer(tbox, out_dir=Path(args.out))

    # Determine target classes
    targets: List[URIRef] = []
    if args.one_class:
        s = args.one_class.strip()
        if s.startswith("http://") or s.startswith("https://"):
            targets = [URIRef(s)]
        else:
            # QName resolution
            try:
                targets = [tbox.namespace_manager.expand_curie(s)]
            except Exception:
                # fallback: allow "kern_Stipulation" etc
                if s.startswith("kern:"):
                    local = s.split(":", 1)[1]
                    targets = [KERN[local]]
                else:
                    print(f"Error: Unable to resolve class '{s}'. Use full URI or QName like kern:Stipulation.", file=sys.stderr)
                    sys.exit(2)
    else:
        # All OWL classes in kern namespace
        for c in tbox.subjects(RDF.type, OWL.Class):
            if isinstance(c, URIRef) and str(c).startswith(str(KERN)):
                targets.append(c)
        targets = sorted(targets, key=lambda u: qname(tbox, u))

    if not targets:
        print("No target classes found.", file=sys.stderr)
        sys.exit(0)

    print(f"Rendering {len(targets)} class diagrams to: {Path(args.out).resolve()}")
    for cls in targets:
        vm = builder.build_for_class(cls)
        base = qname(tbox, cls).replace(":", "_")
        out_path = renderer.render(vm, base)
        print(f"  - {vm.focus_qname} -> {out_path}")

    print("Done.")

if __name__ == "__main__":
    main()
