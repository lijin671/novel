# Novel Source Discovery - 2026-06-09 Serialized Continuity

## Scope

This note records a static source-intake pass for MuMuAINovel book remix, continuation, and same-type creation quality.

The intake focused on serialized webnovel continuity systems: contract chains, chapter commits, fact snapshots, projection logs, foreshadowing debt, retention review, staged drafts, and rolling context trimming.

## Safety Boundary

- Posture: `pattern-only`.
- Intake surface: public repository metadata, public README/root-file inspection, and `git ls-remote` HEAD evidence.
- Scratch files: `tmp/source-intake-2026-06-09-serialized-continuity/`.
- Not performed: install, clone for runtime, script execution, package hooks, Docker, MCP server start, browser extension install, provider call, credential read, or model invocation.
- Runtime trials remain blocked until a separate local safety contract defines scope, auth, secrets, network, cleanup, rollback, and verification.

## Source Snapshot

- `lingfengQAQ/webnovel-writer`
  - URL: https://github.com/lingfengQAQ/webnovel-writer
  - Branch / HEAD: `master` / `e592509b8d0e14fc3aef63cfea6ceaeccdc479e3`
  - License: `NOASSERTION` from static metadata
  - Posture: `pattern-only`
  - Reusable value: Story System contracts, accepted `CHAPTER_COMMIT`, projection log, doctor/preflight, read-only dashboard, RAG/reviewer flow, OOC/rhythm/reader-retention review.

- `zy-zmc/tianming-novel-ai-writer`
  - URL: https://github.com/zy-zmc/tianming-novel-ai-writer
  - Branch / HEAD: `main` / `b7c08b49fbc27af6311eec2b30f1d8e669032b3a`
  - License: `NOASSERTION` from static metadata
  - Posture: `pattern-only`
  - Reusable value: 15-dimensional fact snapshots, 12 change declaration classes, six generation gates, long-distance recall, unified validation, per-chapter state write-back.

- `lujih/webnovel-writer-opencode`
  - URL: https://github.com/lujih/webnovel-writer-opencode
  - Branch / HEAD: `master` / `3030dd2654db8b510ce983469db36b980b670949`
  - License: `NOASSERTION` from static metadata
  - Posture: `pattern-only`
  - Reusable value: OpenCode adaptation of the same serialized writing flow; context preparation, review, anti-AI polish, fact extraction, accepted chapter commit projection.

- `starMagic/webnovel-writer-hermes`
  - URL: https://github.com/starMagic/webnovel-writer-hermes
  - Branch / HEAD: `main` / `a35e162d02a4682c8616c1400565c3ca1b61893b`
  - License: `NOASSERTION` from static metadata
  - Posture: `pattern-only`
  - Reusable value: three-tier memory, foreshadowing `DebtTracker`, dynamic context-budget reservation, entity-graph RAG, time-sliced character-state query, six-dimensional parallel review.

- `HZ-KMNO/web-novel-writing-guidance-skill`
  - URL: https://github.com/HZ-KMNO/web-novel-writing-guidance-skill
  - Branch / HEAD: `main` / `5015b1902cd8492e66ea1688ef3b6502e7d69ef7`
  - License: `NOASSERTION` from static metadata
  - Posture: `pattern-only`
  - Reusable value: chapter blueprint, key-information file, chapter task card, Draft A/B/C ladder, de-AI final pass, continuity record, next-chapter handoff.

- `jinmawang/claude-novel-writeFlow`
  - URL: https://github.com/jinmawang/claude-novel-writeFlow
  - Branch / HEAD: `main` / `a559eee6b7c70063e63b93ebadb5a72c0eff3705`
  - License: `NOASSERTION` from static metadata
  - Posture: `pattern-only`
  - Reusable value: Writer Agent, Style Reviewer, Continuity Reviewer, four-way brainstorm, style definition before outline, +/-2 chapter context window, safe single-chapter rewrite.

