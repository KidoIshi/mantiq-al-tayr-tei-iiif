#!/usr/bin/env python3
"""Static regression checks for the witness-switching comparison viewer."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VIEWER = ROOT / "viewer" / "index.html"
OUTPUT = ROOT / "outputs" / "viewer-comparison-test.json"


def main() -> int:
    html = VIEWER.read_text(encoding="utf-8")
    requirements = {
        "three_witness_modes": all(
            f'data-witness-mode="{mode}"' in html
            for mode in ("bnf348", "fsc28", "parallel")
        ),
        "tei_driven_witness_groups": "witnessGroups = { bnf348: [], fsc28: [] }" in html,
        "witness_specific_apparatus_resolution": "witnessPointers[witnessKey]" in html,
        "unclear_rendering": "unclear-glyph" in html and "appendUncertaintyNote" in html,
        "gap_rendering": "gap-marker" in html and "［…］" in html,
        "paired_region_display": "showComparisonRegions" in html and "region-secondary-image" in html,
        "out_of_range_parallel_selection_guard": "return group ? directChildren(group, 'l')" in html,
        "two_mirador_manifests": all(uri in html for uri in (
            "https://gallica.bnf.fr/iiif/ark:/12148/btv1b10091505x/manifest.json",
            "https://ids.si.edu/ids/manifest/FS-7342_15",
        )),
        "variant_and_gap_labels": "本文異同" in html and "補修による欠損" in html,
        "mirador_subresource_integrity": "integrity=\"sha384-" in html and "crossorigin=\"anonymous\"" in html,
        "tei_driven_display_counts": "const bnfCouplets = witnessGroups.bnf348.length" in html,
    }
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "viewer": str(VIEWER.relative_to(ROOT)),
        "all_passed": all(requirements.values()),
        "checks": requirements,
        "manual_browser_check_record": {
            "performed_by_this_script": False,
            "record_type": "Prior human observation retained as provenance; not rerun by this static test.",
            "date": "2026-11-11",
            "modes_checked": ["bnf348", "fsc28", "parallel"],
            "observed": [
                "FSC-MS-28 renders 9 couplets and 18 hemistichs",
                "0004b renders the unclear dal and textual-variant label",
                "0006a renders the covered gap marker",
                "parallel selection renders two IIIF regions",
                "Mirador loads both witness manifests",
            ],
        },
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
