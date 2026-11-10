#!/usr/bin/env python3
"""Prove that the project ODD schema rejects a TEI module not selected by the project."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from lxml import etree


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from rng_tools import validate_with_jing  # noqa: E402
from validate import RNG_FILE, get_schema  # noqa: E402


TEI_NS = "http://www.tei-c.org/ns/1.0"
SOURCE = ROOT / "data" / "tei" / "bnf-persan-348-f6-sample.xml"
PROJECT_RNG = ROOT / "schema" / "mantiq.rng"
FIXTURE = ROOT / "work" / "odd-negative-test.xml"
REPORT = ROOT / "outputs" / "odd-negative-test-report.json"


def main() -> int:
    parser = etree.XMLParser(resolve_entities=False, no_network=True)
    document = etree.parse(str(SOURCE), parser)
    body = document.find(f".//{{{TEI_NS}}}body")
    if body is None:
        raise RuntimeError("TEI body not found")

    figure = etree.Element(f"{{{TEI_NS}}}figure")
    description = etree.SubElement(figure, f"{{{TEI_NS}}}figDesc")
    description.text = "Negative test: figures module is intentionally absent from the project ODD."
    body.insert(0, figure)
    FIXTURE.parent.mkdir(parents=True, exist_ok=True)
    document.write(str(FIXTURE), encoding="utf-8", xml_declaration=True, pretty_print=True)

    get_schema(offline=False)
    official = etree.RelaxNG(etree.parse(str(RNG_FILE), parser))
    official_accepts = official.validate(document)
    project_accepts, project_messages = validate_with_jing(FIXTURE, PROJECT_RNG)
    project_messages = [
        message.replace(str(ROOT) + "\\", "").replace(str(ROOT) + "/", "")
        for message in project_messages
    ]
    passed = official_accepts and not project_accepts

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "test": "Element from excluded figures module",
        "injected_element": "figure/figDesc",
        "official_tei_all_accepts": official_accepts,
        "project_odd_schema_accepts": project_accepts,
        "expected": "Official TEI All accepts; project ODD schema rejects.",
        "passed": passed,
        "project_validator_messages": project_messages,
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
