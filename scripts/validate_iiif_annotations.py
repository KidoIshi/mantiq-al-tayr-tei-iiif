#!/usr/bin/env python3
"""Cross-check an IIIF AnnotationPage against the TEI lines and zones that generated it."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from lxml import etree

from tei_to_iiif_annotations import NS, diplomatic_text


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEI = ROOT / "data" / "tei" / "bnf-persan-348-f6-sample.xml"
DEFAULT_ANNOTATIONS = ROOT / "iiif" / "bnf-persan-348-f6-annotations.json"
DEFAULT_REPORT = ROOT / "outputs" / "iiif-annotation-validation.json"
EXPECTED_CANVAS = "https://gallica.bnf.fr/iiif/ark:/12148/btv1b10091505x/canvas/f6"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def expected_items(tei_path: Path) -> dict[str, dict]:
    document = etree.parse(str(tei_path))
    zones = {
        zone.get("{http://www.w3.org/XML/1998/namespace}id"): zone
        for zone in document.xpath("//tei:zone", namespaces=NS)
    }
    expected: dict[str, dict] = {}
    for line in document.xpath("//tei:lg[@type='couplet']/tei:l", namespaces=NS):
        line_id = line.get("{http://www.w3.org/XML/1998/namespace}id")
        zone = zones[line.get("facs")[1:]]
        x, y = int(zone.get("ulx")), int(zone.get("uly"))
        width = int(zone.get("lrx")) - x
        height = int(zone.get("lry")) - y
        expected[line_id] = {
            "value": diplomatic_text(line),
            "target": f"{EXPECTED_CANVAS}#xywh={x},{y},{width},{height}",
        }
    return expected


def validate(tei_path: Path, annotation_path: Path) -> dict:
    data = json.loads(annotation_path.read_text(encoding="utf-8"))
    expected = expected_items(tei_path)
    errors: list[str] = []
    items = data.get("items", [])

    if data.get("@context") != "http://iiif.io/api/presentation/3/context.json":
        errors.append("Unexpected or missing IIIF Presentation 3 context")
    if data.get("type") != "AnnotationPage":
        errors.append("Top-level type is not AnnotationPage")
    if not str(data.get("id", "")).startswith(("http://", "https://")):
        errors.append("AnnotationPage id is not an HTTP(S) URI")
    if len(items) != len(expected):
        errors.append(f"Expected {len(expected)} annotations, found {len(items)}")

    seen: set[str] = set()
    for item in items:
        annotation_id = str(item.get("id", ""))
        line_id = annotation_id.rsplit("#", 1)[-1]
        if line_id in seen:
            errors.append(f"Duplicate annotation for {line_id}")
        seen.add(line_id)
        if line_id not in expected:
            errors.append(f"Unknown TEI line in annotation id: {line_id}")
            continue
        if item.get("type") != "Annotation" or item.get("motivation") != "supplementing":
            errors.append(f"Invalid type or motivation for {line_id}")
        body = item.get("body", {})
        if body.get("type") != "TextualBody" or body.get("language") != "fa":
            errors.append(f"Invalid TextualBody metadata for {line_id}")
        if body.get("value") != expected[line_id]["value"]:
            errors.append(f"Diplomatic text mismatch for {line_id}")
        if item.get("target") != expected[line_id]["target"]:
            errors.append(f"Canvas region mismatch for {line_id}")

    missing = sorted(set(expected) - seen)
    errors.extend(f"Missing annotation for {line_id}" for line_id in missing)
    checks = {
        "json_parsed": True,
        "iiif_presentation_3_shape": not any("context" in e or "type" in e or "HTTP" in e for e in errors),
        "annotation_count_matches_tei": len(items) == len(expected),
        "all_tei_lines_matched": not missing and len(seen) == len(expected),
        "diplomatic_text_matches_tei": not any("text mismatch" in e for e in errors),
        "canvas_regions_match_tei_zones": not any("region mismatch" in e for e in errors),
    }
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "tei_file": str(tei_path.relative_to(ROOT)),
        "tei_sha256": sha256(tei_path),
        "annotation_page": str(annotation_path.relative_to(ROOT)),
        "annotation_page_sha256": sha256(annotation_path),
        "canvas": EXPECTED_CANVAS,
        "checks": checks,
        "counts": {"tei_lines": len(expected), "annotations": len(items)},
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tei", type=Path, default=DEFAULT_TEI)
    parser.add_argument("--annotations", type=Path, default=DEFAULT_ANNOTATIONS)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    tei_path = args.tei if args.tei.is_absolute() else ROOT / args.tei
    annotation_path = args.annotations if args.annotations.is_absolute() else ROOT / args.annotations
    report_path = args.report if args.report.is_absolute() else ROOT / args.report
    report = validate(tei_path, annotation_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if all(report["checks"].values()) and not report["errors"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
