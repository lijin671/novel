# Novel source discovery - 2026-06-14 preview production-gate projection

## Source

- Local reference: `D:\project\universal-novel-writing`
- Intake posture: `pattern-only`
- Runtime posture: no install, no clone, no package manager, no provider call, no script execution

## Projection

The portable novel-writing workflow already exposed chapter contracts, scene exit
state, progress reports, genre promises, and revision order. This pass moves the
same ideas into the actual MuMuAINovel continuation preview path instead of only
rendering them as prompt text.

## Implemented patterns

- Context preview now surfaces production-control axes and acceptance steps.
- Progress-report gaps are visible in the preview response and UI.
- Webnovel genre tracker warnings are structured, including chapter sequence
gaps, open-hook rotation gaps, missing micro-payoff signals, cliffhanger
rotation gaps, and stale-character review requirements.
- Entity/arc timeline risks feed canon-drift review when the entity mention arc
timeline gate is active.
- The UI shows these gates before users copy or run the continuation context.

## Files

- `backend/app/services/book_remix_context_service.py`
- `backend/app/schemas/book_remix.py`
- `frontend/src/types/bookRemixBible.ts`
- `frontend/src/components/book-remix/BookRemixContinuationContextPreviewPanel.tsx`
- `backend/tests/services/test_book_remix_context_service.py`
- `backend/tests/api/test_book_remix_bible_api.py`

## Verification scope

Run service tests and API preview tests after this projection. Frontend full
build was not claimed here because previous builds can exceed the current turn's
practical timeout.