- `DuckTraDo/Novel`
  - URL: https://github.com/DuckTraDo/Novel
  - Branch / HEAD: `main` / `cb80630cb340303d70bba42274dd7afbf892d4f8`
  - License: `NOASSERTION` from static metadata
  - Posture: `pattern-only`
  - Reusable value: `memory/story_bible.yaml`, `characters.yaml`, `foreshadowing.yaml`, `events.jsonl`, `timeline.jsonl`, `chapter_summaries.jsonl`, relationship graph, consistency checks, memory update after each chapter.

- `makieali/longform-ai`
  - URL: https://github.com/makieali/longform-ai
  - Branch / HEAD: `main` / `fdf08095f157bcfb993335c5a80572572543e63c`
  - License: `NOASSERTION` from static metadata
  - Posture: `pattern-only`
  - Reusable value: rolling summary, character state tracking, timeline events, world state, relevant passages, token-budget context trimming, edit-cycle records, session restore.

- `guchendesigndog/GC-Writer-Assistant`
  - URL: https://github.com/guchendesigndog/GC-Writer-Assistant
  - Branch / HEAD: `main` / `b38f83c55dddbbd124a04bf7481d8fc97431c83c`
  - License: `NOASSERTION` from static metadata
  - Posture: `pattern-only`
  - Reusable value: lightweight chapter workspace, outline extraction, AI polishing, continuation, themed workspace integration.

## Absorbed Patterns

- `story_contract_commit_chain`
  - Treat story contracts as canon.
  - Drafts become reusable state only after an accepted chapter commit.
  - Derived read models must trace to commit ids.

- `fact_snapshot_delta_gate`
  - Build fact snapshots before prose.
  - Emit typed change declarations after prose.
  - Block write-back when validation cannot explain before/after state.

- `projection_sync_observability`
  - Keep state, index, summary, memory, vector, and dashboard views as projections.
  - Record projection sync/failure/staleness before the next chapter prompt.

- `foreshadowing_debt_budget`
  - Score unresolved hooks as debt.
  - Reserve context for high-debt hooks.
  - A payoff must cite setup, expected window, and new debt status.

- `reader_retention_review_gate`
  - Review consistency, OOC, rhythm, pleasure-point delivery, and next-chapter pull together.
  - Convert retention findings into concrete revision tasks before acceptance.

- `draft_stage_revision_ladder`
  - Use chapter blueprint -> key information -> task card -> Draft A -> Draft B -> Draft C -> continuity handoff.
  - Draft C removes AI tone without changing canon or copy-risk boundaries.

- `rolling_summary_context_trim`
  - Maintain rolling summaries, character state, timeline events, world state, and selected relevant passages.
  - When context is trimmed, persist a manifest of selected and dropped context.

## MuMuAINovel Integration Points

- `source_discovery_service.py`
  - Added default GitHub queries and repository URLs for serialized webnovel continuity sources.
  - Added keyword classification, static summaries, priorities, analysis targets, prompt hints, state hints, and inspired-creation remap/copy-risk guidance for the seven patterns.

- `source_pattern_pack_prompt.py`
  - Added the seven hint families to pattern-pack digest rendering so prompts can see the new guidance.

- `book_remix_context_service.py`
  - Added a serialized continuity audit section for both continuation and same-type inspired contexts.
  - The audit names contract commits, fact snapshots, projections, foreshadowing debt, retention review, staged drafts, and rolling context manifests.

- `backend/app/references/novel-source-pattern-pack-2026-06-09.json`
  - Refreshed from 58 to 67 source candidates.
  - Added the seven serialized continuity pattern groups and their prompt/state/inspired guidance.

## Verification Targets

- `test_serialized_webnovel_projects_are_classified_as_continuity_patterns`
- `test_serialized_webnovel_pattern_pack_exposes_contract_and_review_guidance`
- `test_default_discovery_sources_include_serialized_webnovel_projects`
- `test_build_remix_continuation_context_block_renders_serialized_continuity_audit`
