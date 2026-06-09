# BookRemix Context Health and Gate Evidence - 2026-06-08

## Purpose

This document continues the evidence-only collection requested by the user. It focuses on the next likely implementation slice:

1. `context_health` diagnostics for BookRemix continuation context preview.
2. Generic stage / regression gate design based on existing guardrail and BanDao evidence.
3. How these should reuse current coverage/risk/review structures rather than duplicate them.

No runtime behavior is changed by this document.

## Current Context Preview Evidence

Files:

- `backend/app/services/book_remix_context_service.py`
- `backend/app/schemas/book_remix.py`
- `frontend/src/types/bookRemixBible.ts`
- `frontend/src/components/book-remix/BookRemixContinuationContextPreviewPanel.tsx`
- `backend/tests/services/test_book_remix_context_service.py`
- `backend/tests/api/test_book_remix_bible_api.py`

Current preview response fields:

```json
{
  "project_id": "...",
  "has_context": true,
  "context": "...",
  "context_length": 1234,
  "lineage_confirmed": true,
  "reason": null,
  "source_pattern_pack_loaded": true
}
```

Existing blocker reasons surfaced by frontend:

- `remix_bible_not_found`
- `durable_remix_lineage_missing`
- `continuation_plan_not_found`
- `remix_bible_not_confirmed`
- `continuation_plan_not_confirmed`
- `continuation_plan_not_bound_to_current_bible`
- `continuation_plan_stale_against_bible`
- `empty_context`

Evidence from tests:

- `test_get_continuation_context_preview_returns_actual_prompt_context()` verifies the preview returns the exact prompt block, includes whole-book progress, and marks lineage confirmed.
- `test_get_continuation_context_preview_explains_unconfirmed_or_stale_lineage()` verifies the preview explains a draft plan as `continuation_plan_not_confirmed` instead of only returning an empty block.
- `test_build_project_context_preview_loads_latest_pattern_pack()` verifies preview reflects fresh source pattern pack loading.
- `test_build_project_context_block_ignores_stale_confirmed_plan()` verifies stale confirmed plans produce no context.

Conclusion:

- The preview endpoint is the lowest-risk place to add `context_health` because it already returns readiness metadata and has frontend display space.
- `context_health` should not change prompt behavior initially.
- It should be derived from the same Bible/Plan/package data used by `build_project_context_block()`.

## Existing Analysis Coverage / Continuation Risk Evidence

Files:

- `backend/app/services/book_remix_service.py`
- `backend/app/schemas/book_remix.py`
- `frontend/src/types/bookRemixBible.ts`
- `backend/tests/api/test_book_remix_bible_api.py`

Current coverage response fields:

```json
{
  "project_id": "...",
  "source_chapter_count": 3,
  "source_chapters_count": 3,
  "analyzed_chapter_count": 2,
  "chapter_change_package_count": 1,
  "analysis_coverage_percent": 67,
  "change_package_coverage_percent": 33,
  "fully_analyzed": false,
  "fully_synced": false,
  "missing_source_chapters": [],
  "missing_analysis_chapters": [],
  "missing_change_package_chapters": [],
  "analysis_action_plan": [],
  "continuation_risk": {}
}
```

Existing `continuation_risk` fields:

- `level`: `low | medium | high`
- `label`
- `can_continue`
- `blocking_chapter_numbers`
- `warning_chapter_numbers`
- `reasons`
- `reason_labels`
- `message`

Evidence from tests:

- `test_get_analysis_coverage_reports_missing_analysis_and_change_packages()` verifies coverage percents and missing analysis/change-package chapter lists.
- `test_get_analysis_coverage_counts_generated_packages_as_continuation_context()` verifies generated chapter packages count as continuation context for sync coverage.
- `test_get_analysis_coverage_stays_high_risk_when_generated_package_lacks_source_analysis()` verifies generated packages do not hide source-analysis gaps.
- `test_get_analysis_coverage_ignores_generated_continuation_chapters_after_source_range()` verifies generated continuation chapters after source range are ignored when auditing source-book coverage.
- `test_get_analysis_coverage_returns_action_plan_for_whole_book_gaps()` verifies action plan grouping:
  - `restore_source_chapter`
  - `sync_existing_analysis`
  - `wait_running_analysis`
  - `fill_chapter_content`
  - `queue_analysis`
