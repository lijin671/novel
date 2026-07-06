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
  - Adds a concrete `Universal next chapter scaffold` for continuation prompts by deriving the next chapter job, reader promise, opening hook, scene-plan rule, payoff debt, forbidden contradiction, and write-back requirement from the confirmed bible and continuation plan.
  - Adds a `Universal same-type creation scaffold` for inspired prompts so同类型仿写 rebuilds reader promise, protagonist want/need, opposition, chapter contract, hook/payoff ledger, and project-local continuity instead of carrying source canon into the new work.
  - Adds `chapter_progress_report_completeness` to continuation control audit when `progress_report_continuity_writeback_gate` is active. It reports missing accepted-chapter write-back fields before canon reuse.
  - Adds `Universal progress report completeness gate` to continuation context so drafts cannot silently skip summary, new facts, character changes, hook deltas, continuity updates, next focus, measurable length, or risk review.
  - Adds `Universal continuation handoff gate` so continuation drafting reads the latest accepted chapter boundary before drafting. If the prior chapter ended mid-scene, the next context now preserves exact location, physical/emotional state, hook handling, and skip-ahead/time-jump boundary; Chinese and English mid-scene markers are both recognized.
  - Deepens the `Universal same-type creation scaffold` with a target-owned story-promise packet, independent hook/payoff ledger, and minimum-difference gate for cast, organizations, world rules, conflict object, event order, reveal route, and payoff owner.

## 2026-06-15 deep fusion addendum

The local source was re-read statically from `D:\project\universal-novel-writing`
without install, clone, provider call, MCP/browser/desktop runtime, or prompt body
transplant. Hashes remained unchanged from the original intake snapshot above.

Additional reusable pattern fused into MuMuAINovel:

- The `chapter-workflow.md` scene beat sheet is now projected as a concrete
  next-chapter planning surface, not only as a generic "3-7 scenes" rule.
- `book_remix_context_service.py` renders accepted `scene_beats`, `scene_plan`,
  `scenes`, or `beat_sheet` rows into `Universal next chapter scaffold` with:
  scene, POV, location/time, goal, obstacle, tactic, turn, cost, and exit state.
- The continuation control audit now treats an existing scene beat sheet as
  structured, while still warning on incomplete beat fields such as missing
  tactic, cost, or exit state.
- This improves continuation handoff quality because the next chapter prompt can
  preserve exact scene-level pressure instead of collapsing it into a single
  pending beat.
- Same-type implications remain boundary-only: source scene beat shape is a
  craft axis; target stories must rebuild scene goals, obstacles, tactics, costs,
  exit routes, characters, organizations, and payoff owners independently.

## 2026-06-17 reader-pull prewrite fusion addendum

The local source was re-read statically from `D:\project\universal-novel-writing`
without install, clone, provider call, MCP/browser/desktop runtime, or prompt body
transplant. The relevant source surface is the `revision-checklists.md`
fresh-reader test: a reader should be able to answer POV, current want,
obstacle, why it matters, what changed, and what question or desire pulls
onward.

Additional reusable pattern fused into MuMuAINovel:

- `book_remix_context_service.py` now projects the fresh-reader test into the
  `Universal next chapter scaffold` as `reader_pull_prewrite_checklist`.
- Continuation prompts can carry concrete answers for POV, want, obstacle,
  stakes, changed exit state, and next pull before drafting, instead of waiting
  until post-draft review to discover reader-pull gaps.
- `Universal reader-pull fresh-reader gate` now uses the exact six-question
  review wording and states the no-story-bible-context expectation.
- Same-type creation now gets a `same_type_reader_pull_matrix`: target POV,
  want, obstacle, stakes, changed exit state, and next pull must be rebuilt as
  target-owned material. Source reader pull may define question shape only, not
  answer content.
- `book_remix_service.py` deconstruction packs now use the same final reader
  question: `What question or desire pulls me onward?`.

## Verification targets

```powershell
python -m pytest backend/tests/services/test_source_discovery_service.py::test_local_universal_novel_writing_skill_is_static_absorbed -q
python -m pytest backend/tests/frontend/test_source_discovery_panel_copy.py::test_source_discovery_panel_surfaces_universal_novel_writing_gates -q
python -m pytest backend/tests/services/test_book_remix_context_service.py::test_build_remix_continuation_context_block_renders_universal_novel_workflow_contract -q
python -m pytest backend/tests/services/test_book_remix_context_service.py::test_build_remix_continuation_context_block_projects_universal_next_chapter_scaffold backend/tests/services/test_book_remix_context_service.py::test_build_remix_inspired_context_block_renders_universal_same_type_scaffold -q
python -m pytest backend/tests/services/test_book_remix_context_service.py::test_build_remix_continuation_control_audit_flags_universal_progress_report_gaps backend/tests/services/test_book_remix_context_service.py::test_build_remix_continuation_context_block_renders_universal_progress_report_gap_gate -q
python -m pytest backend/tests/services/test_book_remix_context_service.py::test_universal_continuation_handoff_preserves_mid_scene_state_and_hook_decision backend/tests/services/test_book_remix_context_service.py::test_universal_continuation_handoff_warns_when_mid_scene_resume_state_is_missing backend/tests/services/test_book_remix_context_service.py::test_universal_continuation_handoff_accepts_chinese_mid_scene_and_skip_boundary_terms -q
python -m pytest backend/tests/services/test_book_remix_context_service.py::test_universal_next_chapter_scaffold_projects_structured_scene_beat_sheet -q
python -m pytest backend/tests/services/test_book_remix_context_service.py::test_universal_next_chapter_scaffold_projects_reader_pull_prewrite_checklist backend/tests/services/test_book_remix_context_service.py::test_build_remix_inspired_context_block_renders_same_type_reader_pull_matrix backend/tests/services/test_book_remix_context_service.py::test_build_remix_continuation_context_block_renders_universal_reader_pull_gate backend/tests/services/test_book_remix_service.py::test_deconstruction_pack_for_continuation_surfaces_universal_contract -q
```


