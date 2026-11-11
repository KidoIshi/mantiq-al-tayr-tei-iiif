#!/usr/bin/env python3
"""Run all reproducible project checks and write a compact summary."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs" / "project-verification-summary.json"


def run(label: str, command: list[str]) -> dict:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )
    return {
        "label": label,
        "command": ["python", *command[1:]],
        "passed": completed.returncode == 0,
        "returncode": completed.returncode,
        "stderr": completed.stderr.strip(),
    }


def main() -> int:
    python = sys.executable
    validation_command = [
        python,
        "scripts/validate.py",
        "--tei",
        "data/tei/bnf-persan-348-f6-sample.xml",
        "--report",
        "outputs/validation-report-bnf348-f6.json",
    ]
    if (ROOT / "work" / "schema-cache" / "tei_all.rng").exists():
        validation_command.insert(2, "--offline")
    steps = [
        run("build_project_schema_from_odd", [python, "scripts/build_odd_schema.py"]),
        run("test_project_odd_excludes_unselected_module", [python, "scripts/test_odd_schema.py"]),
        run("test_witness_specific_apparatus_processing", [python, "scripts/test_apparatus_processing.py"]),
        run("generate_iiif_annotation_page", [python, "scripts/tei_to_iiif_annotations.py"]),
        run("validate_tei_xml_rng_schematron", validation_command),
        run(
            "crosscheck_tei_and_iiif_annotations",
            [python, "scripts/validate_iiif_annotations.py"],
        ),
    ]
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project": "Manṭiq al-ṭayr TEI–IIIF prototype",
        "all_passed": all(step["passed"] for step in steps),
        "steps": steps,
        "evidence": {
            "odd_build": "outputs/odd-build-report.json",
            "odd_negative_test": "outputs/odd-negative-test-report.json",
            "tei_validation": "outputs/validation-report-bnf348-f6.json",
            "iiif_annotation_validation": "outputs/iiif-annotation-validation.json",
        },
    }
    OUTPUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
