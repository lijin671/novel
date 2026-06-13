# Universal Novel Writing full chapter contract projection

Date: 2026-06-14

## Source

- `D:/project/universal-novel-writing`
- `D:/project/universal-novel-writing/references/chapter-workflow.md`
- `D:/project/universal-novel-writing/references/story-bible.md`
- `D:/project/universal-novel-writing/references/planning-templates.md`

## Posture

- local static review only
- pattern-only
- license unknown
- no upstream runtime, provider call, install, prompt-body import, or manuscript
  text import

## Absorbed pattern

The portable `Chapter Contract` template is now projected into the concrete
remix continuation context, not only summarized as a generic gate.

Additional contract fields:

- POV
- starting emotion/status
- escalation
- new hook/question
- character change
- continuity fact to preserve
- word-count target

## Local adaptation

`BookRemixContextService` now builds the next-chapter scaffold from accepted
MuMuAINovel state:

- latest accepted chapter package
- latest character-state deltas
- timeline/continuity deltas
- pending plan beat
- pending priority hook
- style signature
- hard constraints and guardrails

The audit now flags missing full-contract surfaces before drafting, so the UI
can show incomplete continuation state instead of silently falling back to a
thin "next chapter" prompt.

## Boundary

For continuation, these fields must come from target-owned accepted bible,
plan, and chapter packages.

For same-type creation, source chapter contracts are craft references only.
Target stories must rebuild POV, status, escalation, hooks, character changes,
continuity facts, and length targets independently.

## Verification

- `backend/tests/services/test_book_remix_context_service.py`
- `python -m pytest backend/tests/services/test_book_remix_context_service.py -q`
