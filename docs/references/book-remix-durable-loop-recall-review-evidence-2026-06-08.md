# BookRemix Durable Loop, Recall, Review, and Intervention Evidence - 2026-06-08

## Purpose

This is an evidence-only continuation of BookRemix research. It focuses on the implementation slices that should come after `context_health` and generic stage gates:

1. related chapter recall;
2. review lesson compaction;
3. manual intervention / pending rewrite ledger;
4. durable checkpoint / commit-saga patterns.

No functional code is changed by this document.

## Evidence Sources

### MuMuAINovel current files

- `backend/app/models/memory.py`
- `backend/app/models/novel_workflow.py`
- `backend/app/services/book_remix_context_service.py`
- `backend/app/services/book_remix_service.py`
- `backend/app/services/book_remix_continuation_state_service.py`
- `backend/app/services/novel_workflow_service.py`
- `backend/app/schemas/book_remix_bible.py`
- `frontend/src/components/book-remix/BookRemixContinuationProgressSummaryPanel.tsx`
- `frontend/src/types/bookRemixBible.ts`
- `backend/tests/services/test_novel_workflow_unlimited_review_policy.py`

### ainovel-cli reference files

- `tmp/source-intake-voocel-ainovel-cli-20260529/internal/tools/novel_context.go`
- `tmp/source-intake-voocel-ainovel-cli-20260529/internal/tools/novel_context_builders.go`
- `tmp/source-intake-voocel-ainovel-cli-20260529/internal/tools/novel_context_test.go`
- `tmp/source-intake-voocel-ainovel-cli-20260529/internal/tools/commit_chapter.go`
- `tmp/source-intake-voocel-ainovel-cli-20260529/internal/tools/save_review.go`
- `tmp/source-intake-voocel-ainovel-cli-20260529/internal/domain/commit.go`
- `tmp/source-intake-voocel-ainovel-cli-20260529/internal/domain/checkpoint.go`
- `tmp/source-intake-voocel-ainovel-cli-20260529/internal/domain/review.go`
- `tmp/source-intake-voocel-ainovel-cli-20260529/internal/store/checkpoints.go`
- `tmp/source-intake-voocel-ainovel-cli-20260529/internal/store/signals.go`
- `tmp/source-intake-voocel-ainovel-cli-20260529/internal/store/progress.go`

## Related Chapter Recall Evidence

### ainovel-cli pattern

`novel_context_builders.go` builds a layered chapter context envelope:

- `working_memory`
- `episodic_memory`
- `reference_pack`
- `selected_memory`

Selected memory is only emitted when there is useful selected content:

```go
func (t *ContextTool) buildChapterSelectedMemory(envelope *chapterContextEnvelope, state contextBuildState, warn func(string, error)) {
    if len(state.storyThreads) > 0 {
        envelope.Selected["story_threads"] = state.storyThreads
    }
    if lessons := t.selectReviewLessons(state.chapter, warn); len(lessons) > 0 {
        envelope.Selected["review_lessons"] = lessons
    }
}
```

Related chapter recall appears in episodic memory when the book is long enough and there is enough context:

```go
if state.progress != nil && state.progress.TotalChapters > 30 && state.currentEntry != nil {
    if related := t.buildRelatedChapters(...); len(related) > 0 {
        envelope.Episodic["related_chapters"] = related
    }
}
```

`novel_context_test.go` verifies:

- `story_threads` are recalled when the next chapter overlaps with active hooks / payoff points.
- weak-overlap foreshadows stay out.
- `related_chapters` are not duplicated into `story_threads`.
- small foreshadow sets keep the full `foreshadow_ledger` instead of adding sparse selected memory.
- sparse selected memory falls back to full ledger.

Important anti-pattern avoided by ainovel-cli:

- It does not retrieve everything.
- It separates compact selected memory from full ledgers.
- It avoids duplicating `related_chapters` into `story_threads`.
- It uses fallback to full ledger when selection quality is too sparse.

