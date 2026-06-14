# Universal Novel Writing post-draft review projection

Date: 2026-06-14

## Source

- `D:/project/universal-novel-writing`
- `D:/project/universal-novel-writing/SKILL.md`
- `D:/project/universal-novel-writing/references/chapter-workflow.md`
- `D:/project/universal-novel-writing/references/revision-checklists.md`

## Posture

- local static review only
- pattern-only
- license unknown
- no install, package execution, provider call, prompt-body import, source prose import, or manuscript import

## Absorbed pattern

The portable workflow treats chapter acceptance as a review packet, not just a generated draft. The reusable control surface is a post-draft checklist with three durable requirements:

- review the latest accepted chapter against story structure, continuity, POV, character voice, scene conflict, pacing, reader pull, hook/payoff movement, prose naturalness, and mobile readability;
- record mobile-readability evidence before accepting serial chapter output;
- repair the smallest failing artifact first: paragraph, scene, ledger field, chapter contract, or review note.

## Local adaptation

`BookRemixContextService` now recognizes `post_draft_review_checklist_gate` from source pattern packs and projects it into both remix modes.

Continuation mode adds:

- `post_draft_review_checklist`
- `mobile_readability_review`
- `least_destructive_repair_scope`

Same-type mode keeps source review notes out of canon. It transfers only the review axes; target drafts must produce fresh target-owned findings.

The preview/control audit now exposes `post_draft_review_warnings` so the UI can block or highlight chapters that lack review evidence before the next drafting step.

## Boundary

For continuation, review evidence must come from target-owned accepted chapter packages, bible state, or plan state.

For same-type creation, upstream review notes, chapter fixes, and readability patches are craft references only. They cannot become target facts, target fixes, or target manuscript text.

## Verification

- `backend/tests/services/test_book_remix_context_service.py`
- `python -m pytest backend/tests/services/test_book_remix_context_service.py -q`