- `test_get_analysis_coverage_reports_continuation_risk_summary()` verifies high-risk blocking message with source chapter missing / analysis missing / change package missing reasons.
- `test_get_analysis_coverage_blocks_unsynced_existing_analysis()` verifies existing `PlotAnalysis` without change package remains a blocking risk.

Conclusion:

- `context_health` should not duplicate the full coverage endpoint.
- It can reference a compact subset, e.g. `analysis_risk_level`, `analysis_can_continue`, `coverage_warning_count`, or a link/action hint.
- Full remediation remains owned by `/analysis-coverage` and `/analysis/start-missing`.

## Current Context Block Content Evidence

`build_remix_continuation_context_block()` already renders:

- hard constraints;
- character anchors;
- timeline anchors;
- story arcs;
- active foreshadows;
- style signature;
- recent chapter change packages;
- whole-book continuation progress;
- plan summary;
- pending/done beats;
- pending/done hooks;
- plan guardrails;
- source-discovered guidance.

Evidence from tests:

- `test_build_remix_continuation_context_block_renders_recent_change_packages_before_done_state()` verifies recent change packages render before pending state.
- `test_build_remix_continuation_context_block_summarizes_whole_book_progress_from_change_packages()` verifies range, timeline progression, latest character states, resolved/open hooks, and completed plan beats.
- `test_build_remix_continuation_context_block_deduplicates_legacy_generation_and_analysis_packages()` verifies legacy generation + analysis package duplication is handled.
- `test_build_remix_continuation_context_block_preserves_generation_guardrail_when_analysis_wins()` verifies guardrail metadata from generation is preserved even when analysis wins for state.
- `test_build_remix_continuation_context_block_renders_emotional_arc_from_change_package()` verifies emotional progression can enter the context.

Minimal `context_health` fields suggested by current evidence:

```json
{
  "status": "ready | warning | blocked",
  "loaded_sections": [
    "hard_constraints",
    "character_cards",
    "timeline",
    "foreshadows",
    "plan_beats",
    "priority_hooks",
    "chapter_change_packages",
    "source_pattern_pack"
  ],
  "missing_sections": [],
  "package_count": 2,
  "package_range": {"start": 19, "end": 20},
  "pending_beat_count": 1,
  "pending_hook_count": 2,
  "source_pattern_pack_loaded": true,
  "lineage_reason": null,
  "warnings": [],
  "loading_summary": "bible:confirmed plan:confirmed packages:2 range:19-20 beats:1 hooks:2 source_pack:ok"
}
```

Recommended status logic for a first slice:

- `blocked` when preview already has `has_context=false` or a lineage blocker reason.
- `warning` when context exists but important sections are empty, e.g. no change packages, no plan beats, no hard constraints, no source pattern pack.
- `ready` when context exists and no warnings.

Do not include large lists in `context_health`; keep it as metadata.

## ainovel-cli Context Evidence

Reference files:

- `tmp/source-intake-voocel-ainovel-cli-20260529/internal/tools/novel_context.go`
- `tmp/source-intake-voocel-ainovel-cli-20260529/internal/tools/novel_context_builders.go`

Relevant patterns:

- `novel_context` returns `_warnings` when a context layer cannot be loaded.
- It returns `_loading_summary` after budget trimming.
- Writer path uses a layered envelope:
  - `working_memory`
  - `episodic_memory`
  - `reference_pack`
  - `selected_memory`
- It injects `user_rules` at a stable canonical path.
- It exposes `chapter_draft.exists + word_count` rather than raw draft content.
- It exposes `checkpoint` with `in_progress_chapter`, `strand_history`, and `hook_history`.
- It applies a budget trim and records `_trimmed` keys.
- Its loading summary counts characters, memories, summaries, timeline, foreshadow ledger, relationship state, state changes, previous tail, style rules, related chapters, review lessons, references, memory policy, warnings, and trimmed sections.

