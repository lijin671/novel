# Local static intake: universal-novel-writing

Date: 2026-06-13

Source: `D:\project\universal-novel-writing`

Posture: `pattern-only`

Runtime boundary: no install, no package execution, no provider call, no MCP/browser/desktop runtime, no prompt body transplant.

## Static surface

- `SKILL.md`
- `references/chapter-workflow.md`
- `references/genre-patterns.md`
- `references/planning-templates.md`
- `references/revision-checklists.md`
- `references/story-bible.md`

Observed file hashes:

```text
820E8643F352CA13A5CC200BA7CF66646EA8052CDC811186EAB65A5FE3B06AB7  SKILL.md
EDA357C06A86070D0B043BF718E37F2A20E418ADAF5C909D7EAFD8D71AB5573D  references/chapter-workflow.md
A3466E86CD70FB59B11DCEB2114B4FB1DC24C68241CBE81A3684725FA9DED735  references/genre-patterns.md
702038C09620725070AD713E2A5A398DEC8CCF0CD79208E7A7C9AC1B14968A7D  references/planning-templates.md
FDDC6EF1B189CB00657C2273C4AD1B762E191FE1A64691B4DED0C38958F39689  references/revision-checklists.md
FC12A7DD8CDF7188E53AABA29B4C6C14B8A7CC100D11B9F7BE7DE000AA8FCA4B  references/story-bible.md
```

## Absorbed patterns

- `universal_novel_mode_contract_gate`
  - Explicit mode selection: `quick-start`, `full-project`, `continue-chapter`, `revise`, `analyze`, `export`.
  - Mode controls the output contract and prevents silent task expansion.
- `portable_story_project_structure_gate`
  - Portable Markdown state: `story-bible.md`, `outline.md`, `characters.md`, `worldbuilding.md`, `continuity.md`, `progress.md`.
  - Manuscript, notes, and revision artifacts stay in separate folders.
- `chapter_contract_scene_beat_gate`
  - Chapter contract before prose: job, reader promise, POV, hook, goal, obstacle, escalation, payoff, new hook, forbidden contradictions.
  - Most chapters use 3-7 scene beats with changed exit state.
- `reader_promise_micro_payoff_gate`
  - Every chapter should serve a reader promise.
  - Chinese webnovel continuation needs chapter-level micro-payoff with cost or state change.
- `revision_order_natural_prose_gate`
  - Revision order: developmental → character → continuity → scene → line → proof/format.
  - Anti-AI cleanup means concrete action, sensory detail, subtext, character-specific diction, and uneven rhythm.
- `progress_report_continuity_writeback_gate`
  - After each chapter, write back summary, new facts, character changes, hooks paid off, new hooks, continuity updates, next likely focus, and risks.

## MuMuAINovel integration

- `source_discovery_service.py`
  - Accepts `local_references` as metadata-only static intake.
  - Adds the six pattern gates above to pattern detection and pattern-pack generation.
- `source_pattern_pack_prompt.py`
  - Renders the new gate hints into generation/guardrail prompt digests.
- `BookRemixSourceDiscoveryPanel.tsx`
  - Surfaces the universal novel-writing gates in the source-discovery pattern panel.
- `book_remix_context_service.py`
  - Projects the same gates into actual continuation / same-type creation prompt context as a compact `Universal novel workflow contract`.
  - Makes mode selection, chapter contract, scene exit-state, reader micro-payoff, revision order, natural prose pass, and progress write-back visible before generation.

## Verification targets

```powershell
python -m pytest backend/tests/services/test_source_discovery_service.py::test_local_universal_novel_writing_skill_is_static_absorbed -q
python -m pytest backend/tests/frontend/test_source_discovery_panel_copy.py::test_source_discovery_panel_surfaces_universal_novel_writing_gates -q
python -m pytest backend/tests/services/test_book_remix_context_service.py::test_build_remix_continuation_context_block_renders_universal_novel_workflow_contract -q
```
