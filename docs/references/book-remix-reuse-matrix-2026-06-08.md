# BookRemix Reuse Matrix: Guardrails, Review, Stage Gates - 2026-06-08

## Purpose

This document records which MuMuAINovel components can be reused for future BookRemix continuation improvements, especially:

- context health diagnostics;
- stage / regression gates;
- review ledger;
- manual intervention / rewrite loop;
- related-chapter recall.

This is evidence collection only. It does not modify runtime behavior.

## Existing Reusable Structures

### 1. Lightweight Chapter Guardrails

Files:

- `backend/app/services/chapter_guardrails.py`
- `backend/tests/services/test_chapter_guardrails_rewrite.py`

Current capabilities:

- Detects empty output.
- Detects chapter-title/meta output at opening.
- Detects recap clichés such as `接上回`.
- Detects omniscient POV cues.
- Detects repetitive opening against continuation point / previous summary.
- Detects canon repetition against BookRemix continuation context.
- Detects inspired-source phrase copying.
- Detects obfuscated forbidden source names.
- Rewrites once via `apply_chapter_guardrail_check()` with a focused repair prompt.
- Outputs a normalized violation shape:
  - `type`
  - `severity`
  - `description`
  - `position`
  - `context`

BookRemix reuse value:

- Stage gate violations should reuse the existing `ChapterGuardrailViolation` shape.
- Existing `guardrail_check` in `chapter_change_packages` already stores guardrail metadata.
- A future stage gate can be added as another guardrail dimension without changing the audit panel shape too much.

Evidence:

- `test_apply_chapter_guardrail_check_rewrites_when_confirmed_canon_is_repeated()` proves BookRemix canon context is already used to prevent replaying completed beats.
- `test_apply_chapter_guardrail_check_injects_source_pattern_pack_into_rewrite_prompt()` proves public source pattern constraints can enter repair prompts.
- `test_chapter_guardrails_flags_obfuscated_forbidden_source_name()` proves forbidden name matching already handles spaced/obfuscated names.

### 2. Workflow Review / Auto-Regeneration Loop

Files:

- `backend/app/models/novel_workflow.py`
- `backend/app/services/novel_workflow_service.py`
- `backend/tests/services/test_novel_workflow_unlimited_review_policy.py`

Current capabilities:

- `NovelWorkflowTask` tracks project-level workflow task state.
- `ChapterWorkflowResult` stores per-chapter workflow review results.
- Review loop is bounded by `MAX_SAFE_REVIEW_ROUNDS = 12`.
- `resolve_review_round_policy()` clamps unsafe/unlimited review requests into a stop-condition policy.
- Review panel collects:
  - overall score;
  - pacing score;
  - engagement score;
  - coherence score;
  - style fidelity score;
  - style drift issues;
  - must-fix items.
- Reader panel collects:
  - immersion score;
  - continue score;
  - favorite points;
  - drop risks;
  - expectations.
- Aggregator revises if:
  - overall score below threshold;
  - two or more revise votes;
  - high-risk issues;
  - high/critical style drift;
  - low style fidelity;
  - low reader score.
- Auto-regeneration writes a new chapter version and can commit regenerated text back into BookRemix state.

BookRemix reuse value:

- Do not build a new review engine from scratch.
- BookRemix-specific review ledger can link or copy summarized `ChapterWorkflowResult.aggregate` fields.
- `style_fidelity` gate is directly relevant to continuation/inspired creation.
- Auto-regeneration already calls `book_remix_continuation_state_service.commit_generated_chapter()` through `_commit_auto_regeneration_to_remix_state()`.

Evidence:

- `test_resolve_review_round_policy_caps_unlimited_request_with_stop_condition()` confirms unlimited review is bounded with explicit stop conditions.
- `test_aggregate_feedback_revises_on_high_style_drift_even_when_scores_pass()` confirms style drift blocks otherwise high-scoring chapters.
- `_commit_auto_regeneration_to_remix_state()` persists workflow-applied regenerated content as a remix checkpoint using `commit_generated_chapter()`.

Gap:

- The review loop is general workflow state, not yet surfaced as BookRemix continuation-specific review history.
- It does not use exactly the `ainovel-cli` seven dimensions, but it has overlapping dimensions and stronger style/reader gates.

