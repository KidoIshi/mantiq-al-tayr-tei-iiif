#!/usr/bin/env python3
"""Run all reproducible project checks and write a compact summary."""

from __future__ import annotations

import json
import subprocess
import sys
import platform
import re
from datetime import datetime, timezone
from pathlib import Path

from rng_tools import find_java


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


def parse_java_version(output: str) -> str | None:
    """Extract the actual version line, ignoring JAVA_TOOL_OPTIONS notices."""

    lines = output.splitlines()
    return next(
        (line.strip() for line in lines if re.search(r"^(?:openjdk|java) version ", line, re.IGNORECASE)),
        None,
    )


def detected_java_version() -> str | None:
    """Return Java's version without making the aggregate report itself fragile."""

    try:
        java = find_java()
    except RuntimeError:
        return None
    completed = subprocess.run(
        [str(java), "-version"], cwd=ROOT, text=True, encoding="utf-8",
        capture_output=True, check=False,
    )
    if completed.returncode != 0:
        return None
    return parse_java_version(completed.stderr + "\n" + completed.stdout)


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
        run(
            "validate_fsc28_opening_review_candidates",
            [python, "scripts/validate_fsc28_review_candidates.py"],
        ),
        run(
            "collate_approved_opening_witnesses",
            [python, "scripts/collate_opening_witnesses.py"],
        ),
        run(
            "static_check_witness_comparison_viewer",
            [python, "scripts/test_viewer_comparison.py"],
        ),
        run("generate_iiif_annotation_page", [python, "scripts/tei_to_iiif_annotations.py"]),
        run("validate_tei_xml_rng_schematron", validation_command),
        run(
            "crosscheck_tei_and_iiif_annotations",
            [python, "scripts/validate_iiif_annotations.py"],
        ),
    ]
    git_commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, encoding="utf-8",
        capture_output=True, check=False,
    )
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project": "Manṭiq al-ṭayr TEI–IIIF prototype",
        "environment": {
            "git_commit": git_commit.stdout.strip() if git_commit.returncode == 0 else None,
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "java": detected_java_version(),
        },
        "all_passed": all(step["passed"] for step in steps),
        "steps": steps,
        "evidence": {
            "odd_build": "outputs/odd-build-report.json",
            "odd_negative_test": "outputs/odd-negative-test-report.json",
            "tei_validation": "outputs/validation-report-bnf348-f6.json",
            "iiif_annotation_validation": "outputs/iiif-annotation-validation.json",
            "fsc28_candidate_validation": "outputs/fsc-ms-28-candidate-validation.json",
            "opening_witness_collation": "outputs/opening-witness-collation.json",
            "viewer_comparison_test": "outputs/viewer-comparison-test.json",
        },
    }
    OUTPUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
