# Novel Source Discovery - Document Conversion / Literary Similarity Gates - 2026-06-10

## Scope

Static source-intake pass for public GitHub repositories that can improve
MuMuAINovel's book-decomposition import, continuation context health, and
same-type creation copy-risk review.

Boundary: public GitHub metadata, reachable HEAD, README/root-file/license
surface only. No clone, no install, no package manager, no Docker, no OCR/PDF
runtime, no model/provider call, no browser/MCP/desktop runtime, no scripts, and
no private data.

## Reviewed sources

- `microsoft/markitdown`
  - HEAD: `e144e0a2be95b34df17433bac904e635f2c5e551`
  - License: MIT
  - Posture: pattern-only / runtime-deferred
  - Reusable value: file and Office-document to Markdown conversion, optional
    PDF/EPUB/DOCX/OCR surfaces, and LLM-ready Markdown import boundaries.

- `docling-project/docling`
  - HEAD: `1b80839c996136eed47c4875e8a82f0d7ff19c69`
  - License: MIT
  - Posture: pattern-only / runtime-deferred
  - Reusable value: GenAI document parsing, PDF/DOCX/HTML/PPTX/XLSX to
    markdown/json, layout, OCR, table extraction, and typed document elements.

- `opendatalab/MinerU`
  - HEAD: `fc7034cbd324648230f4fb012ee876322b923836`
  - License: NOASSERTION from GitHub metadata
  - Posture: pattern-only / runtime-deferred
  - Reusable value: complex PDF and Office document to LLM-ready Markdown/JSON,
    OCR, layout analysis, PDF parser/extractor and document-analysis vocabulary.

- `datalab-to/marker`
  - HEAD: `d3739db19b78df7d54c1d70340ad5d15134f8b89`
  - License: GPL-3.0
  - Posture: pattern-only / runtime-deferred
  - Reusable value: PDF-to-Markdown/JSON, OCR, chunk conversion, layout-aware
    extraction, and conversion review app/server boundaries.

- `lancopku/Chinese-Literature-NER-RE-Dataset`
  - HEAD: `021b3c1c6a1449634ecb2bf9c4ac17f2c5c870dd`
  - License: no license file observed through public metadata
  - Posture: pattern-only
  - Reusable value: discourse-level Chinese literary entity and relation
    annotation vocabulary for characters, aliases, relationships and locations.

- `ropensci/textreuse`
  - HEAD: `6f8cbe38029502e7cc6baeb169f587a6da0da655`
  - License: NOASSERTION from GitHub metadata
  - Posture: pattern-only
  - Reusable value: text-reuse, pairwise comparison, MinHash, locality-sensitive
    hashing, and text-alignment review gates.

- `cophi-wue/pydelta`
  - HEAD: `35b061403021005713515a9040488e76886b3b48`
  - License: NOASSERTION from GitHub metadata
  - Posture: pattern-only
  - Reusable value: Burrow's Delta / computational-stylistics vocabulary for
    author-style distance and source-voice overfit checks.

## Absorbed patterns

- `source_format_import_manifest`
  - Treat conversion to Markdown/JSON as an auditable import step.
  - Record source format, parser/converter identity, settings, source file,
    metadata, TOC/spine/heading map, skipped sections and conversion gaps.

- `pdf_layout_text_extraction_gate` / `ocr_scanned_page_import_gate`
  - PDF and scanned-page import should keep page spans, layout order, OCR
    confidence and manual-review gaps separate from accepted chapter text.

- `document_partition_chapter_detection_gate`
  - Chapter detection should use typed elements and heading evidence, not blindly
    trust generated Markdown headings.

- `chinese_ner_alias_consistency_gate`
  - Chinese literary entity/relation extraction can feed alias, location,
    faction, title-system and relationship consistency ledgers.

- `source_text_fingerprint_gate` / `minhash_lsh_near_duplicate_gate`
  - Same-type creation should include text-reuse and near-duplicate windows as
    review gates before transformed chapters become accepted canon.

- `stylometric_author_fingerprint_gate`
  - Stylometric distance is a bounded review surface. It should prevent source
    author overfit, not optimize toward source-author attribution.

## Local implementation

- Added the seven reviewed repositories to backend default source-discovery
  seeds.
- Added targeted GitHub Search queries for MarkItDown/Docling/MinerU/marker,
  PDF-to-Markdown/document parser, Chinese literary NER/RE, text reuse and
  pydelta signals.
- Extended existing pattern keywords and static summaries instead of creating a
  new route or runtime dependency.
- Added regression coverage proving that the sources feed import, OCR/layout,
  Chinese NER, text-reuse, MinHash and stylometry gates into pattern packs.

## Runtime exclusions

- No external code, README bodies, AGENTS/CLAUDE files, notebooks, package
  scripts, Dockerfiles, OCR engines, parser runtimes, PDF converters, model
  weights, datasets or provider integrations were imported or executed.
- Future runtime trials require a separate local safety contract covering file
  scope, parser version, conversion settings, licensing, output lineage,
  cleanup, rollback and verification.
