# Manṭiq al-ṭayr TEI–IIIF Manuscript Prototype

Updated: 11 November 2026
Status: small-scale prototype reviewed against the manuscript image by the project researcher; not externally peer-reviewed

## Overview

This project develops a reproducible TEI–IIIF workflow for Farīd al-Dīn ʿAṭṭār’s *Manṭiq al-ṭayr* using Bibliothèque nationale de France, Persan 348. It is not presented as a completed critical edition. Its current purpose is to demonstrate how a manuscript-based diplomatic transcription, controlled normalization, image-region alignment, standards conversion, and validation can be combined in a transparent digital-humanities workflow.

## Implemented dataset

- 21 couplets and 42 hemistichs from Gallica scans f6 and f7.
- Persian readings and line pairing reviewed against the image by the project researcher; this is not external peer review.
- Stable identifiers for every couplet and hemistich.
- Three approved `choice/orig/reg` normalizations, while retaining the diplomatic reading as the default.
- 42 TEI `zone` regions reviewed against the image by the project researcher and linked from the hemistichs with `@facs`.
- Two generated IIIF Presentation 3 AnnotationPages containing 42 `supplementing` Web Annotations targeting the BnF f6 and f7 Canvases with `xywh` fragments.
- A browser demonstrator with diplomatic/normalized display, hemistich-region previews, and a Mirador manuscript viewer.

## Data model

Each Persian *bayt* is encoded as `<lg type="couplet">`, and its two *miṣrāʿ*s as `<l n="a">` and `<l n="b">`. The TEI document is the authoritative source for textual structure, editorial responsibility, and image regions. Each `surface/@corresp` identifies its IIIF Canvas. A deterministic converter exports the approved diplomatic transcription and TEI zones as one AnnotationPage per Canvas. The normalization layer is not allowed to overwrite the manuscript transcription.

## Validation

The current dataset passes:

- XML well-formedness checking;
- the official TEI P5 Relax NG schema;
- the project Relax NG schema generated from `schema/mantiq.odd`;
- project-specific Schematron constraints;
- a TEI–IIIF cross-check confirming that all 42 annotation bodies match the diplomatic TEI text and all 42 Canvas targets match the TEI zones.

Machine-readable reports and a one-command verification script are included in the project.

## AI and researcher responsibility

AI-assisted work includes technical research, initial transcription and region proposals, repetitive XML/JSON generation, transformation code, validation, interface prototyping, and documentation drafting. The researcher remains responsible for manuscript selection and scope, paleographical reading, line pairing, uncertainty assessment, normalization policy, approval of image regions, scholarly interpretation, rights decisions, and the final description of the project’s contribution.

The technical competence demonstrated here is therefore not manual XML entry. It is the ability to understand the TEI and IIIF data models, assign appropriate work to automation, define constraints, verify AI-assisted outputs, document provenance, and distinguish technical validity from scholarly validity.

## Current limitations

- The sample covers 21 couplets rather than the complete work.
- Persan 348 is used as a practice witness, not established as a best or base manuscript.
- No multi-witness critical apparatus has yet been encoded.
- Japanese translation alignment, speaker annotation, and nested narrative structures remain future work.
- The repository has not yet been released publicly and no DOI has been assigned.

## Next milestones

The next research milestone is to expand the reviewed sample toward 30 couplets and apply one additional scholarly layer—translation alignment or an independently attested manuscript variant—before preparing a versioned public release and a conference proposal.
