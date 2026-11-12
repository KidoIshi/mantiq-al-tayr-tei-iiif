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
    unclear = line.xpath(
        ".//tei:rdg[@wit='#wit-fsc28']/tei:unclear",
        namespaces=NS,
    )
    if len(unclear) != 1 or unclear[0].text != "د":
        raise RuntimeError("Expected only FSC-MS-28 د to be encoded as unclear")
    if unclear[0].get("reason") != "indistinct" or unclear[0].get("cert") != "low":
        raise RuntimeError("Unexpected uncertainty metadata for FSC-MS-28 د")
    unclear_id = unclear[0].get("{http://www.w3.org/XML/1998/namespace}id")
    notes = document.xpath(
        f"//tei:note[@type='palaeographic'][@target='#{unclear_id}']",
        namespaces=NS,
    )
    if len(notes) != 1:
        raise RuntimeError("Expected one targeted palaeographical note for FSC-MS-28 د")
    fsc_lines = document.xpath(
        "//tei:div[@source='#wit-fsc28']/tei:lg[@type='couplet']/tei:l",
        namespaces=NS,
    )
    if len(fsc_lines) != 18:
        raise RuntimeError(f"Expected 18 independently transcribed FSC-MS-28 lines, found {len(fsc_lines)}")
    covered = document.xpath(
        "//tei:l[@xml:id='mt.fsc28.0006.a']",
        namespaces=NS,
    )
    if len(covered) != 1 or diplomatic_text(covered[0]) != "کرد […] پدید":
        raise RuntimeError("FSC-MS-28 0006a covered text was not preserved as a gap")
    print(actual)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
