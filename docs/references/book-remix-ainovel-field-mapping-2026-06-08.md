# BookRemix x ainovel-cli Field Mapping - 2026-06-08

## Purpose

This note maps concrete `ainovel-cli` continuation/recovery fields to MuMuAINovel BookRemix fields and services.
It is evidence collection only; it does not propose a final schema migration.

## Source Evidence

### MuMuAINovel Files

- `backend/app/api/chapters.py`
  - `_enforce_remix_continuation_risk_gate()`
  - `_build_remix_context_for_generation_prompt()`
  - `generate_chapter_content_stream()`
  - `batch_generate_chapters_in_order()`
- `backend/app/services/book_remix_context_service.py`
  - `build_project_context_block()`
  - `build_project_context_preview()`
  - `build_remix_continuation_context_block()`
  - `build_remix_continuation_progress_summary()`
- `backend/app/services/book_remix_continuation_state_service.py`
  - `commit_generated_chapter()`
  - `sync_chapter_analysis()`
  - `_build_generated_chapter_change_package()`
  - `_build_chapter_change_package()`
- `backend/app/models/book_remix_bible.py`
  - `BookRemixBible.chapter_change_packages`
  - `BookRemixContinuationPlan.beats`
  - `BookRemixContinuationPlan.priority_hooks`
- `backend/app/schemas/book_remix.py`
  - `BookRemixContinuationContextPreviewResponse`
  - `BookRemixContinuationProgressSummaryResponse`
  - `BookRemixAnalysisCoverageResponse`
- `frontend/src/types/bookRemixBible.ts`
- `frontend/src/components/book-remix/BookRemixContinuationContextPreviewPanel.tsx`
- `frontend/src/components/book-remix/BookRemixContinuationProgressSummaryPanel.tsx`

### ainovel-cli Files

- `tmp/source-intake-voocel-ainovel-cli-20260529/internal/tools/commit_chapter.go`
- `tmp/source-intake-voocel-ainovel-cli-20260529/internal/tools/novel_context.go`
- `tmp/source-intake-voocel-ainovel-cli-20260529/internal/tools/save_review.go`
- `tmp/source-intake-voocel-ainovel-cli-20260529/internal/tools/check_consistency.go`
- `tmp/source-intake-voocel-ainovel-cli-20260529/internal/domain/commit.go`
- `tmp/source-intake-voocel-ainovel-cli-20260529/internal/domain/checkpoint.go`
- `tmp/source-intake-voocel-ainovel-cli-20260529/internal/domain/review.go`
- `tmp/source-intake-voocel-ainovel-cli-20260529/internal/domain/story.go`
- `tmp/source-intake-voocel-ainovel-cli-20260529/internal/domain/tracking.go`
- `tmp/source-intake-voocel-ainovel-cli-20260529/internal/store/checkpoints.go`

## Generation Chain Observations in MuMuAINovel

### Single Chapter Generation

Observed path:

1. `backend/app/api/chapters.py:generate_chapter_content_stream()` validates chapter and project access.
2. `_enforce_remix_continuation_risk_gate()` runs before generation when durable remix lineage exists.
3. Normal chapter context builder runs based on outline mode.
4. Source pattern pack is resolved if confirmed remix lineage or inspired style applies.
5. `_build_remix_context_for_generation_prompt()` injects BookRemix continuation context first; inspired context is fallback.
6. Chapter outline, continuation point, and previous summary are kept for generated-chapter commit metadata.

Implication:

- BookRemix context is already in the generation path.
- The weak point is not absence of context injection, but whether the context is health-checked, stable, and visibly complete.

### Batch Generation

Observed path:

1. `batch_generate_chapters_in_order()` checks project access.
2. `_enforce_remix_continuation_risk_gate()` runs before creating the batch task.
3. `book_remix_context_service.has_project_durable_remix_lineage()` detects whether this is a remix continuation project.
4. `book_remix_service.prepare_project_continuation_style()` can refresh default continuation style before batch generation.
5. Batch task proceeds with ordered chapter generation.

Implication:

