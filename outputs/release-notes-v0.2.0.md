# v0.2.0 — First public multi-witness prototype

This release provides a reproducible TEI P5–IIIF prototype for a small manuscript-based sample of Farīd al-Dīn ʿAṭṭār's *Manṭiq al-ṭayr*. It is a methodological demonstration, not a critical edition.

## Included

- Diplomatic transcription of 30 couplets (60 hemistichs) from BnF Persan 348.
- Independent transcription of the opening nine couplets (18 hemistichs) from Smithsonian FSC-MS-28.
- Researcher-reviewed links between 78 hemistichs and image regions on three IIIF Canvases.
- A small non-selective TEI critical apparatus and automated collation of the overlapping sample.
- A project ODD, generated Relax NG schema, Schematron constraints, and automated validation.
- IIIF Presentation 3 AnnotationPages generated from the TEI source.
- A browser demonstrator for witness switching, parallel comparison, and manuscript-image viewing.
- Documentation of editorial decisions, reproducibility, and the division of responsibility between AI assistance and researcher judgment.

## Scope and limitations

- Persan 348 is a practice witness, not an established best or base manuscript.
- The release does not claim to be a complete or critical edition.
- “Researcher-reviewed” means comparison with the cited manuscript images by the project researcher; it does not mean external peer review.
- Japanese translation alignment, speaker annotation, nested narrative structures, and multi-witness lemma selection remain future work.
- External manuscript images are referenced through institutional IIIF services and are not redistributed under the project's CC BY or MIT licenses.

## Verification

Run `python scripts/verify_all.py` to regenerate derived data and execute the XML, TEI, project-schema, Schematron, collation, viewer, and TEI–IIIF consistency checks.

Project-created data and documentation are licensed CC BY 4.0. Code is licensed under the MIT License. Third-party manuscript images remain subject to the source institutions' terms.
