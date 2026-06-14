# Novel Studio AI graph-memory continuity projection

Date: 2026-06-14

## Source

- `https://github.com/YfengJ/novel-studio-ai`
- Observed default branch: `main`
- Observed HEAD: `90fbf0681e76afe791d11f21edd1fb1516ee5e1d`
- Discovery channel: GitHub search / static source intake
- License: not observed from root `LICENSE` or `LICENSE.md`

## Posture

- pattern-only
- L1 public metadata and raw README/root marker review only
- no clone, install, package script, database migration, provider/model call,
  API-key use, local SQLite/vector runtime, manuscript import, generated prose
  import, or runtime trial

## Absorbed pattern

Novel Studio AI contributes a local-first longform continuity model:

- draft chapters remain temporary and cannot update canon
- only accepted chapters write summaries, character states, graph triples,
  timeline events, and memory chunks
- next context packs combine story bible, outline, recent summaries, active
  character states, graph facts, retrieved memory chunks, and timeline events
- continuity checks should catch dead-character conflicts, impossible locations,
  item ownership drift, relationship resets, and style-rule drift before canon
  promotion

## Local adaptation

`BookRemixContextService` now renders a
`Novel Studio graph-memory continuity gate` when a pattern pack includes:

- `novel_studio_graph_memory_continuity_gate`
- `novel_studio_accepted_chapter_writeback_gate`

Added control axes:

- `accepted_chapter_writeback_surface`
- `graph_fact_triple_consistency`
- `character_state_versioning`
- `timeline_event_ordering`
- `contradiction_checklist_review`
- `hybrid_retrieval_context_pack`

Added acceptance steps:

- `verify_accepted_chapter_writeback`
- `verify_graph_fact_triples`
- `verify_character_state_timeline_conflicts`
- `verify_hybrid_retrieval_pack_scope`

This complements the existing context-pack preview gate by making the graph fact,
character-state, timeline, and writeback surfaces explicit in both continuation
and same-type creation prompt contexts.

## Boundary

Continuation mode may use these graph-memory checks only against target-owned
accepted bible, plan, chapter summaries, timeline, character state, and memory.
Draft-only events remain non-canon.

Same-type creation may copy only the graph-memory discipline. It must rebuild all
source graph triples, character states, timeline events, memory chunks, names,
locations, and chapter summaries independently.

## Verification

- `python -m pytest backend/tests/services/test_book_remix_context_service.py::test_novel_studio_graph_memory_continuity_gate_renders_context_and_audit -q`