### MuMuAINovel current state

MuMuAINovel already has strong raw sources for recall:

`PlotAnalysis` (`backend/app/models/memory.py`) exposes:

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
- `overall_quality_score`
- `pacing_score`
- `engagement_score`
- `coherence_score`
- `analysis_report`
- `suggestions`
- `word_count`

`BookRemixBible.chapter_change_packages` already stores continuation-facing state deltas, and current context code summarizes:

- timeline progression;
- latest character states;
- resolved/open hooks;
- completed plan beats;
- pending plan beats;
- emotional progression.

`BookRemixContinuationProgressSummaryPanel` already displays:

- package count;
- chapter range;
- timeline progression;
- latest character state;
- emotional progression;
- resolved hooks;
- open hooks;
- completed plan beats;
- pending plan beats.

### Evidence-based recommendation

Start related chapter recall as read-only prompt/context augmentation, not as a new index table.

First implementation shape:

```json
{
  "selected_memory": {
    "related_chapters": [
      {
        "chapter_number": 37,
        "reason": "same open hook + same character state",
        "summary": "...",
        "matched_signals": ["hook:xxx", "character:yyy"],
        "source": "chapter_change_package | plot_analysis"
      }
    ],
    "story_threads": [],
    "review_lessons": []
  }
}
```

Initial recall inputs, in priority order:

1. `chapter_change_packages` recent + semantically related package deltas.
2. `PlotAnalysis` rows for source chapters, especially `foreshadows`, `hooks`, `plot_points`, `character_states`.
3. Continuation plan beats and priority hooks.

Do not add a vector index yet. Use simple signal overlap first:

- shared `hook_id` / `hook` text;
- shared `beat_id` / beat text;
- same character names in `character_states`;
- same conflict type / plot stage;
- same emotional tone only as a weak signal, never enough by itself.

Suggested tests for a future slice:

1. Recall includes a prior package with the same `hook_id`.
2. Recall includes a prior `PlotAnalysis` with overlapping character + foreshadow.
3. Recall does not include weak emotional-tone-only matches.
4. Recall limits output count and reports a compact loading summary.
5. Recall falls back to full open hook list when selected recall is too sparse.

## Review Lesson Compaction Evidence

### ainovel-cli pattern

`save_review.go` stores structured review entries and updates flow state.

Review shape (`domain/review.go`):

```json
{
  "chapter": 1,
  "scope": "chapter | global | arc",
  "dimensions": [
    {"dimension": "consistency", "score": 80, "verdict": "pass", "comment": "..."}
  ],
  "issues": [
    {"type": "hook", "severity": "warning", "description": "...", "evidence": "...", "suggestion": "..."}
  ],
  "contract_status": "met | partial | missed",
  "contract_misses": [],
  "verdict": "accept | polish | rewrite",
  "summary": "...",
  "affected_chapters": []
}
```

`save_review` applies a scorecard gate:

- critical dimensions: `consistency`, `character`, `continuity`.
- `contract_status=missed` upgrades to rewrite.
- `contract_status=partial` upgrades to polish.
- polish/rewrite requires affected chapters.
- review checkpoint is appended after state changes.

`novel_context_test.go` verifies review lessons are recalled into `selected_memory.review_lessons`, including:

- chapter-scope lessons;
- global review lessons;
- contract misses.

### MuMuAINovel current state

`ChapterWorkflowResult` already stores review output:

- `overall_score`
- `analysis_score`
- `review_score`
- `reader_score`
- `reviewers`
- `reader_feedback`
- `aggregate`
- `revision_brief`
- `applied_regeneration`
- `regeneration_task_id`

`NovelWorkflowService` already provides:

- bounded review rounds (`MAX_SAFE_REVIEW_ROUNDS = 12`);
- style fidelity gates;
- high/critical issue collection;
- reader risk aggregation;
- style drift issue aggregation;
- auto-regeneration;
- stale analysis marking after regeneration;
- BookRemix state commit after auto-regeneration.

