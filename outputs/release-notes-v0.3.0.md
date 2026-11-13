# v0.3.0 — Two-manuscript TEI–IIIF prototype

Version 0.3.0 documents a TEI–IIIF implementation prototype for two manuscript witnesses of Farīd al-Dīn ʿAṭṭār’s *Manṭiq al-ṭayr*.

## Scope

- BnF Persan 348: 30 couplets / 60 hemistichs.
- Smithsonian FSC-MS-28: 9 couplets / 18 hemistichs.
- Total: 39 TEI couplets, 78 hemistichs, 3 IIIF Canvases, 3 AnnotationPages, and 78 image regions checked by the author against the manuscripts.
- One non-selective manuscript variant apparatus; no lemma is selected.
- Explicit distinction between textual variation, an unclear character, and a passage covered by physical repair.
- Automated collation of the 18 overlapping hemistichs: 16 exact matches, one textual variant (0004b), and one passage partly covered by physical repair (0006a).

## Changes since v0.2.0

- Added independent FSC-MS-28 transcription and parallel manuscript comparison.
- Added witness-aware TEI-to-IIIF generation and independent cross-validation.
- Preserved TEI `unclear` information as an IIIF commenting body.
- Added whole-line consistency testing between the apparatus reading and independent witness transcription.
- Added six controlled negative tests for the validation layers.
- Added Mirador subresource-integrity checking, Canvas-dimension validation, release-version consistency checks, and deterministic SHA-256 reporting.
- Documented the licence boundary of the deleted historical Wikisource-derived sample.

## Review and validation

An AI-assisted external code review identified no Blocker or High-severity issues. The 11 Medium-severity findings were addressed and rechecked before this release. The local and GitHub Actions pipelines pass:

- TEI P5 4.12.0 TEI All Relax NG;
- project ODD-generated Relax NG;
- project Schematron;
- witness-specific apparatus and collation tests;
- TEI–IIIF text, uncertainty, region, and Canvas-dimension cross-checks;
- six controlled negative tests;
- public-release readiness check with 0 blockers and 0 warnings.

## Limits

This is a small methodological prototype and manuscript transcription dataset, not a critical edition. The author checked the transcriptions and image regions against the manuscript images; they have not undergone independent scholarly review. The external manuscript images are not redistributed and remain subject to the holding institutions’ terms.

AI tools were used to prepare initial transcription candidates, image-region proposals, code, and documentation drafts. The author made the editorial decisions, checked the manuscript transcriptions and image regions, reviewed the implementation structure and validation results, and approved the changes included in the release. A second AI system provided an additional code review; its findings, the resulting changes, and the subsequent checks are documented in the repository.
