# Novel Source Discovery - 2026-06-12 Local Editor / Canon Drift / Wiki Ingest

## Purpose

This note records a static intake pass for fiction-writing tools that strengthen MuMuAINovel around local author control, canon drift prevention, source-study ingestion, continuation context, and same-type writing boundaries.

No upstream project was cloned deeply, installed, executed, launched, or connected to providers/runtimes.

## Sources

- `DoktorDaveJoos/manuscript`
  - Observed HEAD: `6e696471279c86055b53c13fae9f3c9166e1f497`
  - License: MIT badge observed in README; no local LICENSE file fetched in this static pass
  - Family: local desktop novelist app / revision workbench / story bible
  - Posture: pattern-only; runtime-deferred desktop app, provider calls, local DB and import/export
- `sadasdfsaf/canonkit`
  - Observed HEAD: `edb8c1ac1747a822da1cd728fbc8c13a8f932e7a`
  - License: no LICENSE file observed in static fetch
  - Family: local-first canon drift checker / focused scene context pack
  - Posture: pattern-only; runtime-deferred browser app and npm build/tests
- `abrahamp47/storyforge-wiki`
  - Observed HEAD: `e05622343ee2999cef2d547465a28a92f9c673f6`
  - License: MIT
  - Family: story bible/worldbuilding wiki ingest, lint, graph, and publish workflow
  - Posture: pattern-only; runtime-deferred Claude Code commands, Python tools, and Quartz publish

## Absorbed Patterns

### Local desktop manuscript revision/bible gate

- Keep local manuscript state, author notes, AI-generated descriptions, and Story Bible entries separately labeled.
- Use granular accept/reject diff review for AI prose suggestions.
- Treat local SQLite, semantic search, style analysis, import/export, and provider-backed features as runtime-deferred.

### CanonKit local canon-drift context-pack gate

- Detect canon drift across character cards, ages/years, rules, locations, scenes, and continuity state before drafting.
- Build focused-scene LLM context packs from accepted canon only.
- Record JSON import/export and local-first storage boundaries.

### Storyforge wiki ingest/lint/graph gate

- Separate raw manuscript/lore ingestion from generated wiki pages.
- Run health/lint/query/graph style checks after ingest batches.
- Use chunked map-reduce extraction traces for long manuscript files and keep Quartz/publication as a later gate.

## Runtime-Deferred Gates

The following remain blocked until a separate local safety contract names scope, files, providers, outputs, reviewer, cleanup, and rollback:

- Desktop app launch, AI provider use, local SQLite access, file import/export, semantic search, style analysis, and generated Story Bible writes from Manuscript.
- CanonKit npm build/tests, browser persistence, demo/runtime use, JSON import/export, or local project storage access.
- Storyforge Claude Code slash commands, Python lint/sync tools, raw manuscript ingestion, generated wiki writes, graph rebuilds, Quartz sync, and GitHub Pages publishing.

## MuMuAINovel Mapping

- `local_desktop_manuscript_revision_bible_gate`
  - Adds local Story Bible/revision workbench, accept/reject diff, AI extraction review, and author-control hints.
- `canonkit_local_canon_drift_context_pack_gate`
  - Adds canon drift context-pack policy, focused-scene handoff findings, and JSON boundary hints.
- `storyforge_wiki_ingest_lint_graph_gate`
  - Adds wiki ingest/lint/graph policy, canon conflict query findings, and map-reduce extraction trace hints.

## Scratch Evidence

Static scratch artifacts were written under:

```text
tmp/source-intake-20260612-next-local-editor-canon/
```

The scratch directory contains public search notes, `git ls-remote` HEAD records, and raw README/LICENSE files used for marker review.

## Verification

Expected validation:

```text
python -m py_compile backend/app/services/source_discovery_service.py backend/app/services/source_pattern_pack_prompt.py backend/tests/services/test_source_discovery_service.py backend/tests/frontend/test_source_discovery_panel_copy.py
python -m pytest backend/tests/services/test_source_discovery_service.py::test_local_desktop_canonkit_wiki_sources_are_static_absorbed -q
python -m pytest backend/tests/frontend/test_source_discovery_panel_copy.py -q
python -m pytest backend/tests/services/test_source_discovery_service.py -q
npm --prefix frontend run build
git diff --check
```