- Batch generation has a risk gate and style augmentation, but a visible per-chapter checkpoint or context-health trace is not yet first-class.

## Field Mapping: `commit_chapter` -> BookRemix Change Package

`ainovel-cli` `commit_chapter` input schema is a useful reference for a complete generated-chapter state writeback.

| ainovel-cli field | Meaning | Current / near-current BookRemix location | Mapping confidence |
|---|---|---|---|
| `chapter` | Global chapter number | `chapter_change_packages[].chapter_number` | High |
| `summary` | Short chapter summary | `chapter_change_packages[].summary`; `Chapter.summary`; `PlotAnalysis.analysis_report` fallback | High |
| `characters` | Appearing character names | `character_state_changes[].character_name/name`; `character_cards` updates | Medium |
| `key_events` | Main chapter events | `timeline_delta[].event/summary/content`; package summary | Medium |
| `timeline_events[].time` | In-story time | `timeline_delta[].time` if analysis emits it | Medium |
| `timeline_events[].event` | Timeline event | `timeline_delta[].event` | High |
| `timeline_events[].characters` | Event participants | `timeline_delta[].characters` if retained | Medium |
| `foreshadow_updates[].id` | Stable hook id | local feature branch adds `hook_id` in plan and packages | High after branch integration |
| `foreshadow_updates[].action` | `plant/advance/resolve` | `foreshadow_changes[].status/type/action`; plan priority hook status | Medium |
| `foreshadow_updates[].description` | Hook content | `foreshadow_changes[].hook/content/summary` | High |
| `relationship_changes[]` | Relationship state | No explicit first-class BookRemix package field yet; could map to `character_state_changes` or future `relationship_changes` | Low/Gap |
| `state_changes[].entity` | Character/entity name | `character_state_changes[].character_name/name` | High |
| `state_changes[].field` | Changed attribute | `character_state_changes[].field` if analysis emits it | Medium |
| `state_changes[].old_value` | Before state | `character_state_changes[].state_before` | High |
| `state_changes[].new_value` | After state | `character_state_changes[].state_after` | High |
| `state_changes[].reason` | Cause | `character_state_changes[].reason` if retained | Medium |
| `cast_intros[]` | New secondary cast ledger | No direct BookRemix field; could extend `character_cards` with `tier=secondary` or add `cast_ledger` | Gap |
| `hook_type` | Chapter-end hook type | No explicit package field; possible `emotional_arc` / `guardrail_check` adjunct | Gap |
| `dominant_strand` | Dominant narrative strand | Could map to plan beat/stage/arc metadata; no explicit field | Gap |
| `feedback` | Outline deviation/adaptation | Could map to `generation_notes`, future intervention ledger, or plan feedback | Gap |

## Field Mapping: `CommitResult` -> BookRemix Runtime Signal

`ainovel-cli` commit returns structured facts, not prose instructions:

- `chapter`
- `committed`
- `word_count`
- `next_chapter`
- `review_required`
- `review_reason`
- `hook_type`
- `dominant_strand`
- `feedback`
- `arc_end`
- `volume_end`
- `volume`
- `arc`
- `needs_expansion`
- `needs_new_volume`
- `next_volume`
- `next_arc`
- `book_complete`
- `flow`
- `rule_violations`

MuMuAINovel equivalents:

| ainovel-cli result | Current BookRemix equivalent | Gap / note |
|---|---|---|
| `word_count` | Chapter content length/word count in chapter model and frontend summaries | Present, not necessarily stored in change package |
| `next_chapter` | Sequential generation/order checks in `chapters.py` and batch task | Present operationally, not emitted as BookRemix state fact |
| `review_required` / `review_reason` | Workflow review may exist, but not BookRemix-specific continuation review signal | Gap |
| `arc_end` / `volume_end` | `stage_goals` and `story_arcs` exist, but boundary signals are not generated per chapter | Gap |
| `needs_expansion` / `needs_new_volume` | No explicit rolling plan expansion trigger | Gap |
| `book_complete` | No BookRemix-specific terminal continuation signal | Gap |
| `rule_violations` | `guardrail_check.violations` in chapter change packages | Strong equivalent |
| `flow` | Batch task status / workflow status / plan status | Partial equivalent |

