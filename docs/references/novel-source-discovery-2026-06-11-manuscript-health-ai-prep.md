# Novel Source Discovery - Manuscript Health / AI Preparation Gates

Date: 2026-06-11

## Source

- Repository: `https://github.com/DoktorDaveJoos/manuscript`
- Observed HEAD: `c88bd26053454478cf099497936045596854783c`
- Metadata source: GitHub public API, 2026-06-11
- GitHub `updated_at`: `2026-06-10T17:49:04Z`
- Stars observed: `5`
- License: no license object observed
- Topics: `literature`, `novels`, `writing`, `writing-tool`

## Family

Novel-writing workbench / local-first manuscript analysis / AI preparation.

## Posture

`pattern-only`.

The source is useful for durable craft and workflow patterns, not for runtime
adoption. The license is missing, and the project describes a multi-surface
desktop stack with local files, semantic chunking, RAG, agent folders, MCP
configuration, scripts, embeddings, and provider-facing AI preparation.

## Static README Markers

- manuscript health score
- Story Heartbeat Canvas
- Plot Health Dashboard
- chapter ending analysis
- AI preparation pipeline
- semantic chunks with overlap
- story bible population
- style extraction
- RAG
- error recovery
- circuit breaker protection

## Reusable Patterns

1. Track manuscript-health trends across accepted chapters.
   The score should expose hook quality, pacing, tension, emotional arc, and
   craft issues as trend evidence rather than one-off subjective notes.

2. Classify chapter endings before continuation.
   Useful ending classes are `cliffhanger`, `soft hook`, `closed`, and
   `dead end`. A dead-end class should require a repair plan or an explicit
   quiet-chapter exception.

3. Treat AI preparation as a resumable phase pipeline.
   The durable state should include semantic chunks, retrieval/index state,
   chapter analysis, story-bible population, style extraction, recovery state,
   and circuit-breaker status.

4. For same-type creation, remap health axes and ending taxonomy.
   The new book should have its own tension curve, pacing debt, hook debt,
   heartbeat curve, and recovery trace. It must not preserve the source
   chapter-ending class sequence or source recovery route.

## Artifacts Updated

- `backend/app/services/source_discovery_service.py`
- `backend/app/services/source_pattern_pack_prompt.py`
- `frontend/src/types/sourceDiscovery.ts`
- `frontend/src/components/book-remix/BookRemixSourceDiscoveryPanel.tsx`
- `backend/tests/services/test_source_discovery_service.py`

## Runtime Exclusions

No install, clone checkout, package manager, Laravel/PHP/Node runtime, desktop
app launch, script execution, MCP/server launch, browser/desktop control,
embedding generation, local manuscript ingestion, provider call, credential
read, or local file import was performed or authorized.

## Verification Target

The project-local pattern pack should expose:

- `manuscript_health_ai_prep_gate`
- `manuscript_health_ai_prep_gate_hints`
- `manuscript_health_score_axes`
- `chapter_ending_taxonomy`
- `ai_preparation_phase_policy`
- `manuscript_health_score_timeline`
- `story_heartbeat_canvas_report`
- `chapter_ending_classification_report`
- `ai_preparation_recovery_trace`
- `chapter_ending_taxonomy_remap`
