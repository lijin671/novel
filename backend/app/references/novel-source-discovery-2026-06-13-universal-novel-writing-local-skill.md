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

## 2026-07-06 local-reference coverage trace addendum

The local source was re-read statically from `D:\project\universal-novel-writing`
without install, clone, provider call, MCP/browser/desktop runtime, prompt body
transplant, or source prose import.

Additional reusable pattern fused into MuMuAINovel:

- Pattern packs now expose `local_reference_coverage` so a narrow refresh can
  still show which local static references contributed durable workflow gates.
- `source_discovery_service.py` records title, path/url, posture hint, file
  counts, hash counts, matched workflow gates, risk flags, and trust flags for
  local references.
- Old pattern packs without explicit coverage are backfilled from merged
  `workflow_patterns[*].sources`, so the current source-discovery panel can
  display `local/universal-novel-writing` coverage without rewriting historical
  JSON snapshots.
- `source_pattern_pack_prompt.py` renders a compact
  `local_reference_coverage` digest before the broader hint list, making
  universal mode contracts, chapter contracts, progressive loading, reader
  promise, and same-type boundary gates traceable in prompts.
- The source-discovery panel adds a "本地参考融合覆盖" card and count. This is
  visibility only; it does not install, execute, import runtime code, or treat
  external prompts/prose as project canon.

Verification targets added:

```powershell
python -X utf8 -m pytest backend/tests/services/test_source_discovery_service.py::test_local_universal_novel_writing_skill_is_static_absorbed backend/tests/services/test_source_discovery_service.py::test_load_latest_pattern_pack_preserves_universal_baseline_beyond_three_files -q
python -X utf8 -m pytest backend/tests/frontend/test_source_discovery_panel_copy.py::test_source_discovery_panel_surfaces_pattern_pack_merge_metadata -q
```

## 2026-07-06 graphify-novel static graph/bible addendum

Source reviewed statically: `https://github.com/Anshler/graphify-novel`

Observed metadata on 2026-07-06:

- HEAD: `124c9abc473508e081a625e4d2a24b24071581a2`
- Default branch: `master`
- License: `MIT`
- Stars/forks: `47` / `14`
- Root markers: `README.md`, `README.vi.md`, `SKILL.md`, `LICENSE`

Posture:

- Pattern-only static intake.
- No clone, package-manager install, `npx skills add`, `pip install graphifyy`,
  graphify runtime, MCP/browser/desktop runtime, provider call, graph export import,
  prompt-body transplant, user manuscript import, cookie/token read, or credential read.

Reusable patterns fused into MuMuAINovel:

- `bible/` is modeled as structured source-of-truth state.
- `graphify-out/` is modeled as a derived relationship graph, not canon.
- `draft/` and `static/` stay excluded from canon graph extraction by default.
- Review findings stay proposals until accepted with chapter/source evidence,
  intent, changed bible slice, thread status delta, and graph rebuild evidence.
- Whole-book review can now ask for `bible_graph_dual_layer_report`,
  `thread_status_graph_consistency_findings`, and `draft_static_exclusion_audit`.
- Same-type creation remaps bible state, graph topology, thread statuses,
  relationship paths, structural hubs, and unresolved setups instead of copying
  source nodes, slugs, paths, or prose.

Verification targets added:

```powershell
python -X utf8 -m pytest backend/tests/services/test_source_discovery_service.py::test_static_book_writing_graph_rights_vscode_sources_map_to_workspace_gates -q
```

## 2026-07-06 NovelOS static war-room/future-scene addendum

Source reviewed statically: `https://github.com/Colinsss-Qin/NovelOS`

Observed metadata on 2026-07-06:

- HEAD: `4eb3439ef61a69dbae320bff611a707feac90db0`
- Default branch: `mian`
- License: no license file observed
- Stars/forks: `0` / `0`
- Root markers: `.mcp.json`, `CLAUDE.md`, `PRD_v0.2.txt.md`,
  `project_rules.md`, `package.json`, `prisma`, `src`
- Static hashes sampled: `PRD_v0.2.txt.md`
  `e4c2a191ccd0f7b37a04f60bed21d092b686c1df2d9d5e7a5e901d5f9a4feb53`;
  `project_rules.md`
  `e33e7c3f2991ff06591a150ffbacee3884e3530109bb8e49b762447f4fb0c564`

Posture:

- Pattern-only static intake.
- No clone, npm install/setup, Prisma command, MCP/server launch, Node/SQLite
  runtime, provider call, CLAUDE instruction import, local memory/cache read,
  script execution, cookie/token read, or credential read.