Recommendation from mapping:

- Do not copy `CommitResult` wholesale.
- Add only the BookRemix-native facts needed by the UI and next prompt: `next_chapter`, `review_required`, `review_reason`, stage boundary flags, and guardrail summary.

## Field Mapping: `novel_context` -> BookRemix Context Preview

`ainovel-cli` `novel_context` emits both context content and loading diagnostics:

- `_warnings`
- `_trimmed`
- `_loading_summary`
- role-specific payload: writer vs architect/coordinator
- budget trimming: Writer 100KB, Architect 60KB
- related chapters
- selected memory: story threads and review lessons

Current MuMuAINovel preview response:

```text
project_id
has_context
context
context_length
lineage_confirmed
reason
source_pattern_pack_loaded
```

Existing frontend panel displays:

- ready/not-ready alert
- lineage confirmed tag
- source pattern pack loaded tag
- context length tag
- raw context preview

Suggested `context_health` fields based on mapping:

```json
{
  "bible_confirmed": true,
  "plan_confirmed": true,
  "plan_current_for_bible": true,
  "source_pattern_pack_loaded": true,
  "chapter_change_package_count": 12,
  "package_chapter_range": {"start": 201, "end": 212},
  "pending_plan_beat_count": 8,
  "open_hook_count": 4,
  "warnings": [],
  "missing_sections": [],
  "loading_summary": "bible:ok plan:ok packages:12 hooks:4 beats:8 source_pack:ok"
}
```

Why this is low-risk:

- It can be derived from existing bible/plan/package payloads.
- It does not require changing generation behavior.
- The frontend panel already has tag/alert UI patterns.

## Field Mapping: Related Chapter Recall

`ainovel-cli` `buildRelatedChapters()` selects up to five chapters using:

1. Active foreshadow text / ID match against current outline.
2. Character last appearance from summaries.
3. Character state-change history.
4. Relationship change history.

MuMuAINovel available inputs:

- Current `Chapter` and `Outline` in generation path.
- `PlotAnalysis` rows for source/generated chapters.
- `BookRemixBible.foreshadows` and `chapter_change_packages[].foreshadow_changes`.
- `BookRemixBible.character_cards` and `chapter_change_packages[].character_state_changes`.
- `BookRemixContinuationPlan.beats` and `priority_hooks`, with stable IDs on the local feature branch.

Missing or partial inputs:

- Relationship changes are not first-class in BookRemix package schema.
- Character appearance index is not explicit, but can be approximated from chapter summaries/analysis/package state changes.
- Current outline-to-character matching may be brittle without aliases.

Candidate minimal BookRemix implementation later:

- Build a read-only `related_chapters` block during context assembly.
- Use no new table initially.
- Score from:
  - matching `hook_id` / hook text;
  - matching character names in current outline;
  - latest `character_state_changes` per character;
  - recent failed guardrail/review lessons if available.

## Field Mapping: `save_review` -> BookRemix QA / Manual Intervention

`ainovel-cli` `save_review` requires exactly seven dimensions:

- `consistency`
- `character`
- `pacing`
- `continuity`
- `foreshadow`
- `hook`
- `aesthetic`

Each issue must include:

- `type`
- `severity`
- `description`
- `evidence`
- optional `suggestion`

It also tracks:

- `contract_status`: `met / partial / missed`
- `contract_misses`
- `verdict`: `accept / polish / rewrite`
- `affected_chapters`
- final verdict escalation
- pending rewrite/polish queue
- review checkpoint

MuMuAINovel equivalents:

