# Historical content notice

The current release data is based on manuscript images from BnF Persan 348 and Smithsonian FSC-MS-28. It does not contain the earlier Wikisource-derived structural sample in the current file tree.

The public Git history nevertheless retains an initial, subsequently deleted file named `data/tei/mantiq-sample.xml` in commit `358a467`. The same file is present in the tree referenced by the annotated `v0.1.0` tag. That file was an experimental TEI structural transcription derived from the Persian Wikisource page *Manṭiq al-ṭayr/Āghāz*, accessed on 13 October 2026. It was not treated as an independent manuscript witness or a critical text and was removed from the release tree in commit `e807038`.

Source and attribution:

- Persian Wikisource, “منطق‌الطیر/آغاز”: <https://fa.wikisource.org/wiki/منطق‌الطیر/آغاز>
- Page history and contributors: <https://fa.wikisource.org/w/index.php?title=منطق‌الطیر/آغاز&action=history>
- The Wikisource page footer makes its text available under the Creative Commons Attribution-ShareAlike License. Accordingly, `data/tei/mantiq-sample.xml` as preserved in Git history and the `v0.1.0` tag is licensed under CC BY-SA 4.0, notwithstanding the unqualified CC BY 4.0 statement in the `LICENSE` file stored in that historical tag.

The following five deleted files also remain retrievable from earlier commits or the `v0.1.0` tag:

- `outputs/job-application-achievement-ja.md`
- `outputs/publication-decisions-ja.md`
- `outputs/viewer-verification.json`
- `outputs/validation-report.json`
- `data/tei/mantiq-sample.xml`

The two planning documents contain project planning text and already-public author identifiers, but no credentials or private third-party data. The two JSON reports describe the superseded initial sample. None of these files is a current release deliverable and none should be cited as current project documentation. There is no GitHub Release object for `v0.1.0`; the repository contains an annotated Git tag only.

The Git history has not been rewritten because no secret or sensitive personal data was found, and rewriting would invalidate published commit references and release ancestry. This notice records the provenance and licensing boundary explicitly.
