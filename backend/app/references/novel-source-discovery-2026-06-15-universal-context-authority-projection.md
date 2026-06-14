# Universal Novel Writing context scope / author intent projection

Date: 2026-06-15

## Source

- `D:/project/universal-novel-writing`
- `D:/project/universal-novel-writing/SKILL.md`
- `D:/project/universal-novel-writing/references/chapter-workflow.md`
- `D:/project/universal-novel-writing/references/story-bible.md`

## Posture

- local static review only
- pattern-only
- license unknown
- no install, script execution, provider call, prompt-body import, source prose import, or manuscript import

## Absorbed pattern

Two additional Universal Novel Writing controls were fused into BookRemix:

- `progressive_context_loading_gate`: choose the selected writing mode first, then load only the minimum needed files, accepted ledgers, and previous 1-2 relevant chapters or summaries;
- `author_intent_confirmation_gate`: preserve authorial intent, genre promise, voice/POV, content limits, ending direction, and require visible confirmation before major turns, long batch drafting, mode shifts, or overwrite-like rewrites.

## Local adaptation

`NovelSourceDiscoveryService` now detects these gates from local static summaries and exposes:

- `progressive_context_loading_gate_hints`
- `author_intent_confirmation_gate_hints`
- matching bible enrichment policies, whole-book report targets, and same-type remap targets

`BookRemixContextService` now projects them into continuation and same-type prompt context, adds production control axes, and warns when:

- progressive context scope is missing;
- author intent boundary is missing;
- long-sequence confirmation policy is missing.

The source-discovery panel surfaces both hint groups next to the other Universal Novel Writing gates.

## Boundary

Progressive loading is a context budget and provenance discipline, not permission to read unrelated source chapters.

Author-intent confirmation protects user direction and accepted canon. It does not authorize hidden rewrites, source prose reuse, or long unattended generation.

## Verification

- `python -m pytest backend/tests/services/test_source_discovery_service.py::test_local_universal_novel_writing_skill_is_static_absorbed backend/tests/services/test_book_remix_context_service.py::test_universal_progressive_loading_and_author_intent_gates_render_context_and_audit backend/tests/frontend/test_source_discovery_panel_copy.py::test_source_discovery_panel_surfaces_universal_novel_writing_gates -q`
- `python -m pytest backend/tests/services/test_source_discovery_service.py backend/tests/services/test_book_remix_context_service.py backend/tests/frontend/test_source_discovery_panel_copy.py -q`
