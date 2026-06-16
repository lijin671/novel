# Universal Novel Writing revision strategy fusion

Date: 2026-06-17

## Source

- Local path: `D:\project\universal-novel-writing`
- Files reviewed:
  - `SKILL.md`
  - `references/revision-checklists.md`
  - `references/chapter-workflow.md`
  - `references/planning-templates.md`
  - `references/story-bible.md`

## Posture

- Static review only.
- Pattern-only.
- No install, package execution, provider call, browser/MCP/desktop runtime,
  upstream prompt-body import, or manuscript/prose import.

## Absorbed pattern

The useful pattern is an explicit revision strategy:

- revise in order: developmental -> character -> continuity -> scene -> line ->
  proof/format;
- assign severity before repair;
- patch the smallest failing artifact first;
- naturalness repair should add concrete action, sensory pressure,
  character-specific diction, subtext, uneven rhythm, and mobile-readable
  paragraph breaks.

## MuMuAINovel projection

`BookRemixDeconstructionPack` now includes `revision_strategy` alongside the
existing `revision_gates`.

This makes the preview packet more actionable:

- `revision_gates` says what to check;
- `revision_strategy` says in what order to check and how narrowly to repair.

The style payload prompt now passes `revision_strategy.ordered_passes` and
`revision_strategy.patch_policy` into continuation and same-type style setup.
The frontend preview panel also surfaces this field before project creation.

The continuation context builder now renders a first-class
`Universal revision strategy control` block when the source pattern pack carries
revision order, patch strategy, post-draft review, minimal rollback, or
naturalness gates. Its production audit also exposes:

- `revision_strategy_ordered_passes`;
- `revision_severity_triage`;
- `smallest_failing_artifact_patch_policy`;
- `anti_ai_naturalness_repair_axis`.

## Boundary

This does not import upstream prose, examples, or prompt bodies.

Continuation repair must act on target-owned accepted chapters, bible state, and
continuation plan. Same-type creation may reuse only the revision order and
patch discipline; source findings and source text cannot become target canon.

## Verification

```powershell
python -X utf8 -m pytest backend/tests/services/test_book_remix_service.py::test_deconstruction_pack_for_continuation_surfaces_universal_contract backend/tests/frontend/test_book_remix_preview_copy.py::test_book_remix_preview_surfaces_deconstruction_pack -q
python -X utf8 -m pytest backend/tests/services/test_book_remix_context_service.py::test_build_remix_continuation_context_block_renders_universal_novel_workflow_contract backend/tests/services/test_book_remix_context_service.py::test_build_remix_context_preview_audit_projects_universal_chapter_contract_gates -q
```
