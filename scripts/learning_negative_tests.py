#!/usr/bin/env python3
"""Run safe learning failures against temporary copies of the released data.

This script never edits the authoritative TEI, generated IIIF files, or release
reports.  It creates temporary copies under work/, introduces one controlled
error at a time, and records which validation layer detects the error.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from lxml import etree

import validate as project_validation
from tei_to_iiif_annotations import NS, XML_ID, build_annotation_pages
from validate_iiif_annotations import validate as validate_annotations


ROOT = Path(__file__).resolve().parents[1]
SOURCE_TEI = ROOT / "data" / "tei" / "bnf-persan-348-f6-sample.xml"
WORK = ROOT / "work"
REPORT = WORK / "learning-negative-tests.json"


def write_document(document: etree._ElementTree, path: Path) -> None:
    document.write(path, encoding="utf-8", xml_declaration=True, pretty_print=True)


def remove_second_hemistich(temp_dir: Path) -> dict:
    """Show that the project schema/Schematron rejects a one-line couplet."""

    document = etree.parse(str(SOURCE_TEI))
    couplet = document.xpath("//tei:lg[@type='couplet'][1]", namespaces=NS)[0]
    lines = couplet.xpath("./tei:l", namespaces=NS)
    couplet.remove(lines[1])
    broken = temp_dir / "missing-second-hemistich.xml"
    write_document(document, broken)
    result = project_validation.validate(broken, offline=True)
    detected = (
        not result["checks"]["project_odd_relaxng_valid"]
        or not result["checks"]["project_schematron_valid"]
    )
    return {
        "experiment": "remove_second_hemistich",
        "mutation": "Removed mt.bnf348.0001.b from the first couplet.",
        "expected_detector": "project ODD schema and/or Schematron",
        "detected": detected,
        "checks": result["checks"],
    }


def break_facs_reference(temp_dir: Path) -> dict:
    """Show that conversion stops when a TEI line points to no zone."""

    document = etree.parse(str(SOURCE_TEI))
    line = document.xpath("//tei:lg[@type='couplet']/tei:l[1]", namespaces=NS)[0]
    line.set("facs", "#zone-that-does-not-exist")
    broken = temp_dir / "broken-facs-reference.xml"
    write_document(document, broken)
    message = ""
    try:
        build_annotation_pages(broken, "https://example.invalid/learning")
        detected = False
    except ValueError as exc:
        detected = "Missing zone" in str(exc)
        message = str(exc)
    return {
        "experiment": "break_facs_reference",
        "mutation": "Changed the first line's @facs to a nonexistent zone.",
        "expected_detector": "TEI-to-IIIF converter",
        "detected": detected,
        "message": message,
    }


def alter_annotation_text(temp_dir: Path) -> dict:
    """Show that the TEI-IIIF cross-check rejects altered derived text."""

    annotation_dir = temp_dir / "iiif"
    annotation_dir.mkdir()
    pages = build_annotation_pages(SOURCE_TEI, "https://example.invalid/learning")
    first_filename = sorted(pages)[0]
    for filename, page in pages.items():
        (annotation_dir / filename).write_text(
            json.dumps(page, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    altered_path = annotation_dir / first_filename
    altered = json.loads(altered_path.read_text(encoding="utf-8"))
    altered_line_id = altered["items"][0]["id"].rsplit("#", 1)[-1]
    altered["items"][0]["body"]["value"] = "意図的に変更した学習用本文"
    altered_path.write_text(
        json.dumps(altered, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    result = validate_annotations(SOURCE_TEI, annotation_dir)
    detected = any("Diplomatic text mismatch" in error for error in result["errors"])
    return {
        "experiment": "alter_annotation_text",
        "mutation": f"Changed the IIIF body for {altered_line_id} without changing TEI.",
        "expected_detector": "TEI-IIIF cross-check",
        "detected": detected,
        "relevant_check": result["checks"]["diplomatic_text_matches_tei"],
        "errors": [
            error for error in result["errors"] if "text mismatch" in error
        ],
    }


def main() -> int:
    WORK.mkdir(parents=True, exist_ok=True)
    if not project_validation.RNG_FILE.exists():
        raise RuntimeError(
            "The cached TEI schema is missing. Run python scripts/verify_all.py once first."
        )
    with tempfile.TemporaryDirectory(prefix="learning-review-", dir=WORK) as directory:
        temp_dir = Path(directory)
        experiments = [
            remove_second_hemistich(temp_dir),
            break_facs_reference(temp_dir),
            alter_annotation_text(temp_dir),
        ]
    report = {
        "purpose": "Safe negative tests for researcher code review",
        "authoritative_files_modified": False,
        "all_expected_failures_detected": all(item["detected"] for item in experiments),
        "experiments": experiments,
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["all_expected_failures_detected"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
