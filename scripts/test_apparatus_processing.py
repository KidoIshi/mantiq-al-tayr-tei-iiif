#!/usr/bin/env python3
"""Check witness-specific text extraction from the implemented apparatus."""

from pathlib import Path
import argparse

from lxml import etree

from tei_to_iiif_annotations import NS, diplomatic_text


ROOT = Path(__file__).resolve().parents[1]
TEI = ROOT / "data" / "tei" / "bnf-persan-348-f6-sample.xml"


def check_apparatus(tei_path: Path) -> dict[str, str]:
    document = etree.parse(str(tei_path))
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
    fsc_reading = line.xpath(".//tei:rdg[@wit='#wit-fsc28']", namespaces=NS)[0]
    correspondence = fsc_reading.get("corresp", "")
    linked = document.xpath(
        f"//*[@xml:id='{correspondence.removeprefix('#')}']",
        namespaces=NS,
    )
    if len(linked) != 1:
        raise RuntimeError("FSC-MS-28 apparatus reading does not resolve to one independent transcription segment")
    if " ".join(fsc_reading.itertext()).split() != " ".join(linked[0].itertext()).split():
        raise RuntimeError("FSC-MS-28 apparatus reading differs from its linked independent transcription segment")
    fsc_lines = document.xpath(
        "//tei:div[@source='#wit-fsc28']/tei:lg[@type='couplet']/tei:l",
        namespaces=NS,
    )
    if len(fsc_lines) != 18:
        raise RuntimeError(f"Expected 18 independently transcribed FSC-MS-28 lines, found {len(fsc_lines)}")
    bnf_lines = {
        item.get("{http://www.w3.org/XML/1998/namespace}id").removeprefix("mt.bnf348."): item
        for item in document.xpath(
            "//tei:div[@source='#wit-bnf348']/tei:lg[@type='couplet']/tei:l",
            namespaces=NS,
        )
    }
    independent_lines = {
        item.get("{http://www.w3.org/XML/1998/namespace}id").removeprefix("mt.fsc28."): item
        for item in fsc_lines
    }
    apparatus_ids = sorted(
        item.get("{http://www.w3.org/XML/1998/namespace}id").removeprefix("mt.bnf348.")
        for item in document.xpath(
            "//tei:div[@source='#wit-bnf348']/tei:lg[@type='couplet']/tei:l"
            "[.//tei:app/*[self::tei:lem or self::tei:rdg][contains(concat(' ', normalize-space(@wit), ' '), ' #wit-fsc28 ')]]",
            namespaces=NS,
        )
    )
    if not apparatus_ids:
        raise RuntimeError("No Persan 348 lines contain an FSC-MS-28 apparatus reading")
    missing_independent = sorted(set(apparatus_ids) - independent_lines.keys())
    if missing_independent:
        raise RuntimeError(f"Apparatus lines lack independent FSC-MS-28 transcriptions: {missing_independent}")
    for shared_id in apparatus_ids:
        apparatus_text = diplomatic_text(bnf_lines[shared_id], "#wit-fsc28")
        independent_text = diplomatic_text(independent_lines[shared_id], "#wit-fsc28")
        if apparatus_text != independent_text:
            raise RuntimeError(
                f"Whole FSC-MS-28 {shared_id} differs between apparatus extraction "
                f"({apparatus_text!r}) and independent transcription ({independent_text!r})"
            )
    covered = document.xpath(
        "//tei:l[@xml:id='mt.fsc28.0006.a']",
        namespaces=NS,
    )
    if len(covered) != 1 or diplomatic_text(covered[0]) != "کرد […] پدید":
        raise RuntimeError("FSC-MS-28 0006a covered text was not preserved as a gap")
    return actual


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tei", type=Path, default=TEI)
    args = parser.parse_args()
    tei_path = args.tei if args.tei.is_absolute() else ROOT / args.tei
    actual = check_apparatus(tei_path)
    print(actual)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
