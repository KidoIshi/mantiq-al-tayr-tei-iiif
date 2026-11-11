#!/usr/bin/env python3
"""Check witness-specific text extraction from the implemented apparatus."""

from pathlib import Path

from lxml import etree

from tei_to_iiif_annotations import NS, diplomatic_text


ROOT = Path(__file__).resolve().parents[1]
TEI = ROOT / "data" / "tei" / "bnf-persan-348-f6-sample.xml"


def main() -> int:
    document = etree.parse(str(TEI))
    lines = document.xpath("//tei:l[@xml:id='mt.bnf348.0004.b']", namespaces=NS)
    if len(lines) != 1:
        raise RuntimeError(f"Expected one mt.bnf348.0004.b, found {len(lines)}")
    line = lines[0]
    expected = {
        "#wit-bnf348": "وین دگر را دایما آرام داد",
        "#wit-fsc28": "وان دگر را دایما آرام داد",
    }
    actual = {witness: diplomatic_text(line, witness) for witness in expected}
    if actual != expected:
        raise RuntimeError(f"Witness extraction mismatch: {actual!r}")
    print(actual)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
