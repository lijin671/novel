# 2026-06-12 NovelForge AI 深层静态吸收记录

## Source

- URL: <https://github.com/hayrgpt-rgb/NovelForge-AI>
- Observed HEAD: `48c9bca5e62eefa2dd8365f4a2bf4564b94b546a`
- Default branch: `main`
- GitHub API license: none observed
- Posture: `pattern-only`

## Public evidence used

- GitHub repository metadata, default-branch HEAD, root tree names, and selected raw Markdown docs.
- Read files: `README.md`, `SOURCE_NOVEL_ANALYSIS.md`, `NOVEL_FUSION_ENGINE.md`, `ORIGINALITY_GUARDRAILS.md`, `PRECISION_EDITING.md`, `QUALITY_GATES.md`.
- No clone, no Docker, no package manager, no backend/frontend start, no database/queue launch, no provider/model call, no `.env` read.

## Reusable patterns

- `source_novel_dna_fusion_boundary_gate`: keep source chunks in the source-analysis layer only. Downstream fusion reads abstract `SourceNovelAnalysis`, `NovelDNA`, `FusionBlueprint`, taboo terms, and risk metadata. The writing layer must not receive raw source chunks or source scene summaries.
- `originality_guard_project_creation_gate`: rerun originality checks before project creation. Rights status, taboo terms, forbidden similarity terms, raw-source markers, and high/critical risk block project creation instead of becoming later draft warnings.
- `precision_edit_candidate_version_gate`: selected-passage edits create explicit candidate records with replacement text, change summary, style notes, warnings, and apply/reject decision. Applying a candidate creates a new `SceneVersion`; the source version remains auditable.

## Deferred/runtime gates

- Do not import upstream code because no license file is observed.
- Do not run Docker Compose, PostgreSQL, Redis, RQ, scripts, backend, frontend, provider calls, or OpenAI-compatible configuration.
- Do not ingest or store upstream prompts, source chunks, `.env` data, raw-source excerpts, or generated drafts.

## Project update

- Expanded static pattern detection for `SourceNovelAnalysis`, `NovelDNA`, `FusionBlueprint`, originality guardrails, and precision-edit candidate workflows.
- Added prompt-pack hints for source-analysis/fusion/writing layer separation, project-creation originality gates, selected-passage precision edits, and same-type copy-risk checks.
- Added source-intake search coverage for `SourceNovelAnalysis`, `NovelDNA`, `FusionBlueprint`, and `OriginalityGuard`.

## Verification

- `python -m pytest backend/tests/services/test_source_discovery_service.py::test_static_novelforge_ai_source_adds_versioned_scene_fact_review_pipeline_gate -q`
- `python -m pytest backend/tests/services/test_source_discovery_service.py -q`
- `python -m pytest backend/tests/services/test_chapter_guardrails_rewrite.py backend/tests/api/test_chapter_analysis_remix_sync.py backend/tests/frontend/test_chapters_page_copy.py -q`
- `git diff --check`