Reusable patterns fused into MuMuAINovel:

- Keep War Room, Story Bible, Story Map, Future Scene, and Writing Studio as
  separate planning surfaces.
- Generated chapters should link to current chapter task, recent accepted
  chapters, world/character state, and tag-matched Future Scene candidates.
- Future Scene items are candidate beats, not canon, until accepted with task id,
  affected canon slice, and chapter placement evidence.
- Same-type creation rebuilds stage boards, task links, future-scene tags,
  world-state keys, and chapter placement for the transformed book instead of
  copying source boards, localStorage keys, memory summaries, or scene entries.

Verification targets added:

```powershell
python -X utf8 -m pytest backend/tests/services/test_source_discovery_service.py::test_static_novelos_war_room_future_scene_source_maps_to_task_context_gates -q
```


## 2026-07-06 show-me-the-story foreshadowing / narrative-memory addendum

Source reviewed statically: `https://github.com/Nigh/show-me-the-story`

Observed metadata on 2026-07-06:

- HEAD: `01e32723d53a0f179393cd154fd8546243333372`
- Default branch: `main`
- License: `MIT`
- Stars/forks via public GitHub API: `300` / `27`
- Latest observed pushed timestamp: `2026-07-06T12:07:01Z`
- Raw samples:
  - `README.md` status `200`, bytes `21087`, sha256
    `7e30de4e860a9c5d46dddb2b0016d6b88230fe7fd44cda160362d793a4afbe54`
  - `go.mod` status `200`, bytes `33`, sha256
    `7c1a838dda241c6d0cf6c0e6ecb06e2e85b411068fedc8adc72d0d4aa4a1e1ca`
  - `prompts.go` status `200`, bytes `28976`, sha256
    `ea24447d560bd0375641c82379a88c64752b13c7cddb2d263a1045fff1d486bf`
  - `LICENSE` and `prompts_en.go` raw probes returned `429`; no token, proxy,
    retry storm, or bypass was used.

Posture:

- Pattern-only static intake.
- No clone, Go build, binary execution, package install, browser/local-storage
  access, provider/model call, prompt-body transplant, generated story import,
  cookie/token read, or credential read.

Reusable patterns fused into MuMuAINovel:

- Two-stage creation gate: full-book outline approval, chapter draft, summary,
  fact-check, then accept/revise.
- Foreshadowing is now represented as a lifecycle ledger with seed, advance,
  payoff, active window, overdue counter, and accepted evidence.
- Narrative memory refresh happens only after an accepted chapter; revision
  invalidates stale extracted memory and triggers re-extraction.
- Selected-text revision prefers paragraph-scoped patching; whole-chapter
  fallback must record why the narrower patch was insufficient.
- Key setting changes generate compatible setting deltas and mark unwritten
  chapter outlines stale until coordination completes.
- Same-type creation remaps foreshadowing ids, memory details, paragraph scopes,
  and setting deltas before drafting, and rejects source memory, summaries,
  paragraph text, or diff examples as target canon.

Verification targets added:

```powershell
python -X utf8 -m pytest backend/tests/services/test_source_discovery_service.py::test_static_show_me_story_source_adds_foreshadow_memory_gates -q
```


## 2026-07-06 ai-novel-diagnosis retention triage addendum

Source reviewed statically: `https://github.com/myyimu/ai-novel-diagnosis`

Observed metadata on 2026-07-06:

- HEAD: `03c9d1f3b5db0594909b58e49fc4208e85fd9856`
- Default branch: `master`
- License: `MIT` in raw `LICENSE`; public API returned `NOASSERTION`
- Stars/forks via public GitHub API: `12` / `0`
- Latest observed pushed timestamp: `2026-07-06T10:02:56Z`
- Language: `TypeScript`
- Root markers via contents API: `.env.example`, `AGENTS.md`, `CLAUDE.md`,
  `README.md`, `LICENSE`, `apps`, `docs`, `fixtures`, `one.manifest.json`,
  `package.json`, `pnpm-lock.yaml`, `scripts`, `services`, `skills`