### 3. PlotAnalysis as Existing Recall/Sync Source

File:

- `backend/app/models/memory.py`

Current relevant fields:

- `plot_stage`
- `conflict_level`
- `conflict_types`
- `emotional_tone`
- `emotional_intensity`
- `emotional_curve`
- `hooks`
- `foreshadows`
- `plot_points`
- `character_states`
- `scenes`
- `pacing`
- quality scores
- `analysis_report`
- `suggestions`
- `word_count`

BookRemix reuse value:

- `sync_chapter_analysis()` already converts `PlotAnalysis` into BookRemix bible/plan state.
- Related-chapter recall can start from existing `PlotAnalysis` fields before introducing indexes.
- `character_states[].relationship_changes` is already present inside analysis payload comments, even if BookRemix packages do not yet expose relationship changes as a first-class list.

Gap:

- Alias-aware character recall is not available directly in PlotAnalysis.
- There is no separate relationship ledger in BookRemix packages yet.

### 4. BookRemix Chapter Change Packages

Files:

- `backend/app/models/book_remix_bible.py`
- `backend/app/services/book_remix_continuation_state_service.py`
- `backend/app/services/book_remix_context_service.py`
- `frontend/src/types/bookRemixBible.ts`

Current package fields:

- `type`
- `source`
- `chapter_id`
- `chapter_number`
- `chapter_title`
- `summary`
- `timeline_delta`
- `character_state_changes`
- `foreshadow_changes`
- `plan_progress`
- `changed_sections`
- `guardrail_check`
- `emotional_arc`

BookRemix reuse value:

- This is still the best existing home for chapter-level continuation state changes.
- It already bridges generation, analysis, bible sync, plan sync, prompt context, progress summary, and frontend audit.
- Local feature branch adds ID-aware `beat_id` / `hook_id` progress to strengthen traceability.

Gap:

- No explicit `relationship_changes`.
- No explicit `review_result` or `manual_intervention` field.
- No explicit stage gate result fields.

## Existing Specialized Prototype: BanDao Stage Gates

Files:

- `backend/app/services/bandao_batch_queue_plan.py`
- `backend/app/services/bandao_regression_audit_service.py`
- `backend/tests/services/test_bandao_batch_queue_plan.py`
- `backend/tests/services/test_bandao_regression_audit_service.py`

Current capabilities:

- Builds stage-aware continuation expansion plans for chapters `201-1000`.
- Creates draft chapters and continuation outlines for a long batch.
- Records stage range, stage title, stage goals, reality timeline constraints, character focus, target word count, and guardrails.
- Audits generated pack by chapter for:
  - missing chapter file;
  - word count threshold;
  - required terms;
  - aliases for required terms;
  - forbidden terms;
  - stage title/range.
- Writes a full regression audit report.

Evidence patterns worth abstracting:

- Stage range parser: `201-230` -> start/end.
- Stage opening anchors are stricter than ordinary stage chapters.
- Alias map prevents false failures for translated names / date forms.
- Some terms are required only at stage openings or major anchors, not every chapter.
- Forbidden terms check should compact whitespace before matching.
- Audit report separates machine pass/fail from human literary review.

Do not copy directly:

- BanDao-specific names, groups, dates, source SHA, and target chapter counts.
- Fixed `10000` word target as a universal rule.
- Special chapter `201` logic.

Generic stage gate shape suggested by evidence:

```json
{
  "gate_id": "stage-001",
  "scope": "stage | chapter | anchor",
  "chapter_range": {"start": 201, "end": 230},
  "stage_title": "...",
  "required_terms": [
    {"term": "protagonist", "aliases": ["..."], "required_when": "all | stage_opening | anchor"}
  ],
  "forbidden_terms": [
    {"term": "...", "aliases": ["..."], "match_mode": "compact_substring"}
  ],
  "minimum_word_count": 1000,
  "timeline_anchors": [
    {"label": "...", "aliases": ["..."]}
  ],
  "notes": ["Machine gate only; does not replace literary review."]
}
```

## Best Reuse Path by Feature

### Context Health Diagnostics

Reuse:

