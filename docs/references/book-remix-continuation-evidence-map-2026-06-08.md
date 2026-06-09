# Book Remix Continuation Evidence Map - 2026-06-08

## Scope

This note captures local evidence for improving MuMuAINovel BookRemix continuation / inspired-creation workflows.
It is a repository-native knowledge artifact, not an implementation plan.

Safety posture:

- Evidence was gathered from local repository files and already-downloaded `tmp/` source-intake artifacts.
- No external repository was cloned, installed, imported, or executed in this collection pass.
- Upstream projects remain pattern-only unless a separate trust / license / runtime review is performed.
- Current functional implementation for stable `beat_id` / `hook_id` lives on the local branch `feature/book-remix-continuation-id-state-loop-20260608`.

## Evidence Sources

### Local BookRemix Implementation

Primary files inspected:

- `backend/app/services/book_remix_bible_service.py`
- `backend/app/services/book_remix_continuation_plan_service.py`
- `backend/app/services/book_remix_continuation_state_service.py`
- `backend/app/services/book_remix_context_service.py`
- `backend/app/services/book_remix_service.py`
- `backend/app/api/book_remix.py`
- `frontend/src/pages/BookRemix.tsx`
- `frontend/src/components/book-remix/`

Observed capabilities:

- Continuation bible draft generation from source chapters, analysis snapshots, and public pattern-pack digest.
- Bible core backfill for timeline, foreshadows, hard constraints, and style signature.
- Continuation plan generation from confirmed bible and recent `chapter_change_packages`.
- Immediate generated-chapter state commit via `commit_generated_chapter()`.
- Later chapter-analysis sync via `sync_chapter_analysis()`.
- Prompt context assembly from confirmed bible, current plan, chapter change packages, open hooks, resolved hooks, and whole-book progression.
- Analysis coverage and missing-analysis startup endpoints.
- Frontend panels for bible review, continuation plan, context preview, progress summary, source discovery, and chapter change package audit.

### Local Implemented Branch

Local branch:

- `feature/book-remix-continuation-id-state-loop-20260608`

Worktree:

- `C:/Users/zhouzx/.config/superpowers/worktrees/MuMuAINovel/feature/book-remix-continuation-id-state-loop-20260608`

Commits:

- `dcf662e chore: add book remix baseline files`
- `7d54828 feat: add id-aware book remix continuation state sync`

Validation evidence:

- `python -m pytest tests/services/test_book_remix_continuation_plan_service.py tests/services/test_book_remix_continuation_state_service.py -q` -> `26 passed`
- `python -m pytest tests/services/test_book_remix_context_service.py tests/services/test_chapter_generation_prompt_remix_context.py -q` -> `33 passed`

What the branch adds:

- Stable `beat_id` normalization for plan beats.
- Stable `hook_id` normalization for priority hooks.
- ID-first plan beat sync from chapter analysis.
- ID-first hook resolution sync from chapter analysis.
- ID-bearing `plan_progress` and `foreshadow_changes` in chapter change packages.
- Text-overlap fallback for older no-ID data.

### `voocel/ainovel-cli` Source Intake

Local paths:

- `tmp/source-intake-ainovel-cli/README.md`
- `tmp/source-intake-ainovel-cli/docs/context-management.md`
- `tmp/source-intake-ainovel-cli/internal/tools/commit_chapter.go`
- `tmp/source-intake-ainovel-cli/internal/tools/check_consistency.go`
- `tmp/source-intake-ainovel-cli/internal/tools/novel_context.go`
- `tmp/source-intake-ainovel-cli/internal/tools/novel_context_builders.go`
- `tmp/source-intake-ainovel-cli/internal/store/checkpoints.go`
- `tmp/source-intake-ainovel-cli/internal/store/progress.go`

Absorbable patterns:

- Step-level checkpoints: every tool success appends a checkpoint; recovery can resume at `plan / draft / check / commit` granularity.
- Commit saga: `commit_chapter` writes final chapter, summary, timeline, foreshadow, relationship/state changes, progress, and checkpoint as one guarded workflow.
- Pending commit recovery: a crash mid-commit records stage and resume data.
- Fact-only tools: tools return structured JSON facts, not instruction strings.
- Writer context envelope: current chapter outline, chapter plan/contract, recent summaries, foreshadow ledger, relationship state, character snapshots, style rules, pending reviews.
- Store-summary compaction: when context pressure grows, prefer persisted story-state summaries before LLM full summary.
- Restore pack / handoff pack: after compression or recovery, inject a structured pack with chapter plan, character state, foreshadows, style constraints, and pending review lessons.
- Arc/volume rolling planning: avoid planning all chapters upfront; maintain compass, current arc detail, and expand future arcs at boundaries.
- Related chapter recall: recommend historical chapters from foreshadow, character appearance, state-change, and relationship dimensions.
- Seven-dimensional review: consistency, character, pacing, continuity, foreshadow, hook, aesthetic quality.
- User steering loop: accept live intervention, estimate impact scope, and route to rewrite/polish/review.