- Raw samples:
  - `README.md` status `200`, bytes `21731`, sha256
    `823ef416f8743da2ccb445d4ce60b75b04c34cb69ac7feb914f6835447f0c420`
  - `LICENSE` status `200`, bytes `1215`, sha256
    `e9f11577bf9e7fced52025175e2e063211d5e899eb0b4bd657f77a890c94d4bc`
  - `package.json` status `200`, bytes `3033`, sha256
    `63a69d380e3c2af9271d8ebe3de2e9704130fc9efa6ee2fe4e4501e45ea59bda`
  - `pnpm-lock.yaml` status `200`, bytes `392003`, sha256
    `6f0e68ea2d578bff2fc82bc59ff9fc2c1c0f39ad56d29d9de02e3f13dca3be71`
  - `docs/product-positioning-ai-draft-diagnosis.md` status `200`, bytes
    `14168`, sha256
    `a13dbba85cb3d6341db649b69875274499ef047d23d581d6e54c3db3798f52b1`
  - `docs/diagnosis-workflow-implementation-plan.md` status `200`, bytes
    `16141`, sha256
    `94cea1405b754c6df74c5a1623dc5a0a57caaffaa4c80c7ba85352ce4f156333`
  - `docs/product-review-roadmap.md` status `200`, bytes `15567`, sha256
    `a90c0e6150512fbb566d8cea6cdfa7ac8166e9dcfd9accdde272bc63084a0bae`
  - `docs/book-disassembly-comprehension-review.md` status `200`, bytes
    `18216`, sha256
    `78ba90a012f728812f81936840adcf2af172cd97c82508781afa2930797a8aab`
  - directory raw probes for `src`, `docs`, and `fixtures/novel-diagnosis`
    returned `404` because raw URLs address files, not directories; one `docs`
    raw probe returned `429` and was treated as no-bypass/no-token.

Posture:

- Pattern-only static intake.
- No clone, checkout, pnpm/One CLI install, script execution, Docker/DB service,
  API/Web runtime, provider/model call, uploaded manuscript/example chapter
  import, prompt-body transplant, generated report import, cookie/token read, or
  credential read.

Reusable patterns fused into MuMuAINovel:

- Diagnose before rewrite: every weak opening or continuation issue carries
  problem, text evidence, reader reaction, revision priority, rewrite prompt,
  and rediagnosis checkpoint as one traceable chain.
- Gate decisions are revision-priority suggestions such as continue, modify,
  restructure, or scrap; they are not platform traffic predictions.
- Rewrite prompts are generated from concrete evidence and remain candidate edit
  instructions until rediagnosis proves the tracked issue changed.
- Repeated verified issues can become methodology cards; one-off model opinions
  cannot silently become durable writing rules.
- Mature-sample disassembly extracts reusable structure, character function,
  relationship evolution, world/timeline organization, and a do-not-copy list;
  source content stays outside target canon.
- Same-type creation remaps diagnosis categories, reader-impact signals, rewrite
  prompts, and method cards into target-owned evidence ids, rejecting source
  reports, example chapters, prompt text, mind-map labels, or relationship
  storyline content as target material.

Verification targets added:

```powershell
python -X utf8 -m pytest backend/tests/services/test_source_discovery_service.py::test_static_ai_novel_diagnosis_source_adds_retention_triage_gates -q
```

## 2026-07-06 open-novel-fanqie static benchmark-author gate addendum

Source reviewed statically: `https://github.com/mosonlab/open-novel-fanqie`

Observed metadata on 2026-07-06:

- HEAD/default branch observed through public GitHub API: `main`
- Latest observed pushed timestamp: `2026-06-12T13:10:19Z`
- Public API stars/forks: `11` / `2`
- License: `MIT`
- Language: `TypeScript`
- Root markers: `.claude`, `.env.example`, `LICENSE`, `README.md`, `SOP.md`, `assets`, `demo`, `scripts`, `书`, `对标`
- Static samples:
  - `README.md` bytes `7115`, sha256
    `95f9d13c778f7d77531604abcbb4c708b82772be3e80fa384117e39411ed2a59`
  - `SOP.md` bytes `11556`, sha256
    `6a7312e15e2f4d0b3800431f5d8c69229a37ecc4d3f754443b376ed3a08959ad`
  - `对标/说明.md` bytes `1170`, sha256
    `52f1d378446e805cbcc8694d0eba319966ade32e9f6bd068cdfafd42fa1d39b6`
  - `.claude/skills/open-novel-fanqie/SKILL.md` bytes `8903`, sha256
    `3850624d5024d5d75a1fcf831885d4e499cbe8e6dbdc6cb2c7a2067487fc10ed`
  - `.claude/skills/p1-拆书/SKILL.md` bytes `14336`, sha256
    `a944329f577a674e779f7550f5bd2446c9b7033225be42313fc45d1cf5b96ff2`
  - `.claude/skills/p1b-换壳切入/SKILL.md` bytes `7902`, sha256
    `41e8d0be6584ab54b4afc8741bfc8d268075738c46b6a15948815104c70171e9`
  - `.claude/skills/p6-审稿/SKILL.md` bytes `6715`, sha256
    `7dad32b22ac8dc21c88b58ad8ffed36be9c383337b3b4c1e40d597907d51adb7`
  - `.claude/skills/p8-活文档/SKILL.md` bytes `17151`, sha256
    `03e1a73ea5765efe572d978408f60d3aaf867939d88d11279f96f3517483cd10`
  - raw `LICENSE` returned `429`; public API license was used without token,
    proxy, retry storm, or bypass.

