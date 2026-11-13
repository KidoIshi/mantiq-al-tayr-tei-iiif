#!/usr/bin/env python3
"""Cross-check Canvas-specific IIIF AnnotationPages against their TEI lines and zones."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from lxml import etree

from tei_to_iiif_annotations import NS, XML_ID, annotation_filename


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEI = ROOT / "data" / "tei" / "bnf-persan-348-f6-sample.xml"
DEFAULT_ANNOTATION_DIR = ROOT / "iiif"
DEFAULT_REPORT = ROOT / "outputs" / "iiif-annotation-validation.json"
MANIFEST_REGISTRY = ROOT / "iiif" / "manifest-registry.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def expected_diplomatic_text(line: etree._Element, witness: str) -> str:
    """Independently derive the expected text without using the generator's extractor."""

    def render(node: etree._Element) -> str:
        chunks: list[str] = [node.text or ""]
        for child in node:
            if child.tag == f"{{{NS['tei']}}}choice":
                originals = child.xpath("./tei:orig", namespaces=NS)
                if len(originals) != 1:
                    raise ValueError(f"Expected one orig in {line.get(XML_ID)}")
                chunks.append("".join(originals[0].itertext()))
            elif child.tag == f"{{{NS['tei']}}}app":
                readings = child.xpath("./tei:lem | ./tei:rdg", namespaces=NS)
                matches = [
                    reading for reading in readings
                    if witness in (reading.get("wit") or "").split()
                ]
                if len(matches) != 1:
                    raise ValueError(
                        f"Expected one apparatus reading for {witness} in {line.get(XML_ID)}"
                    )
                chunks.append(render(matches[0]))
            elif child.tag == f"{{{NS['tei']}}}gap":
                chunks.append("[…]")
            elif child.tag in {f"{{{NS['tei']}}}note", f"{{{NS['tei']}}}fw"}:
                pass
            else:
                chunks.append(render(child))
            chunks.append(child.tail or "")
        return "".join(chunks)

    return " ".join(render(line).split())


def expected_uncertainty_comments(
    line: etree._Element,
    witness: str,
    notes_by_target: dict[str, str],
) -> list[str]:
    """Independently derive comments required for selected unclear readings."""

    selected: list[etree._Element] = []

    def visit(node: etree._Element) -> None:
        for child in node:
            if child.tag == f"{{{NS['tei']}}}choice":
                originals = child.xpath("./tei:orig", namespaces=NS)
                if len(originals) != 1:
                    raise ValueError(f"Expected one orig in {line.get(XML_ID)}")
                visit(originals[0])
            elif child.tag == f"{{{NS['tei']}}}app":
                readings = child.xpath("./tei:lem | ./tei:rdg", namespaces=NS)
                matches = [item for item in readings if witness in (item.get("wit") or "").split()]
                if len(matches) != 1:
                    raise ValueError(
                        f"Expected one apparatus reading for {witness} in {line.get(XML_ID)}"
                    )
                visit(matches[0])
            elif child.tag in {f"{{{NS['tei']}}}note", f"{{{NS['tei']}}}fw"}:
                continue
            else:
                if child.tag == f"{{{NS['tei']}}}unclear":
                    selected.append(child)
                visit(child)

    visit(line)
    comments: list[str] = []
    for unclear in selected:
        identifiers = [unclear.get(XML_ID, ""), (unclear.get("corresp") or "").removeprefix("#")]
        note = next((notes_by_target[item] for item in identifiers if item in notes_by_target), "")
        comments.append(
            note or f"The reading {''.join(unclear.itertext())!r} is marked unclear in the TEI source."
        )
    return comments


