# jTEI Project/Tool Paper Outline

## Working title

**From Persian Manuscript Hemistichs to Verifiable IIIF Regions: A Researcher-in-the-Loop TEI Workflow for *Manṭiq al-ṭayr***

Target category: Project/Tool paper. Target length: approximately 4,000–5,000 words, excluding bibliography and compact code examples.

## Central claim

The contribution is not a new critical text of *Manṭiq al-ṭayr*. It is a small, inspectable workflow showing how manuscript-based Persian verse can be transcribed, modeled, aligned to IIIF regions, compared across witnesses, and tested while preserving the boundary between automatable consistency checks and decisions that remain the researcher’s responsibility.

## 1. Research problem and contribution (500–650 words)

- Explain the difficulty of keeping poetic structure, manuscript evidence, normalization, textual variation, and image locations synchronized.
- State the project’s deliberately small scope: 30 couplets from Persan 348 and an overlapping nine-couplet opening from FSC-MS-28.
- Distinguish the contribution from a critical edition and from a general-purpose transcription platform.
- List the reusable contribution: TEI model, ODD/Schematron constraints, TEI-to-IIIF transformation, cross-file checks, comparison viewer, and explicit AI–researcher responsibility boundary.

Evidence: `README.en.md`, `outputs/technical-report-ja.md`, repository release and DOI.

## 2. Source witnesses and editorial status (450–550 words)

- Identify Persan 348 and FSC-MS-28 with holding institutions and stable source URLs.
- Explain why Persan 348 is an implementation witness, not an asserted best manuscript or critical base text.
- Describe independent transcription and researcher image review.
- Explain the one non-selective apparatus example and why no lemma is selected.
- Describe the `unclear` letter and the repair-related `gap` as examples of preserving uncertainty rather than silently resolving it.

Researcher decisions required before submission: approve the final description of witness selection, palaeographic uncertainty, and what “researcher-reviewed” means.

## 3. TEI data model (850–1,000 words)

- `<lg type="couplet">` for a bayt and two `<l>` elements for hemistichs.
- Stable `xml:id` values for citation and linking.
- `<choice><orig/><reg/></choice>` for local, search-oriented normalization while retaining diplomatic transcription.
- `<app><rdg wit="…"/></app>` for non-selective witness variation.
- `<unclear>` and `<gap>` for different evidential states.
- `<facsimile><surface><zone/></surface></facsimile>` and `@facs` for image-region linking.
- TEI header responsibility, source, licensing, and revision statements.
- Alternatives rejected: a printed edition as silent base text; embedding normalization directly in the diplomatic text; selecting a lemma without adequate evidence; storing coordinates only in viewer code.

Evidence: `data/tei/bnf-persan-348-f6-sample.xml`, `schema/mantiq.odd`, `schema/mantiq.sch`.

## 4. Validation architecture and reproducibility (700–850 words)

- Separate XML well-formedness, official TEI All Relax NG, ODD-generated project Relax NG, and Schematron.
- Explain why grammar validation cannot confirm a manuscript reading.
- Show one negative test demonstrating that the customization rejects an unselected TEI module or invalid project structure.
- Describe pinned TEI P5 4.12.0 and TEI Stylesheets 7.61.0 resources, checksums, and GitHub Actions.
- Explain aggregate verification and release-readiness checks.
- State precisely that the viewer regression script is a static code check; prior human browser observation is stored separately.

Evidence: `scripts/verify_all.py`, `scripts/validate.py`, `scripts/build_odd_schema.py`, `scripts/test_odd_schema.py`, `.github/workflows/validate.yml`.

## 5. TEI–IIIF transformation and viewer (650–800 words)

- Describe grouping hemistichs by Canvas and converting each TEI zone to `xywh`.
- Explain why diplomatic `orig` rather than normalized `reg` is emitted into annotations.
- Describe stable Annotation IDs, external Canvas references, and the absence of redistributed manuscript images.
- Explain cross-checking of body text, region coordinates, identifiers, and counts against TEI.
- Present witness switching and parallel region display as inspection aids, not editorial authority.
- Explicitly limit the conformance claim to the project checks rather than complete IIIF certification.

Evidence: `scripts/tei_to_iiif_annotations.py`, `scripts/validate_iiif_annotations.py`, `iiif/*-annotations.json`, `viewer/index.html`.

## 6. AI delegation and scholarly accountability (500–650 words)

- AI-assisted tasks: specification reconnaissance, candidate transcription and coordinates, boilerplate XML/JSON/code, test generation, documentation drafts.
- Researcher-only decisions: readings, segmentation, uncertainty, normalization policy, witness selection rationale, interpretation of variation, rights judgment, final publication claims.
- Explain researcher-in-the-loop review records and why machine validation cannot substitute for philological judgment.
- Report limitations honestly: no external peer review yet; a small sample; one apparatus locus; no full translation, speaker, or narrative hierarchy data.

Researcher decisions required before submission: approve the precise AI disclosure and confirm that it matches the journal’s current policy at submission time.

## 7. Evaluation, limitations, and reuse (400–550 words)

- Report counts: 39 couplets, 78 hemistichs, three Canvases, 78 annotations, one apparatus locus.
- Report successful full-pipeline validation and external AI code review once completed.
- Discuss what transfers to another Persian verse manuscript and what remains witness-specific.
- Prioritize future work: more independently transcribed loci, richer apparatus evidence, translation alignment, speaker/narrative modeling, and user testing.

## 8. Availability and citation (150–250 words)

- Cite the immutable GitHub release and Zenodo DOI, not only the moving `main` branch.
- Link the live demonstrator as supplementary access.
- State CC BY 4.0 for project data/documentation, MIT for code, and separate holding-institution terms for images.
- Include exact software versions and the reviewed commit SHA.

## Figures and tables

1. Architecture diagram: manuscript sources → TEI → schemas/checks → IIIF AnnotationPages → viewer.
2. Compact TEI example showing `lg/l`, `choice`, `app/rdg`, `unclear`, and `facs`.
3. Screenshot of parallel witness regions with an uncertainty/gap example.
4. Table separating machine-verifiable properties from researcher judgments.
5. Validation table mapping each claim to its validator and evidence file.

## Claims that must not appear

- “Critical edition,” “definitive text,” or “best manuscript,” unless future evidence justifies them.
- Complete IIIF conformance or external scholarly validation.
- A claim that AI read the manuscript reliably without researcher review.
- A claim that schema validity proves palaeographic or philological correctness.

## Submission gates

1. All repository tests pass on a clean clone and GitHub Actions.
2. A second AI/code reviewer’s report is resolved and archived.
3. English README and article statements match actual counts and functions.
4. Researcher approves the witness/editorial descriptions and AI disclosure.
5. A versioned release is issued and archived in Zenodo with a DOI.
6. The article cites the exact release, DOI, and reviewed commit SHA.
