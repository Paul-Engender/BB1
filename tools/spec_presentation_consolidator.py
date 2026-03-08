#!/usr/bin/env python3
"""Generate a presentation-style consolidated view for the specs directory."""

from __future__ import annotations

import argparse
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

META_RE = re.compile(r"^\s*(status|version|date|owner)\s*:\s*(.+?)\s*$", re.IGNORECASE)
HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(.+?)\s*$")
BULLET_RE = re.compile(r"^\s*[-*]\s+(.+?)\s*$")
RULE_RE = re.compile(r"^[\s\-_=]{3,}$")


@dataclass
class SpecDoc:
    path: Path
    rel_path: str
    title: str
    status: str
    version: str
    date: str
    owner: str
    summary: str
    highlights: list[str]
    theme: str


def _clean_text(value: str) -> str:
    replacements = {
        "â€“": "-",
        "â€”": "-",
        "â€˜": "'",
        "â€™": "'",
        "â€œ": '"',
        "â€": '"',
        "â€¦": "...",
        "Ã¢â‚¬â€œ": "-",
        "Ã¢â‚¬â„¢": "'",
        "Ã¢â‚¬Å“": '"',
        "Ã¢â‚¬\x9d": '"',
    }
    out = value
    for bad, good in replacements.items():
        out = out.replace(bad, good)
    return out


def _read_text(path: Path) -> str:
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return _clean_text(path.read_text(encoding=encoding))
        except UnicodeDecodeError:
            continue
    return _clean_text(path.read_text(encoding="utf-8", errors="replace"))


def _extract_title(lines: list[str], fallback: str) -> str:
    for line in lines[:80]:
        m = HEADING_RE.match(line)
        if m:
            return m.group(1).strip()
    return fallback


def _extract_meta(lines: list[str]) -> dict[str, str]:
    meta: dict[str, str] = {"status": "", "version": "", "date": "", "owner": ""}
    for line in lines[:120]:
        m = META_RE.match(line)
        if not m:
            continue
        key = m.group(1).lower()
        if not meta[key]:
            meta[key] = m.group(2).strip()
    return meta


def _extract_summary(lines: list[str]) -> str:
    for line in lines[:180]:
        clean = line.strip()
        if clean.lower().startswith(("purpose:", "document intent:", "scope:")):
            _, _, rest = clean.partition(":")
            if rest.strip():
                return rest.strip()

    for line in lines:
        clean = line.strip()
        if not clean:
            continue
        if RULE_RE.match(clean):
            continue
        if HEADING_RE.match(clean):
            continue
        if BULLET_RE.match(clean):
            continue
        if META_RE.match(clean):
            continue
        if clean.startswith("|") and clean.endswith("|"):
            continue
        if clean.startswith("```"):
            continue
        return clean
    return "No summary text found."


def _extract_highlights(lines: list[str]) -> list[str]:
    highlights: list[str] = []

    for line in lines:
        m = BULLET_RE.match(line)
        if not m:
            continue
        item = m.group(1).strip()
        if item and not RULE_RE.match(item) and item not in highlights:
            highlights.append(item)
        if len(highlights) >= 3:
            return highlights

    for line in lines:
        m = HEADING_RE.match(line)
        if not m:
            continue
        item = m.group(1).strip()
        if item and item not in highlights:
            highlights.append(item)
        if len(highlights) >= 3:
            break

    return highlights


def _theme_for(path: Path, specs_dir: Path) -> str:
    rel = path.relative_to(specs_dir).as_posix().lower()
    name = path.name.lower()

    if rel.startswith("spec_upgrade/"):
        return "Spec Upgrade Program"
    if name.startswith("ontoforge_0") or name.startswith("ontoforge_8"):
        return "Canonical Governance Set"
    if name.startswith("ontoforge_9") or name.startswith("integrated project plan"):
        return "Implementation Planning and Backlog"
    if name.startswith("product_") or name.startswith("runtime1_") or name.startswith("runtime2_"):
        return "Product and Runtime Contracts"
    if name.startswith("support_ontology_") or name.startswith("support_release_") or name.startswith("support_to_tbox_"):
        return "Support Ontology Program"
    if name in {"identity_cid_uuidv7.md", "ledger_api_and_ordering.md", "issuerproof_v1.md", "evaluator_boundary_v1.md"}:
        return "Foundation Technical Specs"
    return "Other Specs"


def _status_key(status_value: str) -> str:
    value = (status_value or "").strip()
    if not value:
        return "UNSPECIFIED"
    token = value.split()[0].upper()
    return token.strip(":,.-")