### Local BookRemix BanDao Test Artifacts

Local paths:

- `tmp/book-remix-test-ban-dao-20260530/continuation_bible_draft.json`
- `tmp/book-remix-test-ban-dao-20260530/continuation_plan_to_1000.json`
- `tmp/book-remix-test-ban-dao-20260530/full_continuation_pack/full_pack_quality_audit.json`
- `tmp/book-remix-test-ban-dao-20260530/full_continuation_pack_ai_real/real_ai_regression_audit_report.json`
- `tmp/book-remix-test-ban-dao-20260530/full_continuation_pack_ai_real/manual_intervention_notes.json`
- `tmp/book_remix_evidence_extract_20260608/bandao_artifact_summary.json`
- `tmp/book_remix_evidence_extract_20260608/ainovel_structural_hits.md`

Observed evidence:

- Local continuation scenario covered source chapters `1-200`, target chapters `201-1000`, and 800 generated continuation chapters in real-AI audit output.
- Regression audit passed for 800 chapters with machine gates for minimum word count, key characters, stage timeline anchors, organization boundaries, and forbidden roster rewrites.
- Qualitative anchor audit checked chapters `201`, `231`, `381`, `561`, `651`, `761`, `861`, and `1000`, with minimum checked word count `10375`.
- Manual intervention note shows a temporary regression-anchor patch at chapter `231` later resolved by real-AI regeneration.

Absorbable patterns:

- Stage-level gate matrix: each chapter belongs to a stage range/title and inherits required terms / forbidden hits.
- Machine gate vs literary review separation: regression gates catch structural violations but do not replace human quality review.
- Manual intervention ledger: record temporary patches and require real regeneration overwrite before final completion.
- Long-run artifact manifest: keep summary, quality audit, completion audit, word-count summary, and manual intervention notes together.

### Source Discovery / Inspired Creation Ledger

Local docs:

- `docs/references/novel-source-discovery-2026-06-08.md`
- `docs/references/novel-source-discovery-2026-06-08-github-inspired-patterns.md`

Relevant posture:

- Public candidates are pattern-only or index-plus-pattern.
- Inspired creation must keep fields separate from continuation semantics.
- Inspired creation should use source material as style / genre mechanics only.
- Copy-risk review must reject source names, proper nouns, scene order, set-piece sequence, and distinctive wording.
- Continuation and inspired creation can share style-fidelity gates, but not canon state.

## Current BookRemix Architecture Readout

### Canon State Loop

Current loop shape:

1. Source TXT import creates source chapters and a BookRemix task.
2. Bible service creates a draft continuation bible.
3. User confirms bible.
4. Plan service generates a continuation plan.
5. User confirms plan.
6. Chapter generation prompt receives confirmed bible/plan context.
7. `commit_generated_chapter()` immediately writes a generated-chapter checkpoint into bible/plan state.
8. Chapter analysis later upgrades generated evidence into richer `chapter_analysis` packages.
9. Context service de-duplicates generated packages when analysis exists, while preserving guardrail metadata.

Strengths:

- Immediate commit prevents next chapter from writing blind before analysis finishes.
- Context block now summarizes whole-book continuation progress.
- Analysis coverage endpoints expose missing sync coverage.
- Frontend has preview/audit panels, reducing invisible prompt-state risk.

Risks / gaps:

- State transitions are implicit JSON updates, not a durable step-level checkpoint log.
- Generated-chapter commit is not yet a full saga with resumable stages.
- Context health is not surfaced as a compact diagnostic like `loaded sections / warnings / package count / stale plan`.
- Long-run stage gates from BanDao artifacts are not generalized into reusable regression gate templates.
- Manual intervention is not first-class; temporary patch / regeneration-overwrite workflow is not represented in the model.
- Related-chapter recall is not yet multidimensional; current prompt context is mostly bible/plan/package aggregation.

### Prompt Context Loop

Current context service already supports:

- Source pattern-pack section.
- World rules, hard constraints, character continuity cards, organizations, style signature.
- Timeline anchors and story arcs.
- Whole-book continuation progress from `chapter_change_packages`.
- Open/resolved hooks.
- Pending/done planned beats.
- Plan guardrails.
- Inspired context blocks that do not use continuation canon semantics.

Potential enhancement:

- Add a small machine-readable `context_health` section with package range, missing sections, stale-plan flag, source pattern pack loaded flag, and confidence warnings.
- Include ID-bearing beat/hook progress once the local feature branch lands in main.
- Add related chapter recall blocks keyed by active hook IDs, character IDs/names, state-change names, and plan beat IDs.

## Recommended Next Implementation Slices

### Slice 1: Context Health Diagnostics

Goal:

- Make missing / stale / partial remix context visible before generation.

Candidate outputs:

- Backend context preview returns `context_health` with:
  - `bible_confirmed`
  - `plan_confirmed`
  - `plan_current_for_bible`
  - `chapter_change_package_count`
  - `package_chapter_range`
  - `source_pattern_pack_loaded`
  - `missing_sections`
  - `warnings`
- Frontend context preview panel highlights warnings.

Why next:

- Low-risk, mostly read-only.
- Directly addresses historical concern: empty or weak remix context is not obvious to users.

### Slice 2: Stage Gate / Regression Gate Templates

Goal:

- Convert BanDao audit lessons into reusable continuation QA gates.

Candidate fields:

- `stage_id`
- `stage_range`
- `required_terms`
- `forbidden_terms`
- `timeline_anchors`
- `organization_boundaries`
- `minimum_word_count`
- `manual_review_required`

Why next:

- Local artifact evidence shows this gate caught large-run structural risks.
- It fits existing `guardrail_check` and `chapter_change_packages` without new runtime dependencies.

### Slice 3: Manual Intervention Ledger

Goal:

- Represent temporary fixes, user steering, and regeneration overwrite requirements.

Candidate fields:

- `intervention_id`
- `chapter_number`
- `reason`
- `temporary_patch_path` or note
- `required_resolution`
- `status`
- `resolved_by_chapter_id`
- `resolved_at`

Why next:

- BanDao artifacts show manual intervention was necessary and should be auditable.
- This supports long-running agent work without hiding hand patches.

### Slice 4: Step-Level Continuation Checkpoints

Goal:

- Bring `ainovel-cli` step-level recovery into BookRemix generation/sync.

Candidate events:

- `context_built`
- `chapter_generated`
- `generated_state_committed`
- `guardrail_checked`
- `analysis_queued`
- `analysis_synced`
- `context_preview_refreshed`

Why next:

- Current state loop is useful but not fully replayable.
- Checkpoints can be persisted in existing JSON packages first, before a dedicated table.

### Slice 5: Related Chapter Recall

Goal:

- Improve long continuation coherence by adding targeted recalls rather than only global bible/plan context.

Candidate recall dimensions:

- Active `hook_id` / hook text.
- Character name and latest state update.
- Relationship state.
- Plan beat ID.
- Recent failed guardrail dimensions.

Why next:

- Directly absorbs `ainovel-cli` related-chapter recommendation pattern.
- Works naturally after stable beat/hook IDs are integrated.

### Slice 6: Arc / Volume Rolling Plan

Goal:

- Avoid brittle 800+ chapter all-at-once plans; maintain stage/arc windows that can be expanded at boundaries.

Candidate fields:

- `compass`
- `current_stage`
- `future_stage_skeletons`
- `stage_expansion_status`
- `stage_review_summary`
- `next_stage_trigger`

Why later:

- Higher design impact.
- Should follow stable checkpoints and context health so expansion is auditable.

## Open Questions

- Should BookRemix keep using JSON columns only for these next slices, or introduce a small event/checkpoint table once replayability becomes important?
- Should stage gate templates live inside continuation plan JSON, bible JSON, or separate project-level settings?
- Should manual intervention be a user-facing panel first, or a backend audit artifact first?
- Should related chapter recall reuse existing `PlotAnalysis` rows only, or add lightweight inverted indexes for hooks / characters / state changes?

## Current Recommendation

Recommended next code slice after local ID-state-loop branch is integrated:

1. Add `context_health` diagnostics to context preview and prompt-context metadata.
2. Then add reusable stage/regression gate templates using BanDao audit evidence.
3. Then add manual intervention ledger before attempting full step-level checkpoint recovery.

Rationale:

- `context_health` is low-risk and immediately improves operator trust.
- Stage gates convert proven local artifacts into reusable safety checks.
- Manual intervention ledger prevents hidden patch debt before adding more automation.
