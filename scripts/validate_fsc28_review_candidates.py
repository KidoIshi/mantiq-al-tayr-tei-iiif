#!/usr/bin/env python3
"""Validate FSC-MS-28 opening transcription candidates against TEI zones."""

from __future__ import annotations

import json
from pathlib import Path

from lxml import etree


ROOT = Path(__file__).resolve().parents[1]
TEI = ROOT / "data" / "tei" / "bnf-persan-348-f6-sample.xml"
CANDIDATES = ROOT / "data" / "review" / "fsc-ms-28-opening-candidates.json"
REPORT = ROOT / "outputs" / "fsc-ms-28-candidate-validation.json"
NS = {"tei": "http://www.tei-c.org/ns/1.0"}
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"


def main() -> int:
    document = etree.parse(str(TEI))
    data = json.loads(CANDIDATES.read_text(encoding="utf-8"))
    expected_ids = [f"{number:04d}{side}" for number in range(1, 10) for side in ("a", "b")]
    records = data.get("lines", [])
    actual_ids = [record.get("id") for record in records]
    errors: list[str] = []

    if actual_ids != expected_ids:
        errors.append(f"Candidate order or IDs differ: {actual_ids!r}")

    zone_ids = {
        zone.get(XML_ID)
        for zone in document.xpath(
            "//tei:surface[@xml:id='fsc28.fs7342-15']/tei:zone",
            namespaces=NS,
        )
    }
    for record in records:
        zone = (record.get("zone") or "").removeprefix("#")
        if zone not in zone_ids:
            errors.append(f"{record.get('id')}: missing TEI zone {zone!r}")
        if not record.get("candidate"):
            errors.append(f"{record.get('id')}: empty candidate")
        if not record.get("status"):
            errors.append(f"{record.get('id')}: missing status")

    gaps = [record for record in records if record.get("status") == "researcher-reviewed-gap-covered"]
    if len(gaps) != 1 or gaps[0].get("id") != "0006a" or "[…]" not in gaps[0].get("candidate", ""):
        errors.append("0006a must be the single covered-gap candidate")

    reviewed = [record for record in records if str(record.get("status", "")).startswith("researcher-reviewed")]
    if len(reviewed) != 18:
        errors.append(f"All 18 candidates must be researcher reviewed, found {len(reviewed)}")

    report = {
        "candidate_file": str(CANDIDATES.relative_to(ROOT)),
        "tei_file": str(TEI.relative_to(ROOT)),
        "candidate_count": len(records),
        "zone_count": len(zone_ids),
        "covered_gap": "0006a",
        "researcher_reviewed": expected_ids,
        "passed": not errors,
        "errors": errors,
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
