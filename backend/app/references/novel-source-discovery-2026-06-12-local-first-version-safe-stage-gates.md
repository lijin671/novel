# Novel Source Discovery - Local-First Studio, Version-Safe Review, and Stage-Gate Retry Patterns (2026-06-12)

## Scope

Static source intake for MuMuAINovel book deconstruction, continuation, same-type creation, and long-form state safety.
No dependency install, package script, Docker service, browser session, provider call, database migration, Obsidian plugin install, generated chapter import, or local manuscript/runtime execution was performed.
Static review used public GitHub search/`git ls-remote` and shallow scratch clones under `tmp/source-intake-2026-06-12-writeros-continuity-studio/repos`.

## Sources

### YfengJ/novel-studio-ai

- URL: https://github.com/YfengJ/novel-studio-ai
- Reachable HEAD: `90fbf0681e76afe791d11f21edd1fb1516ee5e1d`
- License marker: not observed
- Static markers: local-first AI long-form fiction workbench, Story Bible, Style Bible, five-chapter arc packs, Chapter Studio, Context Pack preview, character states, graph facts, timeline events, local SQLite memory chunks, API-key redaction, drafts do not update canon until chapter acceptance.
- Absorbed pattern: `novel_studio_accepted_chapter_memory_gate`
- Posture: pattern-only.

Reusable lesson:

- Drafting, continuity check, style revision, chapter acceptance, and memory extraction should be separate state transitions.
- Context Pack assembly should be visible and bounded, not hidden in chat history.
- Only accepted chapters may update summaries, character states, graph facts, timeline events, and memory chunks.

### hayrgpt-rgb/NovelForge-AI

- URL: https://github.com/hayrgpt-rgb/NovelForge-AI
- Reachable HEAD: `48c9bca5e62eefa2dd8365f4a2bf4564b94b546a`
- License marker: not observed
- Static markers: idea-to-export durable pipeline, story bible, outlines, scene cards, scene draft, fact extraction, review, revision, memory update, scene versions, side-by-side version viewing, human review queue, continuity state, Story State ledger, no silent overwrite of accepted prose or canon.
- Absorbed pattern: `novelforge_version_safe_human_review_gate`
- Posture: pattern-only.

Reusable lesson:

- AI output should enter as candidate versions with provenance, proposed facts, continuity warnings, and review status.
- Human review, fact approval, continuity-state update, and prose acceptance should remain separate approvals.
- Version-safe workflows are stronger than direct replacement when doing续写 and仿写 revisions.

### ironharvy/unorthodox-writer

- URL: https://github.com/ironharvy/unorthodox-writer
- Reachable HEAD: `a1ada4cb5a11b931832b3e90cfcec787b969a7e2`
- License marker: not observed
- Static markers: Pipeline Stage Gates, canonical bible digest, rolling synopsis, previous-tail continuity, per-stage quality gates, self-review, external review, AI artifact scan, retry only the failed stage, canon drift checks, final manuscript metrics.
- Absorbed pattern: `unorthodox_pipeline_stage_retry_gate`
- Posture: pattern-only.

Reusable lesson:

- Each pipeline stage needs its own accept/retry/abort criteria.
- Continuation needs both a rolling synopsis and previous-ending tail, plus overlap and contradiction checks.
- Retrying only the failed stage avoids broad regeneration that damages accepted continuity.

### angel1411337-del/WriterOS

- URL: https://github.com/angel1411337-del/WriterOS
- Reachable HEAD: `22808f4b6e54d370ec8c90ffe3e50885d9f32ada`
- License marker: proprietary / source-available for portfolio viewing only; not open source.
- Static markers: commercial continuity engine, specialized validators Architect / Profiler / Psychologist / Navigator / Mechanic, canon layer management, retcons and alternate timelines, Obsidian validation tools, local-first Docker architecture, PostgreSQL + pgvector, 500,000+ word manuscripts.
- Absorbed pattern: `writeros_role_validator_boundary_gate`
- Posture: reference-only / pattern-only with proprietary boundary.

Reusable lesson:

- Long-form continuity review benefits from specialized validator roles by domain.
- Plot structure, entity graph, psychology arc, spatial/travel logic, and rules mechanics should produce separate findings.
- Proprietary/source-available sources can inform abstract review dimensions only; code, schemas, plugins, and runtime behavior stay excluded.

## MuMuAINovel integration

Updated source-discovery surfaces:

- default GitHub queries for accepted-chapter memory, version-safe human review, and pipeline stage retry patterns
- default repository seeds for all four sources
- static repository summaries with runtime-deferred and license-boundary notes
- pattern keyword detection for four gates
- pattern-pack fields:
  - `novel_studio_accepted_chapter_memory_gate_hints`
  - `novelforge_version_safe_human_review_gate_hints`
  - `unorthodox_pipeline_stage_retry_gate_hints`
  - `writeros_role_validator_boundary_gate_hints`
- bible enrichment targets:
  - `accepted_chapter_memory_writeback_policy`
  - `context_pack_canon_separation_policy`
  - `version_safe_scene_candidate_policy`
  - `human_review_queue_canon_policy`
  - `stage_gate_retry_budget_policy`
  - `rolling_synopsis_tail_continuity_policy`
  - `specialized_role_validator_policy`
  - `proprietary_reference_only_boundary_policy`
- whole-book analysis targets:
  - `accepted_chapter_memory_report`
  - `context_pack_preview_trace`
  - `graph_fact_continuity_findings`
  - `version_safe_scene_candidate_report`
  - `human_review_queue_trace`
  - `story_state_ledger_findings`
  - `pipeline_stage_gate_report`
  - `rolling_synopsis_tail_overlap_findings`
  - `retry_budget_artifact_scan`
  - `role_validator_boundary_report`
  - `canon_drift_layer_findings`
  - `proprietary_reference_review`
- inspired creation remap targets:
  - `accepted_chapter_memory_remap`
  - `version_safe_review_remap`
  - `stage_gate_retry_remap`
  - `specialized_validator_role_remap`

## Runtime exclusions

Still blocked unless a separate local safety contract exists:

- npm/pnpm install, postinstall, Next.js or frontend runtime, browser/sessionStorage key use
- FastAPI/Redis/RQ/PostgreSQL/SQLite runtime, migrations, Docker Compose
- provider/model calls, API-key use, generated prose import, user manuscript ingestion
- Obsidian plugin install, WriterOS code/schema import, vector index/database launch
- external review execution, local scripts, overwrite-oriented revision commands

## Verification anchors

Expected local verification after integration:

```text
python -m py_compile backend/app/services/source_discovery_service.py backend/app/services/source_pattern_pack_prompt.py backend/tests/services/test_source_discovery_service.py backend/tests/frontend/test_source_discovery_panel_copy.py
python -m pytest backend/tests/services/test_source_discovery_service.py::test_local_first_version_safe_and_stage_gate_sources_are_static_absorbed -q
python -m pytest backend/tests/frontend/test_source_discovery_panel_copy.py -q
```
