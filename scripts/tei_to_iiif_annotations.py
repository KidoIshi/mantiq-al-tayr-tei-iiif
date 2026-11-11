#!/usr/bin/env python3
"""Convert TEI line-to-zone links into an IIIF Presentation 3 AnnotationPage."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import quote

from lxml import etree


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEI = ROOT / "data" / "tei" / "bnf-persan-348-f6-sample.xml"
DEFAULT_OUTPUT = ROOT / "iiif" / "bnf-persan-348-f6-annotations.json"
DEFAULT_CANVAS = "https://gallica.bnf.fr/iiif/ark:/12148/btv1b10091505x/canvas/f6"
DEFAULT_BASE_URL = "https://kidoishi.github.io/mantiq-al-tayr-tei-iiif"
NS = {"tei": "http://www.tei-c.org/ns/1.0"}


def diplomatic_text(line: etree._Element) -> str:
    """Return line text while selecting orig (not reg) inside every choice."""

    def collect(node: etree._Element) -> str:
        parts: list[str] = [node.text or ""]
        for child in node:
            if child.tag == f"{{{NS['tei']}}}choice":
                orig = child.find("tei:orig", namespaces=NS)
                if orig is None:
                    raise ValueError(f"choice without orig in {line.get('{http://www.w3.org/XML/1998/namespace}id')}")
                parts.append("".join(orig.itertext()))
            else:
                parts.append(collect(child))
            parts.append(child.tail or "")
        return "".join(parts)

    return " ".join(collect(line).split())


def build_annotation_page(tei_path: Path, canvas: str, base_url: str) -> dict:
    document = etree.parse(str(tei_path))
    zones = {
        zone.get("{http://www.w3.org/XML/1998/namespace}id"): zone
        for zone in document.xpath("//tei:zone", namespaces=NS)
    }
    page_url = f"{base_url.rstrip('/')}/iiif/bnf-persan-348-f6-annotations.json"
    items: list[dict] = []

    for line in document.xpath("//tei:lg[@type='couplet']/tei:l", namespaces=NS):
        line_id = line.get("{http://www.w3.org/XML/1998/namespace}id")
        facs = line.get("facs", "")
        if not line_id or not facs.startswith("#"):
            raise ValueError("Every line must have xml:id and a local @facs reference")
        zone = zones.get(facs[1:])
        if zone is None:
            raise ValueError(f"Missing zone {facs} for {line_id}")
        x = int(zone.get("ulx"))
        y = int(zone.get("uly"))
        width = int(zone.get("lrx")) - x
        height = int(zone.get("lry")) - y
        annotation_id = f"{page_url}#{quote(line_id, safe='.-')}"
        items.append(
            {
                "id": annotation_id,
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

    return {
        "@context": "http://iiif.io/api/presentation/3/context.json",
        "id": page_url,
        "type": "AnnotationPage",
        "label": {"ja": ["Persan 348 scan f6 外交的転写（プロジェクト担当研究者が画像と照合した12対句）"]},
        "items": items,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tei", type=Path, default=DEFAULT_TEI)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--canvas", default=DEFAULT_CANVAS)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    args = parser.parse_args()
    tei_path = args.tei if args.tei.is_absolute() else ROOT / args.tei
    output_path = args.output if args.output.is_absolute() else ROOT / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    page = build_annotation_page(tei_path, args.canvas, args.base_url)
    output_path.write_text(json.dumps(page, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(page['items'])} annotations to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