Mapping to BookRemix:

- `_warnings` -> `context_health.warnings`
- `_loading_summary` -> `context_health.loading_summary`
- `working_memory` / `episodic_memory` -> current context block sections; do not expose as separate nested JSON yet.
- `related_chapters` -> future recall slice.
- `review_lessons` -> future review compaction slice.
- `_trimmed` -> future prompt budget slice, not needed for the first diagnostic.

## Guardrail Evidence

Files:

- `backend/app/services/chapter_guardrails.py`
- `backend/tests/services/test_chapter_guardrails_rewrite.py`
- `backend/tests/api/test_chapter_analysis_remix_sync.py`
- `frontend/src/types/bookRemixBible.ts`

Reusable violation shape:

```json
{
  "type": "canon_repetition",
  "severity": "high",
  "description": "...",
  "position": 123,
  "context": "..."
}
```

Existing package integration:

```json
{
  "guardrail_check": {
    "applied": true,
    "attempts": 1,
    "initial_passed": false,
    "final_passed": true,
    "violations": [
      {"type": "canon_repetition", "severity": "high"}
    ]
  },
  "changed_sections": ["guardrail_check"]
}
```

Evidence from tests:

- `test_apply_chapter_guardrail_check_rewrites_when_confirmed_canon_is_repeated()` verifies canon repetition is caught and repaired.
- API tests around captured guardrails verify `remix_continuation_context` is passed into guardrail checks.
- API tests verify rewritten guardrail metadata lands in `chapter_change_packages`.

Conclusion:

- Generic stage gates can reuse this violation shape.
- Stage gate violations can be attached as `type="stage_gate"`, `type="missing_required_terms"`, or `type="forbidden_terms"` under existing `guardrail_check.violations`.
- No immediate new frontend audit panel is required because change package types already include `guardrail_check`.

## BanDao Stage Gate Evidence

Files:

- `backend/app/services/bandao_batch_queue_plan.py`
- `backend/app/services/bandao_regression_audit_service.py`
- `backend/tests/services/test_bandao_batch_queue_plan.py`
- `backend/tests/services/test_bandao_regression_audit_service.py`
- `backend/scripts/generate_bandao_full_pack.py`
- `backend/tests/scripts/test_generate_bandao_full_pack_script.py`

Patterns worth abstracting:

- Stage range is parsed from text like `201-230`.
- Stage opening chapters require stricter anchor checks.
- Alias maps reduce false negatives for names and dates.
- Group/stage-specific required terms are only required on relevant chapters, not globally.
- Forbidden term checking compacts whitespace before substring matching.
- The audit report explicitly says machine gates do not replace human literary review.
- The script can run `--regression-audit-only` and raises when regression audit fails.

Do not generalize blindly:

- BanDao names, organizations, real dates, and source hash.
- `201-1000` / `800 chapters` / `10000 words` as universal limits.
- The chapter 201 special case.

Generic gate evidence shape:

```json
{
  "gate_id": "gate-stage-001",
  "scope": "chapter | stage | anchor",
  "chapter_range": {"start": 201, "end": 230},
  "required_terms": [
    {"term": "...", "aliases": ["..."], "required_when": "all | stage_opening | anchor"}
  ],
  "forbidden_terms": [
    {"term": "...", "aliases": ["..."], "match_mode": "compact_substring"}
  ],
  "minimum_word_count": 1000,
  "timeline_anchors": [
    {"label": "...", "aliases": ["..."]}
  ],
  "note": "Machine gate only; does not replace literary review."
}
```

Potential storage homes:

1. `BookRemixContinuationPlan.guardrails`: low migration risk, already list[dict].
2. `BookRemixContinuationPlan.stage_goals`: useful if gates are stage-bound.
3. New plan JSON key `stage_gates`: cleaner but requires schema/model/frontend updates.