## 2026-06-17 workflow reader-pull enforcement addendum

The local source was re-read statically from `D:\project\universal-novel-writing`
without install, clone, provider call, MCP/browser/desktop runtime, or prompt body
transplant.

Additional reusable pattern fused into MuMuAINovel:

- `novel_workflow_service.py` now carries the fresh-reader six-question test
  into the live chapter workflow reader panel through `reader_pull_answers`.
- When `reader_pull_fresh_reader_gate` is active in the public source pattern
  pack, `_aggregate_feedback` treats missing POV, current want, obstacle,
  stakes, changed exit state, or pull-forward answers as a blocking revision
  reason even if numeric scores pass.
- `_build_revision_brief` now emits a targeted `Reader-pull repair` section so
  auto-regeneration repairs the visible on-page reader promise instead of only
  raising generic pacing or engagement advice.
- Existing tests that monkeypatch the reader panel with the older two-argument
  shape remain supported by a compatibility wrapper.

Verification targets added:

```powershell
python -m pytest backend/tests/services/test_novel_workflow_unlimited_review_policy.py -q
python -m pytest backend/tests/services/test_book_remix_context_service.py backend/tests/services/test_book_remix_service.py backend/tests/services/test_novel_workflow_unlimited_review_policy.py -q
```

## 2026-07-06 workflow post-draft review enforcement addendum

The local source was re-read statically from `D:\project\universal-novel-writing`
without install, clone, provider call, MCP/browser/desktop runtime, prompt body
transplant, or source prose import.

Additional reusable pattern fused into MuMuAINovel:

- `novel_workflow_service.py` now carries the portable post-draft acceptance
  packet into the live reader panel through `post_draft_review_packet`,
  `mobile_readability_review`, and `least_destructive_repair_scope`.
- When `post_draft_review_checklist_gate` is active in the public source
  pattern pack, `_aggregate_feedback` treats missing post-draft review evidence
  as a blocking revision reason even if numeric reviewer/reader scores pass.
- `_build_revision_brief` now emits a targeted `Post-draft review repair`
  section so auto-regeneration repairs the missing acceptance evidence instead
  of only optimizing generic pacing, reader-pull, or style issues.
- The gate follows the universal revision order: prove structure, continuity,
  POV, voice, conflict, pacing, reader-pull, hook/payoff, prose naturalness,
  and mobile readability from visible page evidence; repair the smallest
  failing artifact first.

Verification targets added:

```powershell
python -m pytest backend/tests/services/test_novel_workflow_unlimited_review_policy.py -q
python -m pytest backend/tests/services/test_book_remix_context_service.py backend/tests/services/test_book_remix_service.py backend/tests/services/test_novel_workflow_unlimited_review_policy.py -q
```

## 2026-07-06 pattern-pack baseline preservation addendum

The 2026-07-06 source-pattern refresh is a narrow metadata/static-intake
snapshot. It should update freshness without dropping durable gates already
absorbed from earlier universal-novel-writing passes.

Additional reusable pattern fused into MuMuAINovel:

- `source_discovery_service.py` now merges the latest pattern pack with recent
  prior packs when loading prompt guidance.
- Latest values still win for timestamps, current source titles, and duplicate
  workflow gates.
- Older unique workflow gates and hint lists remain available, so a narrower
  refresh cannot silently remove continuation, hook-integrity, revision, or
  same-type safety rules.
- This preserves deep拆书续写 / 同类型仿写 guidance even when a later discovery
  run contains only metadata-level evidence.

Verification target added:

```powershell
python -X utf8 -m pytest backend/tests/services/test_source_discovery_service.py::test_load_latest_pattern_pack_preserves_previous_baseline_when_refresh_is_narrower -q
```

## 2026-07-06 deep baseline merge metadata addendum

The local source was re-read statically from `D:\project\universal-novel-writing`
without install, clone, provider call, MCP/browser/desktop runtime, prompt body
transplant, or source prose import.

Additional reusable pattern fused into MuMuAINovel:

- Pattern-pack loading now keeps a six-file baseline window instead of the
  latest three files, so earlier `local/universal-novel-writing` gates such as
  scene goal/obstacle/cost/exit, subgenre ledgers, and progress writeback are
  still active after later narrow metadata refreshes.
- `load_latest_pattern_pack_artifact()` now reports
  `merged_pattern_pack_count`, `preserved_workflow_pattern_count`, and
  `preserved_hint_key_count`, with compact preserved-name/key previews.
- The source-discovery panel surfaces the same merge metadata, making it visible
  when a current refresh is using older durable baseline gates.
- This is still pattern-only: source workflow contracts may shape拆书续写 and
  同类型仿写 gates, but external files, prompt bodies, manuscript prose,
  scripts, installers, providers, browser/MCP runtimes, and credentials remain
  excluded.

Verification targets added:

```powershell
python -X utf8 -m pytest backend/tests/services/test_source_discovery_service.py::test_load_latest_pattern_pack_preserves_universal_baseline_beyond_three_files -q
python -X utf8 -m pytest backend/tests/frontend/test_source_discovery_panel_copy.py::test_source_discovery_panel_surfaces_pattern_pack_merge_metadata -q
```
