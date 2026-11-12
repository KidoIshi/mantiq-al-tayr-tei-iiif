#!/usr/bin/env python3
"""Collate the approved opening transcriptions of Persan 348 and FSC-MS-28.

The comparison is diplomatic: ``choice/orig`` is selected, witness-specific
``app/rdg`` readings are selected, and gaps/unclear characters remain explicit.
The script also checks that genuine textual variation is represented by a TEI
apparatus while a covered passage is not silently treated as a variant reading.
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
TEI = ROOT / "data" / "tei" / "bnf-persan-348-f6-sample.xml"
JSON_OUTPUT = ROOT / "outputs" / "opening-witness-collation.json"
MD_OUTPUT = ROOT / "outputs" / "opening-witness-collation-ja.md"

TEI_NS = "http://www.tei-c.org/ns/1.0"
XML_NS = "http://www.w3.org/XML/1998/namespace"
NS = {"tei": TEI_NS}
XML_ID = f"{{{XML_NS}}}id"

WITNESSES = {
    "bnf348": {"pointer": "#wit-bnf348", "label": "BnF Persan 348"},
    "fsc28": {"pointer": "#wit-fsc28", "label": "Smithsonian FSC-MS-28"},
}


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def collapse_space(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def render_inner(element: ET.Element, witness: str) -> tuple[str, set[str]]:
    """Render an element without its tail for one witness."""
    name = local_name(element.tag)
    flags: set[str] = set()

    if name == "gap":
        return " […] ", {"gap", f"gap:{element.get('reason', 'unknown')}"}

    if name == "choice":
        selected = element.find("tei:orig", NS)
        if selected is None:
            selected = next(iter(element), None)
        if selected is None:
            return "", flags
        return render_inner(selected, witness)

    if name == "app":
        pointer = WITNESSES[witness]["pointer"]
        selected = None
        for reading in element.findall("tei:rdg", NS):
            if pointer in reading.get("wit", "").split():
                selected = reading
                break
        if selected is None:
            raise ValueError(f"No reading for {pointer} in apparatus")
        text, child_flags = render_inner(selected, witness)
        return text, child_flags | {"apparatus"}

    if name == "unclear":
        flags.add("unclear")

    pieces = [element.text or ""]
    for child in element:
        child_text, child_flags = render_inner(child, witness)
        pieces.append(child_text)
        pieces.append(child.tail or "")
        flags.update(child_flags)
    return "".join(pieces), flags


def extract_lines(root: ET.Element, witness: str) -> dict[str, dict]:
    pointer = WITNESSES[witness]["pointer"]
    div = root.find(f".//tei:div[@source='{pointer}']", NS)
    if div is None:
        raise ValueError(f"No transcription div for {pointer}")

    records: dict[str, dict] = {}
    for group in div.findall("tei:lg[@type='couplet']", NS):
        couplet = group.get("n", "")
        if not ("0001" <= couplet <= "0009"):
            continue
        for line in group.findall("tei:l", NS):
            part = line.get("n", "")
            key = f"{couplet}{part}"
            raw, flags = render_inner(line, witness)
            records[key] = {
                "id": line.get(XML_ID),
                "text": collapse_space(raw),
                "flags": sorted(flags),
                "facs": line.get("facs"),
                "has_app": line.find(".//tei:app", NS) is not None,
            }
    return records


def zone_links(root: ET.Element) -> dict[str, str]:
    links: dict[str, str] = {}
    for surface in root.findall(".//tei:surface", NS):
        graphic = surface.find("tei:graphic", NS)
        if graphic is None or not graphic.get("url"):
            continue
        graphic_url = graphic.get("url", "")
        base = graphic_url.split("/full/full/", 1)[0]
        suffix = "default.jpg" if "ids.si.edu" in graphic_url else "native.jpg"
        for zone in surface.findall("tei:zone", NS):
            zone_id = zone.get(XML_ID)
            if not zone_id:
                continue
            x = int(zone.get("ulx", "0"))
            y = int(zone.get("uly", "0"))
            width = int(zone.get("lrx", "0")) - x
            height = int(zone.get("lry", "0")) - y
            links[f"#{zone_id}"] = f"{base}/{x},{y},{width},{height}/full/0/{suffix}"
    return links


def classify(bnf: dict, fsc: dict) -> tuple[str, str, bool]:
    fsc_flags = set(fsc["flags"])
    if "gap:covered" in fsc_flags:
        return (
            "covered_gap",
            "FSC-MS-28の中央部は補修紙で覆われるため、異読ではなく欠損として扱う。",
            False,
        )
    if bnf["text"] == fsc["text"]:
        return "exact_match", "外交的転写が一致する。", False
    if bnf["text"].replace(" ", "") == fsc["text"].replace(" ", ""):
        return "orthographic_difference", "分かち書きだけが異なる。", False
    if "unclear" in fsc_flags:
        return (
            "textual_variant_with_uncertainty",
            "本文異同を記録する。FSC-MS-28の別の字母判読不確実性はunclearとして保持する。",
            True,
        )
    return "textual_variant", "独立証人間の本文異同として記録する。", True


def make_report(records: list[dict], counts: Counter, checks: dict) -> str:
    labels = {
        "exact_match": "完全一致",
        "orthographic_difference": "表記差",
        "textual_variant": "本文異同",
        "textual_variant_with_uncertainty": "本文異同＋判読不確実",
        "covered_gap": "補修による欠損",
    }
    rows = []
    for item in records:
        bnf = item["witnesses"]["bnf348"]
        fsc = item["witnesses"]["fsc28"]
        bnf_text = bnf["text"].replace("|", "\\|")
        fsc_text = fsc["text"].replace("|", "\\|")
        rows.append(
            f"| {item['key']} | {bnf_text} | {fsc_text} | "
            f"{labels[item['classification']]} | "
            f"[BnF]({bnf['image']})・[FSC]({fsc['image']}) |"
        )

    return f"""# Persan 348・FSC-MS-28冒頭9対句 校合報告

