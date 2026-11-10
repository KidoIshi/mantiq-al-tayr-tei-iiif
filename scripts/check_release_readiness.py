#!/usr/bin/env python3
"""Report concrete blockers before creating a public release."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from lxml import etree


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs" / "publication-readiness.json"
TEI = ROOT / "data" / "tei" / "bnf-persan-348-f6-sample.xml"
ANNOTATIONS = ROOT / "iiif" / "bnf-persan-348-f6-annotations.json"
VERIFY = ROOT / "outputs" / "project-verification-summary.json"
NS = {"tei": "http://www.tei-c.org/ns/1.0"}


def main() -> int:
    blockers: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    for filename, reason in (
        ("LICENSE", "Project data/code license has not been selected."),
        ("CITATION.cff", "Public author and citation metadata have not been supplied."),
        ("schema/mantiq.odd", "Project ODD customization is missing."),
        ("schema/mantiq.rng", "ODD-generated project schema is missing."),
        ("outputs/odd-build-report.json", "ODD build evidence is missing."),
        ("outputs/odd-negative-test-report.json", "ODD negative-test evidence is missing."),
    ):
        if not (ROOT / filename).exists():
            blockers.append({"check": filename, "reason": reason})

    if not (ROOT / ".git").is_dir():
        blockers.append({"check": "git_repository", "reason": "The directory is not yet a Git repository."})

    for internal_path in (
        "outputs/job-application-achievement-ja.md",
        "outputs/publication-decisions-ja.md",
        "outputs/viewer-verification.json",
    ):
        if (ROOT / internal_path).exists():
            blockers.append(
                {
                    "check": "internal_working_document",
                    "reason": f"Internal working document is still in the public tree: {internal_path}",
                }
            )

    if (ROOT / "data" / "tei" / "mantiq-sample.xml").exists():
        blockers.append(
            {
                "check": "third_party_text_licence",
                "reason": "The Wikisource-derived sample requires separate CC BY-SA attribution and licensing.",
            }
        )

    required_credit = "Source gallica.bnf.fr / Bibliothèque nationale de France"
    for credit_file in (ROOT / "README.md", ROOT / "viewer" / "index.html", TEI):
        if required_credit not in credit_file.read_text(encoding="utf-8"):
            blockers.append(
                {
                    "check": "gallica_source_credit",
                    "reason": f"Required Gallica source credit is missing from {credit_file.relative_to(ROOT)}.",
                }
            )

    annotation_data = json.loads(ANNOTATIONS.read_text(encoding="utf-8"))
    annotation_id = str(annotation_data.get("id", ""))
    if "127.0.0.1" in annotation_id or "localhost" in annotation_id:
        blockers.append(
            {
                "check": "public_annotation_id",
                "reason": "AnnotationPage id still uses a local-only URL.",
            }
        )

    document = etree.parse(str(TEI))
    names = [" ".join(name.itertext()).strip() for name in document.xpath("//tei:titleStmt/tei:respStmt/tei:name", namespaces=NS)]
    if "Researcher" in names:
        blockers.append(
            {
                "check": "public_researcher_identity",
                "reason": "TEI responsibility statement still contains the placeholder 'Researcher'.",
            }
        )
    if not document.xpath("//tei:publicationStmt/tei:availability/tei:licence", namespaces=NS):
        blockers.append(
            {
                "check": "tei_project_licence",
                "reason": "TEI availability does not yet identify a project data licence.",
            }
        )

    verification = json.loads(VERIFY.read_text(encoding="utf-8")) if VERIFY.exists() else {}
    if not verification.get("all_passed"):
        blockers.append({"check": "project_validation", "reason": "The latest aggregate validation did not pass."})

    if not (ROOT / ".github" / "workflows" / "validate.yml").exists():
        warnings.append({"check": "continuous_integration", "reason": "No GitHub validation workflow is present."})

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "technical_release_checks_passed": not blockers,
        "scope_note": (
            "Technical checks only; this report does not determine third-party rights, "
            "scholarly validity, or external peer-review status."
        ),
        "blocker_count": len(blockers),
        "warning_count": len(warnings),
        "blockers": blockers,
        "warnings": warnings,
        "passed_checks": {
            "aggregate_validation": bool(verification.get("all_passed")),
            "github_validation_workflow": (ROOT / ".github" / "workflows" / "validate.yml").exists(),
            "readme": (ROOT / "README.md").exists(),
            "reproducibility_guide": (ROOT / "outputs" / "reproducibility-guide-ja.md").exists(),
        },
    }
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["technical_release_checks_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
