# Novel Source Discovery - 2026-06-11 Source Import / OCR

## Purpose

This note absorbs public GitHub source-import, PDF extraction, OCR, and document
partition projects for the MuMuAINovel book-remix workflow.

The goal is not to install import tools. The goal is to add review gates so
source books can be imported, deconstructed, continued, or used for same-type
creation without mixing raw extraction artifacts into accepted canon.

## Safety Boundary

Static intake only.

- No repository was cloned.
- No package manager, installer, binary, OCR engine, parser, converter, Docker
  stack, model, language data, or provider call was executed.
- AGPL/GPL/MPL projects are pattern-only references.
- Original files, extracted text, normalized text, and accepted manuscript text
  must remain separate artifacts.

## Source Snapshot

| Source | Observed HEAD | License | Posture | Absorbed patterns |
|---|---|---|---|---|
| `aerkalov/ebooklib` | `a50289fb9d4039224d54bf7d92698eb03cd68254` | AGPL-3.0 | pattern-only | `source_format_import_manifest`, `import_provenance_checksum_gate` |
| `pdfminer/pdfminer.six` | `a18de2a9c479b4c847538500017b449ddaec177e` | MIT-like | pattern-only | `pdf_layout_text_extraction_gate` |
| `pymupdf/PyMuPDF` | `d981d87e87924962f7975dc2ed746e6c627e6cf6` | AGPL-3.0/commercial | pattern-only | `pdf_layout_text_extraction_gate`, `source_format_import_manifest` |
| `ocrmypdf/OCRmyPDF` | `5cb5d7a682095700aa28eb592a94c0fe28e94fd0` | MPL-2.0 | pattern-only | `ocr_scanned_page_import_gate` |
| `tesseract-ocr/tesseract` | `f4afb2cc9545f622a07812b09e1b72fc78f85a64` | Apache-2.0 | pattern-only | `ocr_scanned_page_import_gate` |
| `Unstructured-IO/unstructured` | `19857c193657b5f1b0ca922562a3015b38cc6fb8` | Apache-2.0 | pattern-only | `document_partition_chapter_detection_gate`, `source_format_import_manifest` |
| `jgm/pandoc` | `912bfa5e2e3f5c74eb125dfc19404f67c61ca58b` | GPL-2-or-later | pattern-only | `source_format_import_manifest`, `import_provenance_checksum_gate` |

## Reusable Patterns

### `source_format_import_manifest`

Record import facts before any source-book analysis:

- source format: EPUB, PDF, DOCX, Markdown, TXT, or converted artifact
- metadata: title, author, language, edition, publisher fields when present
- TOC and spine/order evidence
- detected chapter ids and section labels
- skipped sections, front matter, back matter, footnotes, tables, and images
- accepted/rejected import decisions

This keeps an imported source artifact from becoming implicit canon.

### `pdf_layout_text_extraction_gate`

PDF text is not trusted until layout evidence is reviewed.

Track:

- page number and page span
- text block order
- coordinates when available
- headers, footers, page numbers, footnotes, and two-column risk
- extraction gaps and unreadable spans

Do not let page-span rhythm or layout-derived section order become the new story
outline in same-type creation.

### `ocr_scanned_page_import_gate`

Scanned-page OCR is a deferred runtime lane.

Track:

- OCR engine and language setting
- page image range
- confidence score or confidence band when available
- low-confidence spans
- unreadable pages
- manual-review decision

Low-confidence OCR text should not feed canon, glossary, style fingerprinting,
or generation context until reviewed.

### `document_partition_chapter_detection_gate`

Document partition output must stay typed until accepted.

Track:

- element type: title, narrative text, list, table, image, note, footer
- normalized heading text
- TOC match or mismatch
- neighboring section boundaries
- uncertain chapter-heading candidates

Bad partitioning can corrupt chapter order and source summaries, so uncertain
headings remain review items.

### `import_provenance_checksum_gate`

Every derived text artifact needs lineage.

Track:

- source path or source URI
- checksum and file size
- parser/converter name and version
- settings and language mode
- import timestamp
- relationship among original, extracted, normalized, and accepted text

When parser settings change, derived summaries, glossary entries, fingerprints,
and copy-risk reports need invalidation or review.

## Project Integration

Updated artifacts:

- `backend/app/services/source_discovery_service.py`
- `backend/app/services/source_pattern_pack_prompt.py`
- `backend/app/services/book_remix_context_service.py`
- `backend/app/references/novel-source-pattern-pack-2026-06-10.json`
- `backend/tests/services/test_source_discovery_service.py`
- `backend/tests/services/test_book_remix_context_service.py`

Pattern pack now records:

- `source_candidate_count: 144`
- `workflow_patterns: 180`
- five new source-import/OCR workflow patterns

## Deferred Runtime Gates

Runtime import/OCR support remains blocked until a separate local safety contract
exists for:

- file scope and scratch path
- parser/OCR/converter binary provenance
- no-network mode where possible
- license boundary
- cleanup and rollback
- reproducible checksum evidence
- manual review before canon write-back