def expected_pages(tei_path: Path) -> dict[str, dict]:
    document = etree.parse(str(tei_path))
    notes_by_target = {
        (note.get("target") or "").removeprefix("#"): " ".join(note.itertext()).strip()
        for note in document.xpath("//tei:note[@target]", namespaces=NS)
    }
    zones: dict[str, tuple[etree._Element, etree._Element]] = {}
    for surface in document.xpath("//tei:surface", namespaces=NS):
        for zone in surface.xpath("./tei:zone", namespaces=NS):
            zones[zone.get(XML_ID)] = (zone, surface)

    expected: dict[str, dict] = defaultdict(lambda: {"canvas": "", "items": {}})
    for line in document.xpath("//tei:lg[@type='couplet']/tei:l", namespaces=NS):
        line_id = line.get(XML_ID)
        zone, surface = zones[line.get("facs")[1:]]
        filename = annotation_filename(surface)
        canvas = surface.get("corresp", "")
        if expected[filename]["canvas"] not in ("", canvas):
            raise ValueError(f"Conflicting Canvas values for {filename}")
        expected[filename]["canvas"] = canvas
        x, y = int(zone.get("ulx")), int(zone.get("uly"))
        width = int(zone.get("lrx")) - x
        height = int(zone.get("lry")) - y
        source_div = line.xpath("ancestor::tei:div[@source][1]/@source", namespaces=NS)
        witness = source_div[0] if source_div else "#wit-bnf348"
        expected[filename]["items"][line_id] = {
            "value": expected_diplomatic_text(line, witness),
            "comments": expected_uncertainty_comments(line, witness, notes_by_target),
            "target": f"{canvas}#xywh={x},{y},{width},{height}",
        }
    return dict(expected)


