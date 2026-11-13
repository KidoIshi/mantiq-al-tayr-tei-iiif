# v0.3.0 — Externally reviewed TEI–IIIF prototype

Version 0.3.0 is the reviewed release of the two-manuscript TEI–IIIF implementation prototype for Farīd al-Dīn ʿAṭṭār’s *Manṭiq al-ṭayr*.

## Scope

- BnF Persan 348: 30 couplets / 60 hemistichs.
- Smithsonian FSC-MS-28: 9 couplets / 18 hemistichs.
- Total: 39 TEI couplets, 78 hemistichs, 3 IIIF Canvases, 3 AnnotationPages, and 78 researcher-reviewed image regions.
- One non-selective manuscript variant apparatus; no lemma is selected.
- Explicit distinction between textual variation, an unclear character, and a passage covered by physical repair.

## Changes since v0.2.0

- Added independent FSC-MS-28 transcription and parallel manuscript comparison.
- Added witness-aware TEI-to-IIIF generation and independent cross-validation.
- Preserved TEI `unclear` information as an IIIF commenting body.
- Added whole-line consistency testing between the apparatus reading and independent witness transcription.
- Added six controlled negative tests for the validation layers.
- Added Mirador subresource-integrity checking, Canvas-dimension validation, release-version consistency checks, and deterministic SHA-256 reporting.
- Documented the licence boundary of the deleted historical Wikisource-derived sample.

## Review and validation

An external AI-assisted code review reported no Blocker or High findings. All 11 Medium findings were resolved and independently rechecked before this release. The final local and GitHub Actions pipelines pass:

- TEI P5 4.12.0 TEI All Relax NG;
- project ODD-generated Relax NG;
- project Schematron;
- witness-specific apparatus and collation tests;
- TEI–IIIF text, uncertainty, region, and Canvas-dimension cross-checks;
- six controlled negative tests;
- public-release readiness check with 0 blockers and 0 warnings.

## Limits

This is a small methodological prototype and manuscript transcription dataset, not a critical edition. The readings and image regions were reviewed by the project researcher but have not undergone scholarly peer review. The external manuscript images are not redistributed and remain subject to the holding institutions’ terms.
