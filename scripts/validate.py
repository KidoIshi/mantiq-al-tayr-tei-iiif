#!/usr/bin/env python3
"""Validate the sample as XML, TEI P5 Relax NG, and project Schematron."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from lxml import etree
from lxml import isoschematron


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEI_FILE = ROOT / "data" / "tei" / "mantiq-sample.xml"
SCH_FILE = ROOT / "schema" / "mantiq.sch"
CACHE_DIR = ROOT / "work" / "schema-cache"
RNG_FILE = CACHE_DIR / "tei_all.rng"
DEFAULT_REPORT_FILE = ROOT / "outputs" / "validation-report.json"
RNG_URL = "https://www.tei-c.org/release/xml/tei/custom/schema/relaxng/tei_all.rng"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def get_schema(offline: bool) -> None:
    if RNG_FILE.exists():
        return
    if offline:
        raise RuntimeError(f"Offline mode: cached schema is missing: {RNG_FILE}")
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(RNG_URL, headers={"User-Agent": "tei-iiif-poc/0.1"})
    with urllib.request.urlopen(request, timeout=60) as response:
        RNG_FILE.write_bytes(response.read())


def validate(tei_file: Path, offline: bool) -> dict:
    parser = etree.XMLParser(resolve_entities=False, no_network=True)
    document = etree.parse(str(tei_file), parser)
    get_schema(offline)

    rng_document = etree.parse(str(RNG_FILE), parser)
    relaxng = etree.RelaxNG(rng_document)
    rng_ok = relaxng.validate(document)

    sch_document = etree.parse(str(SCH_FILE), parser)
    schematron = isoschematron.Schematron(sch_document, store_report=True)
    sch_ok = schematron.validate(document)

    ns = {"tei": "http://www.tei-c.org/ns/1.0"}
    counts = {
        "couplets": int(document.xpath("count(//tei:lg[@type='couplet'])", namespaces=ns)),
        "hemistichs": int(document.xpath("count(//tei:lg[@type='couplet']/tei:l)", namespaces=ns)),
        "apparatus_entries": int(document.xpath("count(//tei:app)", namespaces=ns)),
        "facs_links": int(document.xpath("count(//*[@facs])", namespaces=ns)),
    }

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "tei_file": str(tei_file.relative_to(ROOT)),
        "tei_sha256": sha256(tei_file),
        "schema": {"url": RNG_URL, "cache": str(RNG_FILE.relative_to(ROOT)), "sha256": sha256(RNG_FILE)},
        "checks": {
            "xml_well_formed": True,
            "tei_relaxng_valid": rng_ok,
            "project_schematron_valid": sch_ok,
        },
        "counts": counts,
        "relaxng_errors": [str(item) for item in relaxng.error_log],
        "schematron_report": etree.tostring(
            schematron.validation_report, encoding="unicode", pretty_print=True
        ) if schematron.validation_report is not None else None,
    }


def main() -> int:
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--offline", action="store_true")
    arg_parser.add_argument("--tei", type=Path, default=DEFAULT_TEI_FILE)
    arg_parser.add_argument("--report", type=Path, default=DEFAULT_REPORT_FILE)
    args = arg_parser.parse_args()
    tei_file = args.tei if args.tei.is_absolute() else ROOT / args.tei
    report_file = args.report if args.report.is_absolute() else ROOT / args.report
    report_file.parent.mkdir(parents=True, exist_ok=True)
    try:
        report = validate(tei_file, args.offline)
        ok = all(report["checks"].values())
    except Exception as exc:
        report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "checks": {"completed": False},
            "fatal_error": f"{type(exc).__name__}: {exc}",
        }
        ok = False
    report_file.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
