# Manṭiq al-ṭayr TEI–IIIF Prototype

[日本語 README](README.md)

This repository is a small, reproducible prototype for structuring Persian manuscript poetry in TEI P5 and aligning its hemistichs with IIIF image regions. It is a methodological demonstration, not a critical edition.

Researcher: Kido Ishikawa

[ORCID](https://orcid.org/0009-0009-2254-2189) · [researchmap](https://researchmap.jp/kidoishi/)

## Current scope

- 30 couplets (60 hemistichs) independently transcribed from BnF Persan 348.
- A second transcription of the opening 9 couplets (18 hemistichs) from Smithsonian FSC-MS-28.
- 39 TEI `<lg type="couplet">` units, 78 hemistichs, and 78 reviewed TEI-to-IIIF region alignments on three Canvases.
- One non-selective `<app>` with witness-specific `<rdg>` elements; no lemma is selected.
- Diplomatic transcription and limited search-oriented normalization kept distinct with `<choice><orig>…</orig><reg>…</reg></choice>`.
- A project ODD, generated Relax NG schema, Schematron constraints, and negative tests.
- Deterministic TEI-to-IIIF AnnotationPage generation and cross-file validation.
- A browser demonstrator with witness switching, parallel comparison, region previews, and Mirador.

The readings and regions were reviewed by the project researcher against the manuscript images. This does not constitute external peer review.

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
- Speaker markup, narrative hierarchy, and Japanese translation alignment are models or future work, not populated research data.
- The AnnotationPages follow the basic IIIF Presentation API 3 Web Annotation structure and are checked against project rules; no official claim of complete IIIF conformance is made.

## Licences and external images

- Project-created TEI data, IIIF annotations, reports, and documentation: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- Python, HTML, JavaScript, Schematron, and GitHub Actions: MIT License.
- BnF/Gallica and Smithsonian images are not redistributed. The project references external IIIF resources. Image reuse remains subject to the holding institutions' terms.

BnF credit: Source gallica.bnf.fr / Bibliothèque nationale de France.

Smithsonian credit: Smithsonian National Museum of Asian Art; the object page states “Usage Conditions Apply.”

See `LICENSE`, `LICENSE-CODE`, `CITATION.cff`, and the Japanese technical and reproducibility reports under `outputs/` for details.

The repository’s early Git history contains a deleted Wikisource-derived structural sample under a separate share-alike licence. See `HISTORICAL_CONTENT_NOTICE.md` for its provenance, licence boundary, and the reason the public history was not rewritten.