Evidence-based recommendation for first implementation:

- Start with `guardrails` entries that optionally carry `gate_type`, `chapter_range`, `required_terms`, `forbidden_terms`, and `minimum_word_count`.
- Add a normalization helper later if the shape stabilizes.
- Evaluate after generation using the same guardrail check pathway.

## Review / Manual Intervention Evidence

Files:

- `backend/app/models/novel_workflow.py`
- `backend/app/services/novel_workflow_service.py`
- `backend/tests/services/test_novel_workflow_unlimited_review_policy.py`
- `tmp/source-intake-voocel-ainovel-cli-20260529/internal/tools/save_review.go`
- `tmp/source-intake-voocel-ainovel-cli-20260529/internal/domain/review.go`

MuMuAINovel already has:

- `ChapterWorkflowResult`
- bounded review rounds with `MAX_SAFE_REVIEW_ROUNDS = 12`
- review aggregate fields for score, pacing, engagement, coherence, style fidelity, reader risk, style drift, must-fix items
- auto-regeneration integration
- BookRemix state commit after auto-regeneration

ainovel-cli adds:

- `save_review` with exact review dimensions;
- required affected chapters when verdict is polish/rewrite;
- checkpoint append after review;
- `review_required` and `review_reason` in `commit_chapter`.

Conclusion:

- First BookRemix review improvement should probably be a compact readout from existing workflow results, not a new review engine.
- Manual intervention needs a new ledger only for user-authored temporary patches / regeneration-overwrite obligations.

## Implementation-Ready Evidence Summary

### Lowest-risk first slice: context health

Why:

- Existing endpoint and frontend panel already exist.
- No new DB table needed.
- No generation behavior change required.
- It addresses the highest current trust gap: silent context degradation.

Likely files:

- `backend/app/services/book_remix_context_service.py`
- `backend/app/schemas/book_remix.py`
- `frontend/src/types/bookRemixBible.ts`
- `frontend/src/components/book-remix/BookRemixContinuationContextPreviewPanel.tsx`
- `backend/tests/services/test_book_remix_context_service.py`
- `backend/tests/api/test_book_remix_bible_api.py`

Suggested tests:

1. Preview returns `context_health.status="blocked"` with lineage blocker reason when plan is draft.
2. Preview returns `context_health.status="warning"` when context exists but no change packages exist.
3. Preview returns `context_health.package_count` and `package_range` when packages exist.
4. Frontend type includes `context_health`; panel shows warning count and package range tags.

### Second slice: generic stage gates

Why after context health:

- Stage gates affect generation/rewrite outcome and require more careful design.
- Existing guardrail tests provide a safe path, but gate storage shape still needs design approval.

Likely files:

- `backend/app/services/chapter_guardrails.py`
- `backend/app/services/book_remix_context_service.py` or plan service if rendering gate metadata
- `backend/app/services/book_remix_continuation_plan_service.py`
- `backend/tests/services/test_chapter_guardrails_rewrite.py`
- `backend/tests/api/test_chapter_analysis_remix_sync.py`

Suggested tests:

1. Stage gate reports missing required term at configured chapter.
2. Stage gate accepts alias term.
3. Stage gate reports forbidden term using compact whitespace matching.
4. Stage gate stores violation under existing `guardrail_check.violations`.
5. Stage gate does not require anchor-only terms on every chapter.

## Open Questions for Next Design Step

1. Should `context_health` include compact analysis coverage info by calling `get_analysis_coverage()`, or should it only summarize local Bible/Plan/package state?
2. Should stage gate metadata live under `plan.guardrails` first, or should a `stage_gates` JSON field be added to the plan?
3. Should generation be blocked on `context_health.status="blocked"`, or should first slice remain preview-only?
4. Should manual intervention ledger live in `chapter_change_packages`, `generation_notes`, or a future separate workflow table?

## Current Recommendation

Proceed next with a preview-only `context_health` design / TDD slice, then gate design. Do not change generation behavior until diagnostics are visible and validated.
