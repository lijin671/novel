# Novel Source Discovery - 2026-06-10 Ebook Quality Gates

## Scope

Static source-intake pass for ebook publication quality gates that can improve
MuMuAINovel's拆书续写、同类型仿写 and final manuscript delivery path.

This pass used only public GitHub metadata, `git ls-remote` HEAD checks, and
small public README/LICENSE/root-file probes. No repository was cloned, no
package was installed, and no upstream script, binary, Java tool, npm package,
Qt app, test EPUB, or accessibility checker was executed.

## Source snapshot

- [w3c/epubcheck](https://github.com/w3c/epubcheck)
  - HEAD: `82b174ec319ea3e6c9d2488f84155fa4a9171fc2`
  - branch: `main`
  - observed license surface: BSD-style license text in `LICENSE.md`
  - posture: `pattern-only`
  - absorbed value: EPUB conformance gates for package document, OPF manifest,
    spine, nav document, media types, and validation-report review.

- [daisy/ace](https://github.com/daisy/ace)
  - HEAD: `dfa87b528f598a034f98e8a3126bf4b5bf9203bf`
  - branch: `master`
  - observed license surface: MIT license in `LICENSE.txt`
  - posture: `pattern-only`
  - absorbed value: EPUB accessibility audit gates for metadata, landmarks,
    heading levels, reading order, alt text, language, and hazards.

- [standardebooks/tools](https://github.com/standardebooks/tools)
  - HEAD: `c7d526c6928828a79f8b412cd66dba145a1a36e3`
  - branch: `master`
  - observed license surface: GPLv3 with template/data exceptions noted in
    `LICENSE.md`
  - posture: `pattern-only`
  - absorbed value: front/back matter and publication metadata gates for title
    page, endnotes, colophon, identifiers, and release checks.

- [Sigil-Ebook/Sigil](https://github.com/Sigil-Ebook/Sigil)
  - HEAD: `79ca6771be61305673b9123c8c0a0ee74bd044ee`
  - branch: `master`
  - observed license surface: GPL license text in `COPYING.txt`
  - posture: `pattern-only`
  - absorbed value: TOC/navigation consistency gates for visible headings,
    nav/NCX entries, spine order, landmarks, and reader navigation.

- [w3c/epub-tests](https://github.com/w3c/epub-tests)
  - HEAD: `45feac979d9b12b502f124db7bc5056977628417`
  - branch: `main`
  - observed license surface: W3C Software and Document License notes in
    `LICENSE.md`
  - posture: `pattern-only`
  - absorbed value: regression-fixture pattern for EPUB structure and
    navigation checks. Test EPUB assets were not imported.

- [daisy/epub-accessibility-tests](https://github.com/daisy/epub-accessibility-tests)
  - HEAD: `6ecadf3393083dd93fa79d8b62e0281957a7b05e`
  - branch: `main`
  - observed license surface: no root license found in the static probe
  - posture: `pattern-only; license-review-required`
  - absorbed value: accessibility fixture pattern for reading-system behavior.
    Test books were not downloaded.

## Absorbed patterns

### `epub_structure_validation_gate`

Use this when accepted chapters are being assembled into EPUB or EPUB-like
manuscript artifacts.

Gate checklist:

- container/package document exists and points to the expected package file
- OPF manifest contains only expected accepted chapter/content assets
- spine order matches the accepted chapter order
- nav document is present and internally consistent
- media types and file references are valid
- validation warnings/errors are captured in a reviewable report

For拆书/仿写, source EPUB structure is evidence only. It must not define the new
story's chapter order or metadata.

### `ebook_accessibility_audit_gate`

Use this before final ebook export, especially when chapters include images,
front/back matter, or complex navigation.

Gate checklist:

- language and accessibility metadata are explicit
- landmarks and heading levels support reader navigation
- reading order matches the intended chapter flow
- images/captions/alt text are reviewed
- hazard notes and accessibility caveats are separated from canon

For同类型仿写, accessibility standards can transfer, but captions, alt text,
landmark labels, and source media descriptions must be regenerated.

### `front_back_matter_metadata_gate`

Use this to keep publication shell material separate from story canon.

Gate checklist:

- title page, copyright, dedication, foreword, endnotes, afterword, colophon,
  identifiers, and publication metadata live in a delivery manifest
- attribution/rights notes come from the source-rights gate, not from story
  prompts
- front/back matter does not silently enter continuation context

For same-type creation, title/subtitle/blurb-adjacent metadata must come from
the transformed book, not the reference work.

### `toc_navigation_consistency_gate`

Use this for preview and final export review.

Gate checklist:

- accepted chapter headings match TOC entries
- nav/NCX entries match spine order
- landmarks and preview navigation resolve to the right sections
- missing, duplicate, empty, or reordered entries are reported separately from
  prose quality findings

For same-type creation, navigation should be rebuilt from the transformed
outline after independence checks.

## Repository changes

- Added the six sources to the default GitHub repository intake list.
- Added four publication-quality workflow patterns to source classification.
- Added pattern-pack hints, bible targets, whole-book analysis targets, and
  same-type remap/copy-risk guidance.
- Added continuation and inspired-context prompt audit block:
  `Ebook quality audit`.
- Added tests for classification, pattern-pack rendering, default discovery,
  and prompt-block injection.

## Deferred/runtime gates

- Do not run EPUBCheck, Ace, Standard Ebooks tools, Sigil, EPUB test suites, or
  accessibility fixtures during source intake.
- Runtime validation would need a separate local safety contract covering input
  files, generated outputs, installed tools, network, cleanup, and rollback.
- License-missing or license-uncertain test fixtures stay metadata-only until a
  reviewer records an explicit admission decision.

## Pattern pack refresh

- source_candidate_count: 195
- workflow_patterns: 211
- generated_at: 2026-06-10T19:40:00+08:00