Posture:

- Pattern-only static intake.
- No clone, bun/Claude setup, package install, shell script execution,
  novelcatch.com browsing, provider/model call, benchmark manuscript import,
  demo story import, upstream skill prompt-body transplant, cookie/token read,
  or credential read.

Reusable patterns fused into MuMuAINovel:

- Benchmark deconstruction is now treated as abstract structure only: first-three
  chapter hook engine, optional ≤60-chapter long-run evidence, emotional rhythm,
  and loop formulas may guide process but cannot bring over names, settings,
  event order, or prose.
- Same-type creation now carries explicit author stop-gates for shell-swap
  choice, premise direction, event-bank selection, scene-script lock, and
  hard-flaw repair before drafting continues.
- Chapter generation now gets a scene-script density gate: visible action,
  dialogue hook, emotion rhythm, conflict, payoff, and exit pull must exist
  before prose drafting.
- Continuation context now favors target-owned tone/style cards, character cards,
  ≤300-word event summary, dense scene script, and previous tail; benchmark
  manuscripts, demo chapters, ranking snapshots, and upstream skill bodies stay
  out of draft context.
- Rolling live-document cadence is surfaced as state: every chapter updates the
  event summary, and every 10 chapters require independent hard-flaw review plus
  setting-card refresh before the next continuation block.

Verification targets added:

```powershell
python -X utf8 -m pytest backend/tests/services/test_source_discovery_service.py::test_static_open_novel_fanqie_source_adds_benchmark_author_gate -q
```

## 2026-07-06 Neupen static parallel-memory reader gate addendum

Source reviewed statically: `https://github.com/FantasyLu/neupen`

Observed metadata on 2026-07-06:

- Public `git ls-remote` HEAD for `refs/heads/main`:
  `afd48066f5f483c5b0418f64466bc41f33d5f08e`
- GitHub Search metadata: stars/forks `0` / `0`, latest observed pushed
  timestamp `2026-07-06T09:41:28Z`, license `MIT`, language signal from
  repository description only because the direct repository API returned `403`.
- Direct GitHub repository API returned `403`; this was treated as a rate-limit
  or access boundary. No token, proxy, retry storm, or bypass was used.
- Raw samples:
  - `README.md` status `200`, bytes `64163`, sha256
    `6b77cef18aea0ebd66e78fed8291745fe80efd9eba0c2c8088ad1f904b1df15d`
  - `LICENSE` status `200`, bytes `1066`, sha256
    `f23a21bb92b92add9fa61c5303847d024732c8652067a4b3a9b9a3cb0721d6df`
  - `.env.example` status `200`, bytes `1747`, sha256
    `5247d273409b8c71bb61887adef019b77545c0a141244ee1eb64252367c51063`
  - `package.json` and `pnpm-lock.yaml` raw probes returned `404`; no package
    manager was run.

Posture:

- Pattern-only static intake.
- No clone, Docker/Streamlit/macOS app launch, package install, script
  execution, provider/model call, embedding/vector write, uploaded style sample
  import, generated chapter import, collaboration-account use, cookie/token
  read, or credential read.

Reusable patterns fused into MuMuAINovel:

- Continuation context can now be audited as three explicit layers: L1 permanent
  canon, L2 recent chapter summaries, and L3 selected semantic fragments. Each
  injected item needs a source id, relevance reason, and token cap.
- Review is modeled as four independent dimensions: plot alignment,
  character/world guard, continuity tracking, and AI-style refinement. Any
  rejected dimension requires a full rerun of all dimensions before acceptance,
  avoiding stale partial-pass evidence.
- Foreshadowing now gets deadline state vocabulary: active, due-soon, overdue,
  collected, or abandoned, so chapter planning must either use, defer with
  reason, or resolve the item.
- Reader simulation is acceptance evidence only when personas, scoring
  dimensions, highlighted strengths, and concrete revision suggestions are tied
  to the accepted target chapter.
- Style transfer remains a structured style profile; uploaded reference prose is
  not reused as prompt context once the profile exists.