def _scan_specs(specs_dir: Path, excluded_rel_paths: set[str]) -> tuple[list[SpecDoc], list[Path]]:
    md_paths = sorted(p for p in specs_dir.rglob("*.md") if p.relative_to(specs_dir).as_posix() not in excluded_rel_paths)
    other_paths = sorted(
        p for p in specs_dir.rglob("*") if p.is_file() and p.suffix.lower() not in {".md"}
    )

    docs: list[SpecDoc] = []
    for path in md_paths:
        text = _read_text(path)
        lines = text.splitlines()
        meta = _extract_meta(lines)
        docs.append(
            SpecDoc(
                path=path,
                rel_path=path.relative_to(specs_dir).as_posix(),
                title=_extract_title(lines, path.stem.replace("_", " ")),
                status=meta["status"],
                version=meta["version"],
                date=meta["date"],
                owner=meta["owner"],
                summary=_extract_summary(lines),
                highlights=_extract_highlights(lines),
                theme=_theme_for(path, specs_dir),
            )
        )
    return docs, [p.relative_to(specs_dir) for p in other_paths]


def _emit_markdown(docs: list[SpecDoc], other_assets: list[Path], title: str, specs_dir: Path) -> str:
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    theme_map: dict[str, list[SpecDoc]] = defaultdict(list)
    status_counts = Counter()

    for doc in docs:
        theme_map[doc.theme].append(doc)
        status_counts[_status_key(doc.status)] += 1

    lines: list[str] = []
    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"Generated: `{now}`")
    lines.append(f"Source root: `{specs_dir.as_posix()}`")
    lines.append("")
    lines.append("## Executive View")
    lines.append("")
    lines.append(f"- Total markdown specs: **{len(docs)}**")
    lines.append(f"- Additional non-markdown assets: **{len(other_assets)}**")
    lines.append("- Status distribution:")
    for key, count in sorted(status_counts.items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"  - `{key}`: {count}")
    lines.append("")

    lines.append("## Theme Portfolio")
    lines.append("")
    lines.append("| Theme | Document Count |")
    lines.append("| --- | ---: |")
    for theme in sorted(theme_map):
        lines.append(f"| {theme} | {len(theme_map[theme])} |")
    lines.append("")

    lines.append("## Presentation Cards")
    lines.append("")
    for theme in sorted(theme_map):
        lines.append(f"### {theme}")
        lines.append("")
        for doc in sorted(theme_map[theme], key=lambda d: d.rel_path.lower()):
            lines.append(f"#### {doc.title}")
            lines.append("")
            lines.append(f"- File: `specs/{doc.rel_path}`")
            lines.append(f"- Status: `{doc.status or 'UNSPECIFIED'}`")
            lines.append(f"- Version: `{doc.version or 'UNSPECIFIED'}`")
            lines.append(f"- Date: `{doc.date or 'UNSPECIFIED'}`")
            lines.append(f"- Owner: `{doc.owner or 'UNSPECIFIED'}`")
            lines.append(f"- Summary: {doc.summary}")
            if doc.highlights:
                lines.append("- Highlights:")
                for item in doc.highlights:
                    lines.append(f"  - {item}")
            lines.append("")

    lines.append("## Non-Markdown Assets Annex")
    lines.append("")
    if other_assets:
        for asset in other_assets:
            lines.append(f"- `specs/{asset.as_posix()}`")
    else:
        lines.append("- None")
    lines.append("")
    return "\n".join(lines)


def build_presentation(specs_dir: Path, output_path: Path, title: str) -> None:
    excluded_rel: set[str] = set()
    if output_path.is_relative_to(specs_dir):
        excluded_rel.add(output_path.relative_to(specs_dir).as_posix())
    docs, other_assets = _scan_specs(specs_dir, excluded_rel)
    content = _emit_markdown(docs, other_assets, title, specs_dir)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate consolidated presentation view for specs.")
    parser.add_argument("--specs-dir", default="specs", help="Path to specs directory.")
    parser.add_argument(
        "--output",
        default="specs/specs_presentation_consolidated.md",
        help="Output markdown file path.",
    )
    parser.add_argument(
        "--title",
        default="Specs Consolidated Presentation",
        help="Presentation document title.",
    )
    args = parser.parse_args()

    specs_dir = Path(args.specs_dir).resolve()
    output_path = Path(args.output).resolve()
    if not specs_dir.exists():
        raise SystemExit(f"specs-dir does not exist: {specs_dir}")
    build_presentation(specs_dir, output_path, args.title)
    print(f"Wrote consolidated presentation: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


