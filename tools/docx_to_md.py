#!/usr/bin/env python3
"""Convert DOCX files to Markdown using document.xml parsing.

This is a lightweight converter for project documentation migration.
It maps headings, list paragraphs, plain paragraphs, and tables.
"""

from __future__ import annotations

import argparse
import re
import zipfile
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree as ET


NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def _strip(text: str) -> str:
    return re.sub(r"[ \t]+", " ", text or "").strip()


def _escape_cell(text: str) -> str:
    return text.replace("|", r"\|")


def _p_text(p: ET.Element) -> str:
    chunks: list[str] = []
    for node in p.iter():
        tag = node.tag.rsplit("}", 1)[-1]
        if tag == "t":
            chunks.append(node.text or "")
        elif tag == "tab":
            chunks.append("\t")
        elif tag in {"br", "cr"}:
            chunks.append("\n")
    return _strip("".join(chunks))


def _heading_level(p: ET.Element) -> int | None:
    p_style = p.find("./w:pPr/w:pStyle", NS)
    if p_style is None:
        return None
    val = p_style.attrib.get(f"{{{NS['w']}}}val", "")
    if not val:
        return None
    m = re.match(r"Heading([1-6])$", val)
    if m:
        return int(m.group(1))
    if val in {"Title", "Subtitle"}:
        return 1
    return None


def _list_prefix(p: ET.Element) -> str | None:
    ilvl = p.find("./w:pPr/w:numPr/w:ilvl", NS)
    num_id = p.find("./w:pPr/w:numPr/w:numId", NS)
    if ilvl is None or num_id is None:
        return None
    lvl = int(ilvl.attrib.get(f"{{{NS['w']}}}val", "0"))
    indent = "  " * lvl
    return f"{indent}- "


def _table_to_md(tbl: ET.Element) -> list[str]:
    rows: list[list[str]] = []
    for tr in tbl.findall("./w:tr", NS):
        cells: list[str] = []
        for tc in tr.findall("./w:tc", NS):
            para_texts = [_p_text(p) for p in tc.findall("./w:p", NS)]
            para_texts = [t for t in para_texts if t]
            cell_text = " <br> ".join(para_texts)
            cells.append(_escape_cell(cell_text))
        if cells:
            rows.append(cells)

    if not rows:
        return []

    width = max(len(r) for r in rows)
    for r in rows:
        if len(r) < width:
            r.extend([""] * (width - len(r)))

    out: list[str] = []
    header = rows[0]
    out.append("| " + " | ".join(header) + " |")
    out.append("| " + " | ".join(["---"] * width) + " |")
    for r in rows[1:]:
        out.append("| " + " | ".join(r) + " |")
    return out


def docx_to_markdown(docx_path: Path) -> str:
    with zipfile.ZipFile(docx_path) as zf:
        xml = zf.read("word/document.xml")
    root = ET.fromstring(xml)
    body = root.find("./w:body", NS)
    if body is None:
        return ""

    lines: list[str] = []

    for child in body:
        tag = child.tag.rsplit("}", 1)[-1]
        if tag == "p":
            text = _p_text(child)
            if not text:
                if lines and lines[-1] != "":
                    lines.append("")
                continue
            h = _heading_level(child)
            if h is not None:
                lines.append(f"{'#' * h} {text}")
                lines.append("")
                continue

            prefix = _list_prefix(child)
            if prefix is not None:
                lines.append(f"{prefix}{text}")
            else:
                lines.append(text)
            lines.append("")
        elif tag == "tbl":
            tbl_lines = _table_to_md(child)
            if tbl_lines:
                lines.extend(tbl_lines)
                lines.append("")

    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines) + "\n"


def find_docx_files(root: Path) -> Iterable[Path]:
    for p in root.rglob("*.md"):
        if p.is_file():
            yield p


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert DOCX files to Markdown")
    parser.add_argument("--root", default="specs", help="Root folder to scan for .md files")
    parser.add_argument("--delete-source", action="store_true", help="Delete .md files after conversion")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    converted = 0
    for docx in sorted(find_docx_files(root)):
        md_path = docx.with_suffix(".md")
        md_text = docx_to_markdown(docx)
        md_path.write_text(md_text, encoding="utf-8")
        converted += 1
        if args.delete_source:
            docx.unlink()
        print(f"converted: {docx} -> {md_path}")

    print(f"total converted: {converted}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