- Same-type creation remaps memory layers, review dimensions, foreshadow
  deadlines, style-profile axes, and reader personas into target-owned records;
  source SQLite rows, LanceDB fragments, uploaded style text, reader-score
  examples, provider settings, collaboration comments, and generated chapters
  stay outside target canon.

Verification target added:

```powershell
python -X utf8 -m pytest backend/tests/services/test_source_discovery_service.py::test_static_neupen_source_adds_parallel_memory_reader_gate -q
```

## 2026-07-06 local universal writing reread and Neupen fusion addendum

The local source `D:\project\universal-novel-writing` was re-read statically
after the Neupen pass. The six reviewed files still match the original SHA-256
snapshot recorded above. No install, clone, package execution, script run,
provider/model call, browser/MCP/desktop runtime, prompt-body transplant,
manuscript import, cookie/token read, or credential read occurred.

Additional fusion result:

- Neupen's L1/L2/L3 memory packet is treated as a context-assembly layer, while
  `universal-novel-writing` remains the authoring contract for mode, chapter
  job, reader promise, scene beats, revision order, and progress write-back.
- Parallel review dimensions now complement the universal post-draft acceptance
  order: plot alignment maps to developmental/structure evidence, character
  guard maps to want/need/wound/world-rule evidence, continuity tracking maps to
  ledger/write-back evidence, and style refinement maps to anti-AI naturalness
  without copying source prose.
- Reader simulation remains a reviewer lens only. It must answer the universal
  fresh-reader questions from the target page before it can support acceptance.
- Foreshadowing deadlines inherit the universal hook/payoff ledger discipline:
  every due-soon or overdue thread must be paid off, escalated, deferred with
  reason, or explicitly abandoned before the chapter is treated as accepted.
- Same-type creation now has a clearer precedence rule: source projects may
  supply method shape, but target-owned reader promise, protagonist pressure,
  world rules, scene goals, payoff route, memory ids, review ids, and reader
  scorecards must be rebuilt before drafting.
- The prompt digest now renders a wider inspired-mapping target window so older
  universal remap gates are not hidden when newer Neupen remap targets are
  appended to the same pattern pack.

Verification targets added:

```powershell
python -X utf8 -m pytest backend/tests/services/test_source_discovery_service.py::test_static_neupen_source_adds_parallel_memory_reader_gate -q
python -X utf8 -m pytest backend/tests/services/test_source_discovery_service.py -q
```

## 2026-07-06 Scriveno static voice/context/status gate addendum

Source reviewed statically: `https://github.com/hannsxpeter/scriveno`

Observed metadata on 2026-07-06:

- Public `git ls-remote --symref HEAD` default branch: `main`
- Public `git ls-remote` HEAD:
  `a4469d886a02e1c3109156385b0d0affe3b492af`
- GitHub repository API metadata: stars/forks `9` / `2`, pushed timestamp
  `2026-06-27T02:22:29Z`, license `MIT`, language `JavaScript`, topics include
  `creative-writing`, `novel`, `publishing`, `translation`, `codex`, and
  `claude-code`.
- Top-level API markers include `README.md`, `LICENSE`, `AGENTS.md`,
  `CLAUDE.md`, `package.json`, `package-lock.json`, `commands`, `agents`,
  `docs`, `lib`, `scripts`, and `templates`.
- Static samples saved only under `tmp/source-intake-scriveno-20260706`:
  - `README.md` bytes `20711`, sha256
    `a0221d849e3646437241ce8b49377c343415ea1e2e9c104f3e70a5baa371f13e`
  - `LICENSE` bytes `1078`, sha256
    `2ceb75aad90a37a31466327d411a995400174219bc21c2a920d6a1510431e097`
  - `docs/creative-context.md` bytes `12545`, sha256
    `324945b415b59057d5545018c29a0896577d00351ebb098e60207593ea8a8783`
  - `docs/voice-dna.md` bytes `22250`, sha256
    `bbfdb349f72cfd6ed51c1d5081d5c52696666dfacd2182837e565549a5e44024`
  - `docs/auto-invoke-policy.md` bytes `10147`, sha256
    `c4ea2d80d607185fc33da95d82ecf1558979971413edc559f8d70bf519b606ac`
- Direct `raw.githubusercontent.com` returned `429` for some probes; this was
  treated as a no-bypass rate boundary. The review used GitHub API raw content
  for the bounded files above and did not use tokens, proxies, clones, or retry
  storms.

Posture:

- Pattern-only static intake.
- No clone, npm/npx install, package script execution, runtime smoke command,
  agent prompt import, provider/model call, proof-demo import, generated prose
  import, publishing package generation, local manuscript read, cookie/token
  read, or credential read.

Reusable patterns fused into MuMuAINovel:

- Voice DNA becomes a target-owned voice sovereignty gate: `STYLE-GUIDE.md`
  loads before outline, cast, record, translation, polish, or weaker-rule
  scaffolds. `WRITING-RULES.md` and pitfall packs may support but cannot
  override accepted author voice.
- `RECORD.md` is absorbed as an established-content store for open threads,
  reader promises, payoffs, continuity facts, movement, and next-unit
  obligations. Continuation context should cite these obligations before
  accepting a draft.
- Creative Context labels are mapped to project-native craft notes:
  `CHOICE` constrains, `HUNCH` tests, `QUESTION` blocks only when marked
  blocking, and `WATCHPOINT` travels into post-draft review.
- A next/status route is read-only by default and must separate candidate agents,
  candidate local helpers, and manual gates before any action mutates manuscript
  state.
- Same-type creation remaps voice dimensions, record-thread obligations,
  craft-note labels, route status, and work-type vocabulary into target-owned
  files. Source command bodies, proof demos, agent prompts, route labels,
  publishing metadata, local manuscript paths, and style-guide examples stay
  outside target canon.

Verification target added:

```powershell
python -X utf8 -m pytest backend/tests/services/test_source_discovery_service.py::test_static_scriveno_source_adds_voice_context_status_gate -q
```


## 2026-07-06 AI-novel-predict static memory/simulation/branch addendum

Source reviewed statically: `https://github.com/we1005/AI-novel-predict`

Observed metadata on 2026-07-06:

- Public `git ls-remote --symref HEAD` default branch: `main`
- Public `git ls-remote` HEAD:
  `002210566ce7160b324e9edbf6da2676fe7e4789`
- Raw README status `200`, bytes `32669`, sha256
  `43f2674b2293292c2f90c1dbfe7015b1d83aa60c278c8847d049debd2063d7cb`
- Static README markers include structured memory before context, 21 LLM
  agents, L1 SQLite, L2 FTS5 trigram, Graph Projection, 6-agent
  incremental extraction, Writer plus style/plot/consistency reviewers plus
  Editor arbitration with <=3 rewrites, role simulation, Mystery Agent,
  chapter write-back into memory, git-backed baseline plus increments,
  deterministic materialize rebuild, chapter rollback, branch-as-derived-book
  isolation, `book_scope`, MoXi cross-book analysis, style genome, and
  `voice_only` style transfer.

Posture:

- Pattern-only static intake.
- No clone, checkout, backend/frontend launch, package install, Docker run,
  database service, provider/model call, demo chapter import, prompt-body
  transplant, generated prose import, API key read, book database read, cookie
  read, token read, or credential read.

Reusable patterns fused into MuMuAINovel:

- Structured memory is promoted as a pre-context gate: continuation context must
  cite target-owned canon, search/recent summaries, graph facts, and per-chapter
  increments before drafting.
- Role simulation is constrained by character knowledge scope: desire, fear,
  voice, `secrets_known`, `secrets_hidden`, and accepted facts visible to that
  character.
- Draft acceptance now models Writer, style/plot/consistency reviewers, and
  Editor arbitration with bounded rewrite count and explicit memory write-back.
- Git-backed manuscript source and rebuildable memory cache stay separate;
  baseline plus increments should be replayable through a materialize-style
  audit before rollback or branch promotion.
- Branch exploration is isolated as a derived book or namespace. Drafts,
  extracted facts, foreshadowing, and callbacks cannot bleed across
  `book_scope`.
- Same-type imitation may transfer abstract style axes and genre mechanics in a
  `voice_only` mode, but source plot arcs, characters, demo chapters, prompt
  bodies, memory rows, branch names, and generated prose remain outside target
  canon.
- `D:\project\universal-novel-writing` remains the authoring contract above
  this memory/simulation layer: mode, chapter job, reader promise, scene beat,
  revision order, fresh-reader pull, and progress write-back decide whether the
  generated unit can be accepted.

Verification target added:

```powershell
python -X utf8 -m pytest backend/tests/services/test_source_discovery_service.py::test_static_ai_novel_predict_source_adds_memory_simulation_branch_gate -q
```


## 2026-07-06 webnovel-writing-system static file-SOP/waterline addendum

Source reviewed statically: `https://github.com/FeiYun-Novel/webnovel-writing-system`

Observed metadata on 2026-07-06:

- Public `git ls-remote --symref HEAD` default branch: `main`
- Public `git ls-remote` HEAD:
  `6a28e555678fc0b723a435d398b0f24157f10ece`
- GitHub Search metadata showed license `MIT`; direct repository API returned
  `403` and was treated as no-bypass/no-token.
- Raw README status `200`, bytes `9381`, sha256
  `2a9f5c73330bd83d61f0f4e1d91efbe94bf9cba16dcc4ab6fb62458ccf4d2371`
- Raw probes for `LICENSE`, `SKILL.md`, `workflow.md`, and
  `webnovel-writing/SKILL.md` returned `429`; no token, proxy, browser, or
  retry storm was used.
- Static README markers include cross-session state as Markdown files,
  per-chapter SOP, phase checklists, reusable technique-library routing before
  drafting, context waterline green/yellow/red archive policy, multi-subagent
  parallel self-check, reader-perspective review without setting files,
  main-agent mechanical checks, numeric `style_gate.py` rules, style sample
  cards, cool-point threshold questions, and compact chapter summaries.

Posture:

- Pattern-only static intake.
- No clone, checkout, template copy, `CLAUDE.md`/`AGENTS.md` instruction import,
  script execution, package install, provider/model call, upstream workflow text
  import, technique body import, generated prose import, local manuscript read,
  cookie read, token read, or credential read.

Reusable patterns fused into MuMuAINovel:

- Cross-session continuity is now represented as file-state cold start: current
  status, next step, file map, boundaries, chapter progress, character state,
  foreshadowing, event ledger, and unresolved questions must be readable without
  chat memory.
- Every chapter carries visible SOP phase checkpoints. Planning, drafting,
  self-check, sealing, and write-back cannot collapse into one fluent but
  unverified generation step.
- Writing craft is pulled forward: before prose, the target project should build
  a chapter technique list from target-owned technique cards or placeholders.
- Context waterline is now a state gate. Green continues; yellow schedules
  summarization/archive; red archives before more drafting to protect future
  prompt quality and cost.
- Parallel review becomes input-isolated: reader perspective sees only chapter
  text and previous tail, while continuity/style/mechanical checks receive only
  their needed target files.
- Numeric style gates and style sample cards are acceptance evidence only.
  Upstream script code, thresholds, templates, samples, checklist wording, and
  skill instructions remain outside target canon.
- `D:\project\universal-novel-writing` stays the higher authoring contract;
  this addendum strengthens cross-session operation, SOP visibility, waterline
  maintenance, and review isolation around that contract.

Verification target added:

```powershell
python -X utf8 -m pytest backend/tests/services/test_source_discovery_service.py::test_static_webnovel_writing_system_source_adds_file_sop_waterline_gate -q
```


## 2026-07-07 my_novel static brief-handoff/timeline addendum

Source reviewed statically: `https://github.com/Stebaze/my_novel`

Observed metadata on 2026-07-07:

- Public `git ls-remote --symref HEAD` default branch: `main`
- Public `git ls-remote` HEAD:
  `0318e43d37a6b5822103d763e9e8c9183c32f9b5`
- GitHub repository API returned license `Apache-2.0`, stars `0`, pushed
  `2026-07-01T10:58:23Z`.
- Raw README status `200`, bytes `8452`, sha256
  `381a46027be8d4044d81fa98450c0ae381e96dc31ee074b5ee60e9d6306bf2f4`.
- Raw `CLAUDE.md` status `200`, bytes `18062`, sha256
  `0fcdd6c91e453674e54292f772e54fdb4ae83da667d75958d4bf644976884e26`.
- Raw `用户使用指南.md` status `200`, bytes `17240`, sha256
  `a6902f2f28435bd83f4b6e916e4e26c60653cc66c65bf8ec583ae6d8de783b85`.
- Raw `framework/_specs/interaction-spec.md` status `200`, bytes `12827`,
  sha256 `55c20dbaba63108262e0cf552d9f736114052ed875152209ab32a0bcc53b14bc`.
- Raw `framework/_specs/skill-template.md` status `200`, bytes `4421`,
  sha256 `58ee9fc3ad4b79e90276dfdec432b5ee7e9c6d9c64548e9410cf7aefbee692f3`.
- Static markers include author-keeps-pen stance, brief/report-first authoring,
  session entry and state routing, outline-before-chapter, plan -> handoff ->
  generate -> review -> publish, artifact-based resume, eight-field handoff,
  draft/formal layer separation, append-only draft deltas, chapter-versioned
  settings, forward conflict scans, hard/soft blockers, bounded fix loops,
  adaptation source-profile extraction, and single-scene mode.

