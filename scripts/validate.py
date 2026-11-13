#!/usr/bin/env python3
"""Validate the sample as XML, TEI P5 Relax NG, and project Schematron."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from lxml import etree
from lxml import isoschematron

from rng_tools import validate_with_jing


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEI_FILE = ROOT / "data" / "tei" / "bnf-persan-348-f6-sample.xml"
SCH_FILE = ROOT / "schema" / "mantiq.sch"
CACHE_DIR = ROOT / "work" / "schema-cache"
RNG_FILE = CACHE_DIR / "tei_all.rng"
PROJECT_RNG_FILE = ROOT / "schema" / "mantiq.rng"
DEFAULT_REPORT_FILE = ROOT / "outputs" / "validation-report-bnf348-f6.json"
TEI_VERSION = "4.12.0"
RNG_URL = (
    f"https://www.tei-c.org/Vault/P5/{TEI_VERSION}/xml/tei/custom/schema/relaxng/tei_all.rng"
)
RNG_SHA256 = "b0f115095ead2ccc6933aa3365c6f4a82cba3b2ec7eee7f76bb616d7a63b7e48"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def get_schema(offline: bool) -> None:
    if RNG_FILE.exists() and sha256(RNG_FILE) == RNG_SHA256:
        return
    if offline:
        state = "missing" if not RNG_FILE.exists() else "present but has the wrong SHA-256"
        raise RuntimeError(f"Offline mode: cached schema is {state}: {RNG_FILE}")
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(RNG_URL, headers={"User-Agent": "tei-iiif-poc/0.1"})
    with urllib.request.urlopen(request, timeout=60) as response:
        schema_bytes = response.read()
    downloaded_sha256 = hashlib.sha256(schema_bytes).hexdigest()
    if downloaded_sha256 != RNG_SHA256:
        raise RuntimeError(
            "Downloaded TEI schema checksum mismatch: "
            f"expected {RNG_SHA256}, received {downloaded_sha256}"
        )
    with tempfile.NamedTemporaryFile(dir=CACHE_DIR, delete=False) as temporary:
        temporary.write(schema_bytes)
        temporary_path = Path(temporary.name)
    temporary_path.replace(RNG_FILE)


def validate(tei_file: Path, offline: bool) -> dict:
    parser = etree.XMLParser(resolve_entities=False, no_network=True)
    document = etree.parse(str(tei_file), parser)
    get_schema(offline)

    rng_document = etree.parse(str(RNG_FILE), parser)
    relaxng = etree.RelaxNG(rng_document)
    rng_ok = relaxng.validate(document)

    if not PROJECT_RNG_FILE.exists():
        raise RuntimeError("Project ODD schema is missing; run scripts/build_odd_schema.py")
    project_rng_ok, project_rng_errors = validate_with_jing(tei_file, PROJECT_RNG_FILE)

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
        "schema": {
            "tei_all": {
                "tei_version": TEI_VERSION,
                "url": RNG_URL,
                "cache": str(RNG_FILE.relative_to(ROOT)),
                "sha256": sha256(RNG_FILE),
                "expected_sha256": RNG_SHA256,
            },
            "project_odd": {"path": str(PROJECT_RNG_FILE.relative_to(ROOT)), "sha256": sha256(PROJECT_RNG_FILE)},
        },
        "checks": {
            "xml_well_formed": True,
            "tei_all_relaxng_valid": rng_ok,
            "project_odd_relaxng_valid": project_rng_ok,
            "project_schematron_valid": sch_ok,
        },
        "counts": counts,
        "relaxng_errors": [str(item) for item in relaxng.error_log],
        "project_odd_relaxng_errors": project_rng_errors,
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
    report_file.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
