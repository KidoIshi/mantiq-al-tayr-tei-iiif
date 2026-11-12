#!/usr/bin/env python3
"""Report concrete blockers before creating a public release."""

from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from lxml import etree


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs" / "publication-readiness.json"
TEI = ROOT / "data" / "tei" / "bnf-persan-348-f6-sample.xml"
VERIFY = ROOT / "outputs" / "project-verification-summary.json"
NS = {"tei": "http://www.tei-c.org/ns/1.0"}

GALLICA_CREDIT = "Source gallica.bnf.fr / Bibliothèque nationale de France"
SMITHSONIAN_CREDIT = "Smithsonian National Museum of Asian Art"
SMITHSONIAN_STATUS = "Usage Conditions Apply"
PUBLIC_BASE = "https://kidoishi.github.io/mantiq-al-tayr-tei-iiif/"


def tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )
    return [line for line in result.stdout.splitlines() if line]


def main() -> int:
    blockers: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    required_files = (
        "LICENSE",
        "LICENSE-CODE",
        "CITATION.cff",
        "README.md",
        "schema/mantiq.odd",
        "schema/mantiq.rng",
        "schema/mantiq.sch",
        "outputs/reproducibility-guide-ja.md",
        "outputs/technical-report-ja.md",
        "outputs/publication-audit-ja.md",
        "outputs/opening-witness-collation.json",
        "outputs/viewer-comparison-test.json",
        "outputs/odd-build-report.json",
        "outputs/odd-negative-test-report.json",
    )
    for filename in required_files:
        if not (ROOT / filename).exists():
            blockers.append({"check": filename, "reason": "Required release file is missing."})

    if not (ROOT / ".git").is_dir():
        blockers.append({"check": "git_repository", "reason": "The directory is not a Git repository."})

    tracked = tracked_files()
    private_prefixes = ("private/", "output/", "tmp/", "work/")
    for path in tracked:
        if path.startswith(private_prefixes):
            blockers.append({"check": "private_path_tracked", "reason": f"Private/generated path is tracked: {path}"})

    for internal_path in (
        "outputs/job-application-achievement-ja.md",
        "outputs/publication-decisions-ja.md",
        "outputs/viewer-verification.json",
    ):
        if (ROOT / internal_path).exists():
            blockers.append(
                {"check": "internal_working_document", "reason": f"Internal working document remains in the public tree: {internal_path}"}
            )

    if (ROOT / "data" / "tei" / "mantiq-sample.xml").exists():
        blockers.append(
            {"check": "third_party_text_licence", "reason": "The old Wikisource-derived sample requires separate attribution and licensing."}
        )

    rights_requirements = {
        "README.md": (GALLICA_CREDIT, SMITHSONIAN_CREDIT, SMITHSONIAN_STATUS),
        "viewer/index.html": (GALLICA_CREDIT, SMITHSONIAN_CREDIT, SMITHSONIAN_STATUS),
        "data/tei/bnf-persan-348-f6-sample.xml": (GALLICA_CREDIT, SMITHSONIAN_CREDIT, SMITHSONIAN_STATUS),
        "LICENSE": (GALLICA_CREDIT, SMITHSONIAN_CREDIT, SMITHSONIAN_STATUS),
    }
    for filename, phrases in rights_requirements.items():
        text = (ROOT / filename).read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in text:
                blockers.append({"check": "third_party_credit", "reason": f"{filename} is missing: {phrase}"})

    citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8") if (ROOT / "CITATION.cff").exists() else ""
    for phrase in ("version: 0.2.0", "Persan 348", "FSC-MS-28", "78 reviewed hemistich-to-image"):
        if phrase not in citation:
            blockers.append({"check": "citation_metadata", "reason": f"CITATION.cff is missing current-scope text: {phrase}"})

    registry_path = ROOT / "iiif" / "manifest-registry.json"
    if registry_path.exists():
        registry_text = registry_path.read_text(encoding="utf-8")
        if "asia-archive.si.edu" in registry_text:
            blockers.append({"check": "current_object_url", "reason": "Manifest registry still uses the retired Smithsonian archive URL."})
        if "https://www.si.edu/termsofuse" not in registry_text:
            blockers.append({"check": "smithsonian_rights_url", "reason": "Manifest registry lacks the Smithsonian rights URL."})

    annotation_paths = sorted((ROOT / "iiif").glob("*-annotations.json"))
    if len(annotation_paths) != 3:
        blockers.append({"check": "annotation_pages", "reason": f"Expected 3 AnnotationPages, found {len(annotation_paths)}."})
    annotation_count = 0
    for annotation_path in annotation_paths:
        annotation_data = json.loads(annotation_path.read_text(encoding="utf-8"))
        annotation_id = str(annotation_data.get("id", ""))
        annotation_count += len(annotation_data.get("items", []))
        if not annotation_id.startswith(PUBLIC_BASE):
            blockers.append({"check": "public_annotation_id", "reason": f"Non-public AnnotationPage id in {annotation_path.name}: {annotation_id}"})
    if annotation_count != 78:
        blockers.append({"check": "annotation_count", "reason": f"Expected 78 annotations, found {annotation_count}."})

    document = etree.parse(str(TEI))
    names = [" ".join(name.itertext()).strip() for name in document.xpath("//tei:titleStmt/tei:respStmt/tei:name", namespaces=NS)]
    if "Researcher" in names:
        blockers.append({"check": "public_researcher_identity", "reason": "TEI responsibility statement contains the placeholder 'Researcher'."})
    if not document.xpath("//tei:publicationStmt/tei:availability/tei:licence", namespaces=NS):
        blockers.append({"check": "tei_project_licence", "reason": "TEI availability does not identify a project data licence."})
    tei_counts = {
        "couplets": int(document.xpath("count(//tei:lg[@type='couplet'])", namespaces=NS)),
        "hemistichs": int(document.xpath("count(//tei:lg[@type='couplet']/tei:l)", namespaces=NS)),
        "surfaces": int(document.xpath("count(//tei:facsimile/tei:surface)", namespaces=NS)),
    }
    if tei_counts != {"couplets": 39, "hemistichs": 78, "surfaces": 3}:
        blockers.append({"check": "tei_release_counts", "reason": f"Unexpected TEI counts: {tei_counts}"})

    verification = json.loads(VERIFY.read_text(encoding="utf-8")) if VERIFY.exists() else {}
    if not verification.get("all_passed"):
        blockers.append({"check": "project_validation", "reason": "The latest aggregate validation did not pass."})

    viewer_test_path = ROOT / "outputs" / "viewer-comparison-test.json"
    viewer_test = json.loads(viewer_test_path.read_text(encoding="utf-8")) if viewer_test_path.exists() else {}
    if not viewer_test.get("all_passed"):
        blockers.append({"check": "viewer_validation", "reason": "The comparison viewer regression check did not pass."})

    text_suffixes = {".md", ".xml", ".json", ".html", ".py", ".yml", ".yaml", ".cff", ".txt"}
    local_path_pattern = re.compile(r"(?:[A-Za-z]:\\Users\\|file://)", re.IGNORECASE)
    secret_pattern = re.compile(
        r"(?:-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----|"
        r"gh[pousr]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|"
        r"(?:api[_-]?key|password|secret|token)\s*[:=]\s*['\"][^'\"]{8,})",
        re.IGNORECASE,
    )
    secret_matches = 0
    for relative in tracked:
        if relative == "scripts/check_release_readiness.py":
            continue
        path = ROOT / relative
        if path.suffix.lower() not in text_suffixes or not path.exists():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if local_path_pattern.search(text):
            blockers.append({"check": "local_path_disclosure", "reason": f"Local filesystem path appears in tracked file: {relative}"})
        if secret_pattern.search(text):
            secret_matches += 1
            blockers.append({"check": "secret_disclosure", "reason": f"Possible credential appears in public candidate: {relative}"})

    tracked_images = [path for path in tracked if Path(path).suffix.lower() in {".jpg", ".jpeg", ".png", ".tif", ".tiff"}]
    if tracked_images:
        warnings.append({"check": "tracked_images", "reason": f"Review image rights before release: {', '.join(tracked_images)}"})

    workflow_exists = (ROOT / ".github" / "workflows" / "validate.yml").exists()
    if not workflow_exists:
        warnings.append({"check": "continuous_integration", "reason": "No GitHub validation workflow is present."})
    else:
        workflow_text = (ROOT / ".github" / "workflows" / "validate.yml").read_text(encoding="utf-8")
        for action in ("actions/checkout@v6", "actions/setup-python@v7", "actions/setup-java@v6"):
            if action not in workflow_text:
                warnings.append({"check": "github_action_version", "reason": f"Review GitHub Action version: expected {action}."})

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "technical_release_checks_passed": not blockers,
        "scope_note": "Technical and documentation checks only; final rights assessment, scholarly validity, repository visibility, and external peer review require human judgment.",
        "blocker_count": len(blockers),
        "warning_count": len(warnings),
        "blockers": blockers,
        "warnings": warnings,
        "passed_checks": {
            "aggregate_validation": bool(verification.get("all_passed")),
            "viewer_validation": bool(viewer_test.get("all_passed")),
            "github_validation_workflow": workflow_exists,
            "tei_counts": tei_counts,
            "annotation_pages": len(annotation_paths),
            "annotations": annotation_count,
            "third_party_images_tracked": len(tracked_images),
            "possible_credentials": secret_matches,
        },
        "manual_release_actions": [
            "Review the final Git diff and commit the release candidate.",
            "Confirm that the repository may be changed from private to public.",
            "Enable and verify GitHub Pages after publication.",
            "Create a version tag/release and update CITATION.cff if the version changes.",
            "Optionally archive the tagged release in Zenodo and add the DOI.",
        ],
    }
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["technical_release_checks_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
