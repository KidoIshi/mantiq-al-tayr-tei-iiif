# Manṭiq al-ṭayr in TEI and IIIF: A Two-Manuscript Transcription Prototype

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24202416.svg)](https://doi.org/10.5281/zenodo.24202416)

[日本語 README](README.md)

This repository demonstrates how Persian manuscript poetry can be structured in TEI P5 and linked at the hemistich level to IIIF image regions. It documents the data, transformation, and validation steps used for two manuscript witnesses. It is a methodological prototype, not a critical edition.

Researcher: Kido Ishikawa

[ORCID](https://orcid.org/0009-0009-2254-2189) · [researchmap](https://researchmap.jp/kidoishi/)

**Live demonstrator: [Open the TEI–IIIF viewer](https://kidoishi.github.io/mantiq-al-tayr-tei-iiif/viewer/)**

Archived releases and citation metadata: [Zenodo (concept DOI: 10.5281/zenodo.24202416)](https://doi.org/10.5281/zenodo.24202416)

Latest archived release: [Zenodo v0.3.2 (DOI: 10.5281/zenodo.24202704)](https://doi.org/10.5281/zenodo.24202704)

## Current scope

- 30 couplets (60 hemistichs) transcribed from BnF Persan 348.
- A separate transcription of the corresponding opening 9 couplets (18 hemistichs) from Smithsonian FSC-MS-28.
- 39 TEI `<lg type="couplet">` units, 78 hemistichs, and 78 TEI-to-IIIF region alignments on three Canvases.
- Automated collation of the 18 overlapping hemistichs: 16 exact matches, one textual variant (0004b), and one passage partly covered by physical repair (0006a).
- One non-selective `<app>` with witness-specific `<rdg>` elements; no lemma is selected.
- Diplomatic transcription and limited search-oriented normalization kept distinct with `<choice><orig>…</orig><reg>…</reg></choice>`.
- A project ODD, generated Relax NG schema, Schematron constraints, and negative tests.
- Deterministic TEI-to-IIIF AnnotationPage generation and cross-file validation.
- A browser demonstrator with witness switching, parallel comparison, region previews, and Mirador.

The author checked the transcriptions and image regions against the manuscript images. They have not yet been independently reviewed.

AI tools were used to prepare initial transcription candidates, image-region proposals, code, and documentation drafts. The author made the editorial decisions, checked the manuscript transcriptions and image regions, reviewed the implementation structure and validation results, and approved the changes included in the release. A second AI system provided an additional code review; its findings, the resulting changes, and the subsequent checks are documented in the repository.

## Reproduce and validate

Requirements are Python 3, Java 17 or later, and the Python packages listed in `requirements.txt`. The build pins TEI P5 4.12.0 and TEI Stylesheets 7.61.0 resources and verifies their checksums.

```powershell
python -m pip install -r requirements.txt
python scripts/verify_all.py
python scripts/check_release_readiness.py
```

The validation pipeline distinguishes three layers:

- official TEI All Relax NG: conformance to TEI P5;
- ODD-generated project Relax NG: conformance to the selected TEI modules;
- project Schematron: local rules such as two hemistichs per couplet, identifier patterns, resolvable facsimile links, and valid image coordinates.

To run the viewer locally:

```powershell
python -m http.server 8000
```

Then open `http://localhost:8000/viewer/`. Network access is required for external IIIF resources and the Mirador CDN.

## Editorial and technical limits

- Persan 348 was selected as a practical witness for learning and implementation, not identified as a best manuscript or a base text for a critical edition.
- The normalized forms are experimental search aids, not readings from a printed edition or an edited text.
- The apparatus contains only one manuscript-supported variant and does not constitute a critical edition.
- Speaker markup, narrative hierarchy, and Japanese translation alignment are described in design documents but have not been populated as research data.
- The AnnotationPages follow the basic IIIF Presentation API 3 Web Annotation structure. They have been checked against the project rules, but not against an official IIIF conformance test suite.

## Licences and external images

- Project-created TEI data, IIIF annotations, reports, and documentation: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- Python, HTML, JavaScript, Schematron, and GitHub Actions: MIT License.
- BnF/Gallica and Smithsonian images are not redistributed. The project references external IIIF resources. Image reuse remains subject to the holding institutions' terms.

BnF credit: Source gallica.bnf.fr / Bibliothèque nationale de France.

Smithsonian credit: Smithsonian National Museum of Asian Art; the object page states “Usage Conditions Apply.”

See `LICENSE`, `LICENSE-CODE`, `CITATION.cff`, and the Japanese technical and reproducibility reports under `outputs/` for details.

The repository’s early Git history contains a deleted Wikisource-derived structural sample under a separate share-alike licence. See `HISTORICAL_CONTENT_NOTICE.md` for its provenance, licence boundary, and the reason the public history was not rewritten.