Tests verify:

- unlimited review requests are capped with explicit stop conditions;
- high style drift forces revision even when other scores pass;
- low style fidelity forces revision;
- legacy reviewer output without style fields remains backward compatible;
- revision brief includes style drift repair requirements.

### Evidence-based recommendation

Do not build a parallel BookRemix review engine.

Instead, add a compact review lesson extractor that reads existing `ChapterWorkflowResult` records and emits only reusable lessons into context or preview metadata.

Potential compact shape:

```json
{
  "review_lessons": [
    {
      "chapter_number": 38,
      "source": "workflow_result",
      "decision": "revise",
      "severity": "high",
      "lesson": "Style fidelity drift: cadence became too modern and clipped.",
      "advice": "Restore source cadence and narrative temperature.",
      "applied_regeneration": true
    }
  ]
}
```

Good candidates for compaction:

- high/critical issues;
- style drift issues;
- must-fix items;
- top reader risks;
- revision brief first lines;
- `analysis_stale` / `remix_continuation_sync` facts from aggregate.

Do not include full reviewer payload in prompt context.

Suggested tests:

1. Extract high/critical style drift as a review lesson.
2. Extract `must_fix` into a lesson.
3. Ignore low-severity generic praise.
4. Mark lessons from auto-regenerated chapters as `applied_regeneration=true`.
5. Keep output bounded by count and character budget.

## Manual Intervention / Pending Rewrite Evidence

### ainovel-cli pattern

`save_review.go` turns polish/rewrite verdicts into a pending rewrite queue:

- `Progress.SetPendingRewrites(chapters, reason)`
- `Progress.SetFlow(rewriting | polishing)`

`progress.go` enforces the queue:

- while flow is rewriting/polishing, only chapters inside `PendingRewrites` may be worked on;
- `CompleteRewrite(chapter)` drains the queue;
- when the queue is empty, flow returns to writing.

`commit_chapter.go` rewrite path enforces that:

- an already completed chapter in pending rewrite may be overwritten;
- draft equal to final is rejected to prevent fake rewrite;
- rewrite commit drains the queue;
- world state deltas are not blindly re-applied during rewrite.

This is stronger than a note field: it is an operational queue with constraints.

### MuMuAINovel current state

BookRemix currently has:

- `ChapterWorkflowResult.applied_regeneration`
- `ChapterWorkflowResult.regeneration_task_id`
- workflow aggregate metadata;
- `_mark_analysis_stale_after_auto_regeneration()`;
- `_commit_auto_regeneration_to_remix_state()`;
- `BookRemixBible.generation_notes`;
- `BookRemixBible.chapter_change_packages`.

But there is no first-class manual intervention ledger for:

- temporary human patch;
- reason;
- affected chapter(s);
- whether regeneration replaced the patch;
- whether reanalysis is required;
- whether continuation state was resynced.

BanDao evidence also showed a temporary manual regression-anchor patch later resolved by regeneration. That pattern should be represented explicitly before long-run operations become routine.

### Evidence-based recommendation

Add manual intervention only after `context_health` and review lessons are visible.

Potential ledger shape inside existing JSON first:

```json
{
  "manual_interventions": [
    {
      "intervention_id": "intervention-001",
      "chapter_number": 231,
      "type": "temporary_patch | manual_rewrite | human_note",
      "reason": "regression anchor missing",
      "status": "open | superseded_by_regeneration | closed",
      "created_at": "...",
      "resolved_at": null,
      "requires_reanalysis": true,
      "related_package_id": "...",
      "resolution": {
        "regeneration_task_id": "...",
        "chapter_change_package_id": "..."
      }
    }
  ]
}
```

Likely first storage home:

- `BookRemixBible.generation_notes` for human-readable notes is too loose.
- `chapter_change_packages` is good for chapter-level state changes but awkward for cross-chapter queues.
- A new JSON key on Bible, e.g. `manual_interventions`, is clearer but requires schema/model/frontend work.