- `BookRemixContextService.build_project_context_preview()`
- `BookRemixContinuationContextPreviewResponse`
- `BookRemixContinuationContextPreviewPanel`
- `build_remix_continuation_progress_summary()` helpers

Minimal implementation idea:

- Add derived `context_health` object to preview response.
- Include `loading_summary` similar to `ainovel-cli` `_loading_summary`.
- Use existing frontend `Alert` + `Tag` style.

No new DB table needed.

### Stage / Regression Gates

Reuse:

- `ChapterGuardrailViolation` shape.
- `guardrail_check` in chapter change packages.
- BanDao regression audit concepts.
- `BookRemixContinuationPlan.stage_goals` as a possible storage home for stage metadata.

Potential minimal implementation:

- Add optional generic gate list to continuation plan JSON as `stage_gates` or encode in `stage_goals` entries.
- Evaluate gates after generation in the existing guardrail check path.
- Store gate violations under `guardrail_check.violations` with `type="stage_gate"` or more specific types like `missing_required_terms`.

Open design decision:

- Whether to add a schema field (`stage_gates`) or keep it within flexible `stage_goals` JSON until proven.

### Review Ledger

Reuse:

- `NovelWorkflowService` aggregate output.
- `ChapterWorkflowResult` persistence.
- `style_fidelity` gate.
- `revision_brief` construction.
- `commit_generated_chapter()` after auto-regeneration.

Potential minimal implementation:

- Add a BookRemix progress/context summary section that references latest workflow result for generated chapters.
- Do not duplicate all workflow data into BookRemix bible immediately.
- For prompt use, compact to a `review_lessons` block:
  - high-risk issues;
  - style drift issues;
  - reader risks;
  - must-fix list;
  - decision.

Open design decision:

- Whether BookRemix should own a separate review ledger or read from existing workflow tables.

### Manual Intervention Ledger

Reuse:

- `ChapterWorkflowResult.decision`, `revision_brief`, `applied_regeneration` for automatic interventions.
- Existing chapter versions/regeneration task metadata.
- `chapter_change_packages` for continuation-state visibility.

Need new design for:

- User-authored temporary patches.
- Required regeneration overwrite.
- Resolution evidence.

Potential JSON shape:

```json
{
  "intervention_id": "manual-001",
  "chapter_number": 231,
  "reason": "temporary regression anchor patch",
  "status": "open | resolved | superseded",
  "required_resolution": "real_ai_regeneration_overwrite",
  "opened_at": "...",
  "resolved_at": "...",
  "resolved_by_chapter_id": "...",
  "notes": []
}
```

### Related Chapter Recall

Reuse:

- `PlotAnalysis.plot_points`
- `PlotAnalysis.foreshadows`
- `PlotAnalysis.character_states`
- `BookRemixBible.chapter_change_packages`
- plan `beat_id` / hook `hook_id` once local branch lands

Do not require new index initially.

Potential scoring dimensions:

- explicit hook ID match;
- hook text match;
- character state match;
- recent failed guardrail/review lesson;
- stage/beat match.

## Recommended Sequence Updated by Evidence

1. **Context health diagnostics**: lowest risk, mostly derived fields and frontend tags.
2. **Generic stage gate evaluation**: reuse `ChapterGuardrailViolation` and BanDao audit patterns.
3. **Review lesson compaction**: read from existing `ChapterWorkflowResult` rather than creating a new review model.
4. **Manual intervention ledger**: only after review/guardrail outputs are visible.
5. **Related chapter recall**: start read-only from packages/PlotAnalysis; add indexes later if needed.
6. **Step-level checkpoints**: still valuable, but defer DB/event design until the above readouts are visible.

## Evidence-based Cautions

- Do not reimplement a parallel review engine for BookRemix; existing workflow service already handles bounded review and auto-regeneration.
- Do not make every stage term mandatory in every chapter; BanDao tests show anchor-specific requirements reduce false positives.
- Do not treat machine gates as literary approval; audit reports explicitly distinguish machine gates from human quality review.
- Do not move all state into a new table prematurely; `chapter_change_packages` already connect generation, analysis, prompt context, and UI.
- Do not merge inspired-creation copy-risk fields into faithful-continuation canon fields; they share guardrail mechanics but not semantics.
