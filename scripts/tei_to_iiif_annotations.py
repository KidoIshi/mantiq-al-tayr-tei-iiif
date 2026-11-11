#!/usr/bin/env python3
"""Convert TEI line-to-zone links into one IIIF AnnotationPage per Canvas."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote

from lxml import etree


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEI = ROOT / "data" / "tei" / "bnf-persan-348-f6-sample.xml"
DEFAULT_OUTPUT_DIR = ROOT / "iiif"
DEFAULT_BASE_URL = "https://kidoishi.github.io/mantiq-al-tayr-tei-iiif"
NS = {"tei": "http://www.tei-c.org/ns/1.0"}
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"


def diplomatic_text(line: etree._Element) -> str:
    """Return line text while selecting orig (not reg) inside every choice."""

    def collect(node: etree._Element) -> str:
        parts: list[str] = [node.text or ""]
        for child in node:
            if child.tag == f"{{{NS['tei']}}}choice":
                orig = child.find("tei:orig", namespaces=NS)
                if orig is None:
                    raise ValueError(f"choice without orig in {line.get(XML_ID)}")
                parts.append("".join(orig.itertext()))
            else:
                parts.append(collect(child))
            parts.append(child.tail or "")
        return "".join(parts)

    return " ".join(collect(line).split())


def surface_token(surface: etree._Element) -> str:
    """Return a stable filename token such as f6 from a TEI surface."""

    candidate = surface.get("n", "")
    if candidate.startswith("scan-"):
        candidate = candidate.removeprefix("scan-")
    if not candidate:
        candidate = (surface.get(XML_ID) or "surface").rsplit(".", 1)[-1]
    if not re.fullmatch(r"[A-Za-z0-9._-]+", candidate):
        raise ValueError(f"Unsafe surface token: {candidate!r}")
    return candidate


def annotation_filename(surface: etree._Element) -> str:
    return f"bnf-persan-348-{surface_token(surface)}-annotations.json"


def build_annotation_pages(tei_path: Path, base_url: str) -> dict[str, dict]:
    document = etree.parse(str(tei_path))
    zone_bindings: dict[str, tuple[etree._Element, etree._Element]] = {}
    for surface in document.xpath("//tei:surface", namespaces=NS):
        for zone in surface.xpath("./tei:zone", namespaces=NS):
            zone_id = zone.get(XML_ID)
            if not zone_id or zone_id in zone_bindings:
                raise ValueError(f"Missing or duplicate zone xml:id: {zone_id!r}")
            zone_bindings[zone_id] = (zone, surface)

    grouped_lines: dict[str, list[tuple[etree._Element, etree._Element]]] = defaultdict(list)
    surfaces_by_file: dict[str, etree._Element] = {}
    for line in document.xpath("//tei:lg[@type='couplet']/tei:l", namespaces=NS):
        line_id = line.get(XML_ID)
        facs = line.get("facs", "")
        if not line_id or not facs.startswith("#"):
            raise ValueError("Every line must have xml:id and a local @facs reference")
        binding = zone_bindings.get(facs[1:])
        if binding is None:
            raise ValueError(f"Missing zone {facs} for {line_id}")
        zone, surface = binding
        filename = annotation_filename(surface)
        if filename in surfaces_by_file and surfaces_by_file[filename] is not surface:
            raise ValueError(f"More than one surface maps to {filename}")
        surfaces_by_file[filename] = surface
        grouped_lines[filename].append((line, zone))

    pages: dict[str, dict] = {}
    for filename, bindings in sorted(grouped_lines.items()):
        surface = surfaces_by_file[filename]
        canvas = surface.get("corresp", "")
        if not canvas.startswith(("http://", "https://")):
            raise ValueError(f"surface {surface.get(XML_ID)} lacks an HTTP(S) Canvas @corresp")
        page_url = f"{base_url.rstrip('/')}/iiif/{filename}"
        items: list[dict] = []
        for line, zone in bindings:
            line_id = line.get(XML_ID)
            x = int(zone.get("ulx"))
            y = int(zone.get("uly"))
            width = int(zone.get("lrx")) - x
            height = int(zone.get("lry")) - y
            items.append(
                {
                    "id": f"{page_url}#{quote(line_id, safe='.-')}",
                    "type": "Annotation",
                    "motivation": "supplementing",
                    "body": {
                        "type": "TextualBody",
                        "value": diplomatic_text(line),
                        "format": "text/plain",
                        "language": "fa",
                    },
                    "target": f"{canvas}#xywh={x},{y},{width},{height}",
                }
            )
        pages[filename] = {
            "@context": "http://iiif.io/api/presentation/3/context.json",
            "id": page_url,
            "type": "AnnotationPage",
            "label": {"ja": [f"Persan 348 {surface.get('n')} 外交的転写"]},
            "partOf": [{"id": canvas, "type": "Canvas"}],
            "items": items,
        }
    return pages


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tei", type=Path, default=DEFAULT_TEI)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    args = parser.parse_args()
    tei_path = args.tei if args.tei.is_absolute() else ROOT / args.tei
    output_dir = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    pages = build_annotation_pages(tei_path, args.base_url)
    annotation_total = 0
    for filename, page in pages.items():
        output_path = output_dir / filename
        output_path.write_text(json.dumps(page, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        annotation_total += len(page["items"])
        print(f"Wrote {len(page['items'])} annotations to {output_path}")
    print(f"Wrote {annotation_total} annotations across {len(pages)} Canvas-specific pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