生成日：{datetime.now(timezone.utc).date().isoformat()}
状態：研究者承認済みの独立転写18半句を機械校合し、TEI校異装置との対応を検証済み

## 結果概要

- 対象：9対句・18半句
- 完全一致：{counts['exact_match']}半句
- 表記差：{counts['orthographic_difference']}半句
- 本文異同：{counts['textual_variant'] + counts['textual_variant_with_uncertainty']}半句
- 補修による欠損：{counts['covered_gap']}半句
- 校異装置対応検査：{'合格' if all(checks.values()) else '不合格'}

## 校合表

| 半句 | Persan 348 | FSC-MS-28 | 分類 | 画像 |
|---|---|---|---|---|
{chr(10).join(rows)}

## 分類規則

1. 比較対象は正規化形ではなく外交的転写とする。`<choice>`では`<orig>`を採る。
2. `<app>`を含む箇所は、比較する証人の`<rdg wit="…">`だけを抽出する。
3. 文字列が同じなら完全一致、空白だけが違う場合は表記差とする。
4. 独立して読める語形が異なる場合だけ本文異同とし、非選択的な`<app><rdg>`で記録する。
5. `<unclear>`は「採用した読みの視認性」、`<gap>`は「読める本文が存在しない範囲」を表す。どちらもそれ自体を別の読みとは数えない。
6. 他証人から欠損を補ってFSC-MS-28の転写として表示しない。

## 今回の編集判断

- 0004b：Persan 348の`وین`とFSC-MS-28の`وان`を本文異同として扱う。優先本文は選ばず、二つの`<rdg>`を並列に保持する。
- 0004bのFSC-MS-28側`دگر`：語の読みは保持するが、`د`だけを`<unclear>`とする。これは`وین/وان`とは別種の情報である。
- 0006a：FSC-MS-28の中央部は補修紙で覆われるため`<gap reason="covered"/>`とする。Persan 348の語句をFSC-MS-28の異読として登録しない。
- 残る16半句：外交的転写が一致するため、冗長な`<app>`を作らない。

## 技術的に学ぶ点

校合は「文字列が違えばすべて`<app>`」ではない。写本に何が見えるか、表記上の差か、欠損か、判読の確度か、独立した本文異同かを分離してからTEI要素を選ぶ。AIは抽出・比較・整合性検査を反復できるが、差を本文異同として採用する判断と、将来`<lem>`を選ぶ本文批判は研究者が担う。
"""


def main() -> int:
    root = ET.parse(TEI).getroot()
    links = zone_links(root)
    bnf_lines = extract_lines(root, "bnf348")
    fsc_lines = extract_lines(root, "fsc28")

    errors: list[str] = []
    if set(bnf_lines) != set(fsc_lines):
        errors.append("The witness line sets do not match")
    if len(bnf_lines) != 18:
        errors.append(f"Expected 18 aligned lines, found {len(bnf_lines)}")

    records: list[dict] = []
    for key in sorted(set(bnf_lines) & set(fsc_lines)):
        bnf = bnf_lines[key]
        fsc = fsc_lines[key]
        classification, explanation, apparatus_required = classify(bnf, fsc)
        if apparatus_required and not bnf["has_app"]:
            errors.append(f"{key}: textual variant has no TEI apparatus")
        if not apparatus_required and bnf["has_app"]:
            errors.append(f"{key}: TEI apparatus exists but classification does not require one")
        for record in (bnf, fsc):
            record["image"] = links.get(record["facs"], "")
            if not record["image"]:
                errors.append(f"{key}: no image region for {record['facs']}")
        records.append(
            {
                "key": key,
                "classification": classification,
                "explanation": explanation,
                "apparatus_required": apparatus_required,
                "witnesses": {"bnf348": bnf, "fsc28": fsc},
            }
        )

    counts = Counter(record["classification"] for record in records)
    expected = {
        "exact_match": 16,
        "textual_variant_with_uncertainty": 1,
        "covered_gap": 1,
    }
    for label, expected_count in expected.items():
        if counts[label] != expected_count:
            errors.append(f"Expected {expected_count} {label}, found {counts[label]}")

    checks = {
        "line_sets_match": set(bnf_lines) == set(fsc_lines),
        "eighteen_lines_compared": len(records) == 18,
        "apparatus_matches_textual_variants": not any("apparatus" in error for error in errors),
        "all_lines_have_image_regions": not any("image region" in error for error in errors),
        "expected_classification_counts": not any(error.startswith("Expected") for error in errors),
    }
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_tei": str(TEI.relative_to(ROOT)),
        "method": "diplomatic witness-specific collation",
        "counts": dict(sorted(counts.items())),
        "checks": checks,
        "records": records,
        "errors": errors,
    }
    JSON_OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MD_OUTPUT.write_text(make_report(records, counts, checks), encoding="utf-8")
    print(json.dumps({"counts": payload["counts"], "checks": checks, "errors": errors}, ensure_ascii=False, indent=2))
    return 0 if not errors and all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