Posture:

- Pattern-only static intake.
- No clone, checkout, Claude skill installation, package/script execution,
  upstream instruction import, prompt/workflow body import, guide/template text
  import, generated chapter import, local novel data read, author-profile import,
  provider/model call, cookie read, token read, or credential read.

Reusable patterns fused into MuMuAINovel:

- Chapter production now has a stronger artifact state-machine gate. Outline,
  direction, handoff, brief, chapter, review, fix log, and publish state are
  separate receipts instead of one hidden fluent process.
- Handoff is promoted as an explicit session boundary. The next stage must read
  target-owned paths/status fields instead of reconstructing state from chat
  memory or imported command wording.
- Brief-first author control is preserved even when AI-prose mode exists. A run
  should record whether it is brief-only or generated-prose, plus the author
  brief, revision report, and bounded fix-loop status.
- Draft, review, and published manuscript layers remain separate. Free revision
  cannot silently mutate accepted canon or platform-published state.
- Settings now gain chapter-introduction and forward-conflict vocabulary: when a
  fact, power, relationship, or world rule changes after later chapters exist,
  later chapters need an explicit conflict scan.
- Adaptation and同类型仿写 only reuse abstract profiles and target briefs; source
  prose, source skill bodies, upstream command names, local path conventions,
  author profiles, and generated chapter files stay outside target canon.
- `D:\project\universal-novel-writing` remains the higher authoring contract;
  this addendum strengthens durable handoff, artifact receipts, layer separation,
  timeline conflict review, and adaptation boundaries under that contract.

Verification target added:

```powershell
python -X utf8 -m pytest backend/tests/services/test_source_discovery_service.py::test_static_my_novel_source_adds_brief_handoff_timeline_gate -q
```

## 2026-07-07 local universal reread and fair-play mystery reader gate addendum

The local source `D:\project\universal-novel-writing` was re-read statically.
The six reviewed files still match the original SHA-256 snapshot recorded above.
No install, clone, package execution, script run, provider/model call,
browser/MCP/desktop runtime, prompt-body transplant, manuscript import,
cookie/token read, or credential read occurred.

Additional static reference reviewed: `https://github.com/ushironoko/novel-harness-skills`

Observed metadata on 2026-07-07:

- Public `git ls-remote --symref HEAD` default branch: `main`
- Public `git ls-remote` HEAD:
  `a550cb79655fde95739369dc196b52f8befead6a`
- GitHub repository API returned `403`; treated as no-bypass/no-token.
- Raw README status `200`, bytes `5731`, sha256
  `cc74cfbaa867dcd315c70e3ced6a9a65b533f459777644b7cac2e2cebd7c9728`.
- Raw `LICENSE` and `LICENSE.md` probes returned `404`; license remains
  no-license-observed for static intake.
- Static README markers include fair-play mystery phases, world/cast/case
  artifacts, clue and lie ledgers, reasoning chains, D1-D10 audit dimensions,
  bounded repair loops, and pre-reveal parallel reader culprit guesses.

Posture:

- Pattern-only static intake.
- No clone, checkout, skill installation, workflow/script execution, prompt-body
  import, skill-body copy, reader-persona wording import, trick example import,
  generated mystery text import, provider/model call, cookie read, token read, or
  credential read.

Reusable patterns fused into MuMuAINovel:

- `D:\project\universal-novel-writing` remains the higher authoring contract:
  genre promise, chapter contract, clue/suspect ledgers, reader-pull test,
  revision order, and minimal rollback decide acceptance.
- `mystery_fair_play_audit_reader_verification_gate` adds mystery-specific
  evidence: fair-play clue-before-solution review, lie ledger, suspect
  motive/means/opportunity, reasoning-chain proof, and pre-reveal reader-guess
  verification.
- Whole-book analysis now has dedicated fair-play clue ledger, reasoning-chain,
  reader-guess, and audit-dimension reports.
- Same-type mystery remaps puzzle architecture only. Target projects must rebuild
  culprit, victim, motive, clue order, red herrings, setting, impossible-trick
  mechanics, reveal route, and payoff owner from the target brief.
- Copy-risk blocks source trick mechanics, clue order, culprit/victim roles,
  explanation structure, audit prompt wording, reader persona wording, skill
  bodies, workflow scripts, and generated mystery text.

Verification target added:

```powershell
python -X utf8 -m pytest backend/tests/services/test_source_discovery_service.py::test_static_novel_harness_skills_source_adds_mystery_fair_play_gate -q
```