| ainovel-cli review | Existing BookRemix / workflow equivalent | Gap / note |
|---|---|---|
| Seven dimensions | Could be represented in workflow review / guardrail metadata, but not BookRemix continuation-specific | Gap |
| Evidence-required issues | `guardrail_check.violations[].context/description` has partial equivalent | Partial |
| Contract status/misses | Continuation plan beat/guardrail fulfillment can serve as contract | Gap |
| `affected_chapters` | Batch/workflow retry logic exists, but not BookRemix review ledger | Gap |
| pending rewrite/polish queue | General workflow may have regeneration, but no BookRemix manual intervention ledger | Gap |
| review checkpoint | No BookRemix checkpoint event log yet | Gap |

Candidate low-risk route:

- First add a read-only review summary field inside `chapter_change_packages` or a separate `review_packages` JSON list.
- Later connect it to workflow auto-regeneration only after UI and user controls exist.

## Field Mapping: Checkpoints / Pending Commit

`ainovel-cli` checkpoint model:

```json
{
  "seq": 1,
  "scope": {"kind": "chapter", "chapter": 201},
  "step": "commit",
  "artifact": "chapters/201.md",
  "digest": "sha256:...",
  "occurred_at": "..."
}
```

`PendingCommit` model:

```json
{
  "chapter": 201,
  "stage": "started | state_applied | progress_marked | signal_saved",
  "summary": "...",
  "hook_type": "...",
  "dominant_strand": "...",
  "result": {...},
  "started_at": "...",
  "updated_at": "..."
}
```

MuMuAINovel current state:

- Chapter generation and batch generation have task/status models.
- BookRemix state writes are stored as JSON changes in bible/plan.
- Chapter change packages serve as a durable-ish per-chapter summary, but not as a general append-only step log.

Suggested future event names:

- `context_built`
- `chapter_generated`
- `generated_state_committed`
- `guardrail_checked`
- `analysis_queued`
- `analysis_synced`
- `context_preview_refreshed`
- `review_saved`
- `manual_intervention_opened`
- `manual_intervention_resolved`

Do not implement a new table until:

- Context-health visibility exists.
- Stage gate templates are visible in UI.
- The team confirms that replay/resume is worth schema migration.

## Frontend Readiness

Existing frontend already has:

- `BookRemixContinuationContextPreviewPanel`
- `BookRemixContinuationProgressSummaryPanel`
- `BookRemixChapterChangePackage` types
- `BookRemixAnalysisCoveragePanel`
- `BookRemixSourceDiscoveryPanel`

Smallest frontend path for `context_health`:

1. Extend `BookRemixContinuationContextPreview` type.
2. Add tags for `package_count`, `package_range`, `warnings`, and `missing_sections`.
3. Show warning `Alert` if context exists but health has warnings.
4. Keep raw context preview unchanged.

Smallest frontend path for future stage gates:

1. Extend progress summary or chapter change package panel with gate counts.
2. Display `passed / warning / blocked` tags.
3. Keep detailed violations under existing guardrail/audit UI.

## Current Gaps Ranked by Evidence Strength

### High-confidence gaps

1. `context_health` diagnostics are missing from API/frontend despite context preview already existing.
2. Relationship changes and cast ledger are not first-class in BookRemix continuation packages.
3. Stage/arc boundary signals are not generated per chapter.
4. BookRemix review results are not represented as a seven-dimensional, evidence-required ledger.
5. Manual intervention and rewrite/polish queues are not first-class in BookRemix.

### Medium-confidence gaps

1. Related-chapter recall can be built from current packages, but matching quality depends on aliases and IDs.
2. Step-level checkpoints could improve recovery, but a JSON event list may be enough before DB migration.
3. Contract status can be derived from plan beats/guardrails, but needs UX design.

### Low-confidence / defer

1. Full arc/volume rolling plan expansion should wait until context-health, ID sync, and stage gates are stable.
2. Dedicated relationship model/table should wait until package-based relationship field proves useful.

## Suggested Next Evidence Collection

If continuing research before coding, inspect:

- Existing workflow review/regeneration models in `backend/app/models/novel_workflow.py` and related services.
- `chapter_guardrails.py` to see whether stage gate templates can reuse existing violation format.
- `PlotAnalysis` schema/model for character and foreshadow fields available for related-chapter recall.
- Frontend audit panels to decide whether stage gates belong in progress summary or package detail.