def validate(tei_path: Path, annotation_dir: Path) -> dict:
    expected = expected_pages(tei_path)
    annotation_paths = sorted(annotation_dir.glob("bnf-persan-348-*-annotations.json"))
    annotation_paths.extend(sorted(annotation_dir.glob("fsc-ms-28-*-annotations.json")))
    actual = {path.name: path for path in annotation_paths}
    errors: list[str] = []
    document = etree.parse(str(tei_path))
    registry = json.loads(MANIFEST_REGISTRY.read_text(encoding="utf-8"))
    registry_dimensions = {
        canvas["id"]: (int(canvas["width"]), int(canvas["height"]))
        for record in registry.get("records", [])
        for canvas in record.get("sample_canvases", [])
    }
    for surface in document.xpath("//tei:surface", namespaces=NS):
        canvas = surface.get("corresp", "")
        dimensions = (int(surface.get("lrx", "0")), int(surface.get("lry", "0")))
        if registry_dimensions.get(canvas) != dimensions:
            errors.append(
                f"Canvas dimensions mismatch for {canvas}: TEI {dimensions}, "
                f"registry {registry_dimensions.get(canvas)}"
            )
        for zone in surface.xpath("./tei:zone", namespaces=NS):
            coordinates = tuple(int(zone.get(name, "0")) for name in ("ulx", "uly", "lrx", "lry"))
            if not (0 <= coordinates[0] < coordinates[2] <= dimensions[0]
                    and 0 <= coordinates[1] < coordinates[3] <= dimensions[1]):
                errors.append(f"Zone outside Canvas dimensions: {zone.get(XML_ID)} {coordinates}")
    expected_files = set(expected)
    actual_files = set(actual)
    for filename in sorted(expected_files - actual_files):
        errors.append(f"Missing AnnotationPage file: {filename}")
    for filename in sorted(actual_files - expected_files):
        errors.append(f"Unexpected AnnotationPage file: {filename}")

    total_expected = 0
    total_annotations = 0
    all_seen: set[str] = set()
    page_reports: list[dict] = []
    for filename in sorted(expected_files & actual_files):
        path = actual[filename]
        data = json.loads(path.read_text(encoding="utf-8"))
        page_expected = expected[filename]
        expected_items = page_expected["items"]
        items = data.get("items", [])
        total_expected += len(expected_items)
        total_annotations += len(items)
        page_errors: list[str] = []
        if data.get("@context") != "http://iiif.io/api/presentation/3/context.json":
            page_errors.append("Unexpected or missing IIIF Presentation 3 context")
        if data.get("type") != "AnnotationPage":
            page_errors.append("Top-level type is not AnnotationPage")
        if not str(data.get("id", "")).startswith(("http://", "https://")):
            page_errors.append("AnnotationPage id is not an HTTP(S) URI")
        if data.get("rights") != "https://creativecommons.org/licenses/by/4.0/":
            page_errors.append("AnnotationPage does not identify the project data rights URI")
        if len(items) != len(expected_items):
            page_errors.append(f"Expected {len(expected_items)} annotations, found {len(items)}")

        page_seen: set[str] = set()
        for item in items:
            annotation_id = str(item.get("id", ""))
            line_id = annotation_id.rsplit("#", 1)[-1]
            if line_id in page_seen or line_id in all_seen:
                page_errors.append(f"Duplicate annotation for {line_id}")
            page_seen.add(line_id)
            all_seen.add(line_id)
            if line_id not in expected_items:
                page_errors.append(f"Unknown TEI line in annotation id: {line_id}")
                continue
            if item.get("type") != "Annotation" or item.get("motivation") != "supplementing":
                page_errors.append(f"Invalid type or motivation for {line_id}")
            raw_body = item.get("body", {})
            bodies = raw_body if isinstance(raw_body, list) else [raw_body]
            transcription_bodies = [
                body for body in bodies
                if body.get("type") == "TextualBody"
                and body.get("language") == "fa"
                and body.get("purpose") != "commenting"
            ]
            comment_bodies = [
                body for body in bodies
                if body.get("type") == "TextualBody" and body.get("purpose") == "commenting"
            ]
            if len(transcription_bodies) != 1:
                page_errors.append(f"Invalid TextualBody metadata for {line_id}")
                transcription_body = {}
            else:
                transcription_body = transcription_bodies[0]
            if transcription_body.get("value") != expected_items[line_id]["value"]:
                page_errors.append(f"Diplomatic text mismatch for {line_id}")
            if [body.get("value") for body in comment_bodies] != expected_items[line_id]["comments"]:
                page_errors.append(f"Uncertainty comment mismatch for {line_id}")
            if item.get("target") != expected_items[line_id]["target"]:
                page_errors.append(f"Canvas region mismatch for {line_id}")
        missing = sorted(set(expected_items) - page_seen)
        page_errors.extend(f"Missing annotation for {line_id}" for line_id in missing)
        errors.extend(f"{filename}: {message}" for message in page_errors)
        page_reports.append(
            {
                "annotation_page": str(path.relative_to(ROOT)),
                "annotation_page_sha256": sha256(path),
                "canvas": page_expected["canvas"],
                "tei_lines": len(expected_items),
                "annotations": len(items),
                "errors": page_errors,
            }
        )

    expected_line_ids = {line_id for page in expected.values() for line_id in page["items"]}
    checks = {
        "json_parsed": True,
        "canvas_specific_page_set_matches_tei": expected_files == actual_files,
        "iiif_presentation_3_shape": not any(
            term in error for error in errors for term in ("context", "type", "HTTP", "partOf")
        ),
        "annotation_count_matches_tei": total_annotations == total_expected,
        "all_tei_lines_matched": all_seen == expected_line_ids,
        "diplomatic_text_matches_tei": not any("text mismatch" in error for error in errors),
        "uncertainty_comments_match_tei": not any("Uncertainty comment mismatch" in error for error in errors),
        "canvas_regions_match_tei_zones": not any("region mismatch" in error for error in errors),
        "canvas_dimensions_match_registry": not any(
            "dimensions" in error or "Zone outside" in error for error in errors
        ),
    }
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "tei_file": str(tei_path.relative_to(ROOT)),
        "tei_sha256": sha256(tei_path),
        "annotation_pages": page_reports,
        "checks": checks,
        "counts": {
            "canvases": len(expected),
            "annotation_pages": len(actual),
            "tei_lines": len(expected_line_ids),
            "annotations": total_annotations,
        },
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tei", type=Path, default=DEFAULT_TEI)
    parser.add_argument("--annotation-dir", type=Path, default=DEFAULT_ANNOTATION_DIR)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    tei_path = args.tei if args.tei.is_absolute() else ROOT / args.tei
    annotation_dir = args.annotation_dir if args.annotation_dir.is_absolute() else ROOT / args.annotation_dir
    report_path = args.report if args.report.is_absolute() else ROOT / args.report
    report = validate(tei_path, annotation_dir)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if all(report["checks"].values()) and not report["errors"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
