# Novel Source Discovery - Source Rights Provenance Gates - 2026-06-10

## Purpose

Absorb source-rights and provenance patterns for MuMuAINovel's book
deconstruction, continuation, and same-type writing workflows.

The goal is not to import legal tooling or public-domain corpora. The goal is
to add admission gates before source text, corpus output, or adaptation-risk
material enters analysis and drafting context.

## Static Source Snapshot

All HEADs below were refreshed with `git ls-remote <repo> HEAD` on
2026-06-10. Only public metadata, root license files, README, and project
metadata were inspected.

- `licensee/licensee`
  - HEAD: `dad4bb434b80a3d86bf9660f0db0e622a4d5d087`
  - default branch: `main`
  - license: MIT via GitHub metadata and `LICENSE.md`
  - posture: `pattern-only`
  - absorbed pattern: `source_license_detection_gate`

- `fsfe/reuse-tool`
  - HEAD: `20e2e152790022891d67f1074c6dbce0494ad7cd`
  - default branch: `main`
  - license: `Apache-2.0 AND CC0-1.0 AND CC-BY-SA-4.0 AND GPL-3.0-or-later`
    from `pyproject.toml`; root files use SPDX headers
  - posture: `pattern-only`
  - absorbed pattern: `spdx_reuse_compliance_gate`

- `spdx/license-list-data`
  - HEAD: `421fbabbe80c94c58c12316af1bc6a2dca2362bc`
  - default branch: `main`
  - license: no GitHub API license assertion observed; README says the
    repository contains generated SPDX License List data
  - posture: `pattern-only`
  - absorbed patterns: `spdx_reuse_compliance_gate`,
    `attribution_derivative_work_gate`

- `c-w/Gutenberg`
  - HEAD: `123d13435b31a39f6fda3c4df2976a40f74633a1`
  - default branch: `master`
  - license: Apache-2.0 via GitHub metadata and `LICENSE.txt`
  - repository state: archived in GitHub metadata
  - posture: `pattern-only`
  - absorbed pattern: `public_domain_corpus_boundary`

- `Imkun-on/gutenberg-corpus-cli`
  - HEAD: `8bf8ca7260a0a3c1c233a30eb629771beea9639e`
  - default branch: `main`
  - license: MIT via GitHub metadata and `LICENSE`
  - posture: `pattern-only`; runtime-deferred
  - absorbed pattern: `public_domain_corpus_boundary`
  - risk flag: `corpus_downloader`

## Absorbed Workflow Patterns

- `source_license_detection_gate`
  - Detect and record source license status before source-book import,
    deconstruction, continuation, or same-type imitation uses long text.
  - Unknown, missing, or low-confidence license status blocks copying source
    passages into prompts.

- `spdx_reuse_compliance_gate`
  - Normalize rights metadata to SPDX ids where possible.
  - Keep copyright holders, attribution notes, reviewer decisions, and
    source-file provenance outside story canon.

- `public_domain_corpus_boundary`
  - Public-domain sources still require title, author, source URL, observed
    date, extraction format, and jurisdiction caveat.
  - Corpus downloaders remain runtime-deferred. Metadata can guide admission;
    downloader output is not drafting context by default.

- `attribution_derivative_work_gate`
  - Classify each source as inspiration, quotation, adaptation, translation, or
    derivative-risk material before same-type writing.
  - Attribution does not replace independent plot, character, setting, event
    order, and phrasing checks.

## Runtime Exclusions

No external repository was cloned, installed, executed, or imported.

Excluded by design:

- Ruby gems and `licensee` runtime
- REUSE CLI/package execution
- generated SPDX data import into prompts or runtime context
- Gutenberg download, scraping, cleaning, SQLite, or full-text-search runtime
- external scripts, package managers, Docker, native binaries, MCP servers, or
  browser extensions

## Artifacts Updated

- `backend/app/services/source_discovery_service.py`
- `backend/app/services/source_pattern_pack_prompt.py`
- `backend/app/services/book_remix_context_service.py`
- `backend/app/references/novel-source-pattern-pack-2026-06-10.json`
- `backend/tests/services/test_source_discovery_service.py`
- `backend/tests/services/test_book_remix_context_service.py`
