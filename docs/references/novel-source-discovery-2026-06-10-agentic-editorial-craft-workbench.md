# Novel Source Discovery - 2026-06-10 Agentic Editorial / Craft Workbench

## Purpose

Static intake for public GitHub projects that improve MuMuAINovel's ?????
????? and long-form manuscript review workflow.

This pass focuses on agentic editorial handoff, per-chapter state archives,
section metadata traceability, and AI-prose fingerprint clusters. It does not
install or run any external project.

## Safety Boundary

- Quarantine: public metadata, `git ls-remote HEAD`, README/license static read.
- No repository was cloned.
- No package manager, installer, Electron app, Claude Code agent, MCP server,
  scanner, publisher, LibreOffice/OpenOffice add-on, workflow service, model,
  or provider call was executed.
- AGPL/GPL/uncertain-license projects stay pattern-only.
- Runtime use would require a separate local safety contract covering file
  scope, model/provider calls, external tools, network, cleanup, and rollback.

## Source Snapshot

| Source | Observed HEAD | License | Posture | Absorbed patterns |
|---|---|---|---|---|
| `john-paul-ruf/novel-engine` | `cdb4f33dd4b07e6c52ad001e167cff5c512138e0` | AGPL-3.0 | pattern-only | `agentic_editorial_pipeline_gate` |
| `ThomasHoussin/Claude-Book` | `3fdebbb576b1be6d123b48258d2310c5dff013c4` | MIT | pattern-only | `agentic_editorial_pipeline_gate`, `chapter_state_archive_ladder` |
| `DoktorDaveJoos/manuscript` | `ed61a9a83fade86ed441285c2d33df805e417e72` | not confirmed via GitHub API | pattern-only | `section_metadata_traceability_gate` |
| `geobond13/fiction-forge` | `181a28cfe41c018eef278a00d28be1887ce7ba01` | MIT | pattern-only | `ai_prose_fingerprint_cluster_gate` |
| `shenminglinyi/PlotPilot` | `1c481237b6fa32ef5f85d7f8da4cb16f366cd4f0` | Apache-2.0 + Commons Clause / NOASSERTION | pattern-only | `section_metadata_traceability_gate` |
| `peter88213/novelibre` | `8201f9e5dfd859651a950773791a2783b6cb0ef8` | GPL-3.0 | pattern-only | `section_metadata_traceability_gate` |

## Reusable Patterns

### `agentic_editorial_pipeline_gate`

Separate planning, architecture, drafting, reviewing, copy-editing, and
compilation as explicit handoff stages.

For MuMuAINovel this means:

- continuation context may include reviewer-accepted canon only
- same-type creation should build new-story artifacts before any writer role
  drafts prose
- automated roles propose; author/reviewer acceptance decides canon changes
- role outputs stay inspectable and do not silently become source of truth

### `chapter_state_archive_ladder`

Keep permanent bible and transient per-chapter state separate.

Track:

- permanent bible files and immutable source-derived decisions
- current chapter state pointer
- archived state after every accepted chapter
- state templates and required fields
- timeline/history deltas
- drift between bible, current state, and archived chapter state

This reduces context corruption when long continuation sessions resume after
many generated chapters.

### `section_metadata_traceability_gate`

Every chapter/section should have metadata that can be audited independently
from prose.

Track:

- cast, location, item, faction, and plotline ids
- act, beat, status, pacing, and tension position
- source evidence or transformed-canon evidence
- section-to-timeline and section-to-character-state links
- missing or stale metadata before generation

For same-type creation, source section metadata must be remapped into new cast,
locations, items, plotlines, and beats before drafting.

### `ai_prose_fingerprint_cluster_gate`

Scan long-form drafts for repeated machine-prose fingerprints as clustered
review evidence.

Track:

- voice drift across chapters
- overused punctuation and sentence shapes
- hedging and generic emotional resolution
- show-then-tell patterns
- repeated metaphor or transition clusters
- accepted/ignored exceptions

Findings become targeted revision tasks. They must not auto-rewrite author
voice, invented terms, or same-type independence gates.

## MuMuAINovel Integration

Updated artifacts:

- `backend/app/services/source_discovery_service.py`
- `backend/app/services/source_pattern_pack_prompt.py`
- `backend/app/services/book_remix_context_service.py`
- `backend/app/references/novel-source-pattern-pack-2026-06-10.json`
- `backend/tests/services/test_source_discovery_service.py`
- `backend/tests/services/test_book_remix_context_service.py`

Pattern pack refresh:

- source_candidate_count: 201
- workflow_patterns: 215
- generated_at: 2026-06-10T20:40:00+08:00

## Deferred Runtime Gates

Before any runtime adoption:

- define exact project-local files and scratch paths
- choose whether the stage may call AI providers
- keep source books, transformed canon, and reviewer notes separate
- prohibit MCP/server/editor launch without a local safety contract
- record accepted/ignored scan findings and rollback path
- verify no generated role output becomes canon without reviewer acceptance