Lowest-risk interim path:

- add compact manual intervention facts to `chapter_change_packages` when tied to a chapter;
- defer a global queue until there is UI/workflow need.

## Durable Checkpoint / Commit Saga Evidence

### ainovel-cli pattern

`commit_chapter.go` uses a pending commit saga:

Stages (`domain/commit.go`):

- `started`
- `state_applied`
- `progress_marked`
- `signal_saved`

`PendingCommit` stores:

- chapter;
- stage;
- summary;
- hook type;
- dominant strand;
- result;
- timestamps.

`signals.go` stores:

- `meta/pending_commit.json`
- `meta/last_commit.json`
- `meta/last_review.json`

`checkpoints.go` stores append-only JSONL checkpoints:

- `seq`
- `scope`
- `step`
- `artifact`
- `digest`
- `occurred_at`

Important properties:

- append-only checkpoint facts;
- idempotency by `Scope + Step + Digest`;
- seq advances only after successful write;
- malformed tail lines are skipped on restore;
- latest-by-scope and latest-by-step queries exist;
- pending commit is cleared if a repeat commit sees chapter already completed;
- stop guards can require a new `commit` checkpoint before ending.

### MuMuAINovel current state

BookRemix has durable persisted state in DB JSON fields:

- `BookRemixBible.chapter_change_packages`
- `BookRemixContinuationPlan.beats`
- `BookRemixContinuationPlan.priority_hooks`
- `ChapterWorkflowResult`
- `RegenerationTask`
- `PlotAnalysis`

The recent ID-state-loop slice already improves logical idempotency:

- stable `beat_id` / `hook_id`;
- ID-aware sync;
- legacy text overlap fallback.

Remaining gap:

- there is no append-only step checkpoint log for multi-step chapter commit.
- `commit_generated_chapter()` writes a final change package but does not expose a resumable saga with stage facts.

### Evidence-based recommendation

Do not add a full checkpoint table before diagnostics/gates/review lessons, unless failures show it is necessary.

If implemented, prefer a small `book_remix_workflow_events` / JSONL-like DB table later rather than overloading `chapter_change_packages`.

Potential event shape:

```json
{
  "event_id": "...",
  "project_id": "...",
  "chapter_id": "...",
  "chapter_number": 42,
  "scope": "chapter",
  "step": "generation_saved | package_committed | analysis_synced | review_completed | regeneration_applied",
  "artifact_ref": "chapter_change_package:<id>",
  "digest": "sha256:...",
  "status": "completed",
  "occurred_at": "..."
}
```

But first use existing evidence:

- `chapter_change_packages` as canon state deltas;
- `ChapterWorkflowResult` as review facts;
- `RegenerationTask` as rewrite facts;
- `analysis_coverage` as sync/readiness diagnostics.

## Fit With Current Recommended Sequence

Current sequence remains:

1. `context_health` preview diagnostics.
2. generic stage/regression gates using guardrail structures.
3. review lesson compaction from `ChapterWorkflowResult`.
4. manual intervention ledger / pending rewrite visibility.
5. related chapter recall.
6. durable checkpoint / saga only if needed by failure evidence.

This document strengthens the evidence for steps 3-6 and confirms that steps 1-2 should still happen first.

## Open Questions

1. Should related chapter recall be surfaced in `context_health` as a count first, before injecting into prompts?
2. Should review lessons live in `selected_memory` inside the prompt block, or as a separate preview metadata field first?
3. Should manual interventions be chapter-scoped package facts first or a global queue from the beginning?
4. Should durable checkpoints be a DB table, a JSON field event log, or avoided until long-running failures require it?
5. Should rewrite/polish queues block generation, or first only warn in the preview/context health panel?

## Current Recommendation

Keep the next code slice as `context_health`. After that, implement stage gates. Then implement review lesson compaction as a read-only context preview/prompt addition. Related chapter recall and manual intervention queues should be delayed until diagnostics and review lessons make the state visible enough to debug.
