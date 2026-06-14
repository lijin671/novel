# NovelForge version-safe scene/fact projection

Date: 2026-06-14

## Source

- `https://github.com/hayrgpt-rgb/NovelForge-AI`
- Observed default branch: `main`
- Observed HEAD: `48c9bca5e62eefa2dd8365f4a2bf4564b94b546a`
- Discovery channel: GitHub search / static source intake
- License: not observed from root `LICENSE` or `LICENSE.md`

## Posture

- pattern-only
- L1 public metadata and raw README/root marker review only
- no clone, install, Docker, worker, database, provider call, package script,
  prompt-body import, prose import, credential read, or runtime trial

## Absorbed pattern

NovelForge contributes a version-safe authoring custody pattern for long-form
novel generation:

- keep draft, archived, revised, and accepted scene versions traceable
- require fact approval or rejection before facts can update canon memory
- retrieve only the focused facts, memory chunks, reference assets, and state
  required by the current generation or revision pass
- use review reports to catch continuity, motive, and source-boundary defects
  before accepting a scene or chapter
- allow export/manuscript merge only from accepted scene or chapter states

## Local adaptation

`BookRemixContextService` now projects this into remix continuation and same-type
creation contexts as `NovelForge version-safe scene/fact pipeline gate`.

Added control axes:

- `scene_version_lineage`
- `fact_approval_queue`
- `focused_memory_reference_asset_retrieval`
- `continuity_reviewreport_findings`
- `accepted_export_readiness`

Added acceptance steps:

- `verify_scene_version_lineage`
- `approve_fact_extraction_before_memory`
- `verify_reference_asset_retrieval_scope`
- `verify_continuity_reviewreport_findings`

This complements the local `D:/project/universal-novel-writing` chapter-contract
projection: the universal reference defines what a chapter must decide; this
projection defines how scene/fact state becomes accepted canon safely.

## Boundary

Continuation mode may use this gate only against target-owned accepted bible,
plan, chapter packages, and project memory.

Same-type creation may absorb the custody workflow only. It must not reuse
source scene versions, fact memories, reference assets, review reports, prose,
prompts, names, plot order, or runtime behavior.

## Verification

- `python -m pytest backend/tests/services/test_book_remix_context_service.py::test_novelforge_version_safe_scene_fact_pipeline_renders_context_and_audit -q`
