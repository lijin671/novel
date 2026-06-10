# Novel Source Discovery - 2026-06-10 Book Mining / Autopilot / Longrun

## Scope

Static source-intake pass for MuMuAINovel book-deconstruction, continuation, and same-type writing workflows.

No external repository was cloned, installed, executed, or imported. Review used public GitHub metadata, `git ls-remote` HEAD checks, raw README/LICENSE snippets, and GitHub tree metadata only.

## Promoted sources

### `cchheerrss/ai-novel-trilogy`

- URL: https://github.com/cchheerrss/ai-novel-trilogy
- Observed HEAD: `c5e533b36a0bf913e03a51e536322a51d0d52a02`
- License: MIT
- Family: novel automation / book-mining / genesis / continuation pipeline
- Posture: pattern-only
- Static evidence:
  - README describes a three-system lifecycle: book mining, novel genesis, then novel automation.
  - Public tree exposes `book-mining/`, `novel-genesis/`, `novel-automation/`, pattern libraries, canon-seed handoff, and automation gate files.
- Absorbed pattern:
  - `book_mining_genesis_automation_gate`
- Local adaptation:
  - Split source-book deconstruction from new-book canon.
  - Keep pattern library, concept scoring, canon seed, and automation gate decisions as separate artifacts.
  - Source mining notes stay reference-only; only accepted canon seed fields can drive chapter automation.

### `zhitongblog/novel-studio`

- URL: https://github.com/zhitongblog/novel-studio
- Observed HEAD: `df15dde3d618c2704de530e0d2654046c3ce716f`
- License: MIT
- Family: multi-book webnovel studio / autopilot orchestration
- Posture: pattern-only / runtime-deferred
- Static evidence:
  - README describes multi-book longform writing, per-book Unterm profile isolation, Codex/Claude/Gemini CLI orchestration, autopilot continuation, stop limits, and periodic full-book logic checks.
  - Public tree contains desktop/Tauri, CLI, MCP, model, and autopilot surfaces.
- Absorbed pattern:
  - `multi_book_autopilot_studio_gate`
- Local adaptation:
  - Add per-book profile boundary and context namespace checks.
  - Autopilot must have visible continue limits, stop phrases, manual stop, and periodic full-book logic review.
  - MCP, Tauri, npm, local auth-token, and CLI runtime surfaces remain excluded from intake.

### `DinhLucent/webnovel-longrun-aigen-docs`

- URL: https://github.com/DinhLucent/webnovel-longrun-aigen-docs
- Observed HEAD: `e98081c825ecd8762a0254f4d5bf4692e53fefcf`
- License: GPL-3.0
- Family: long-running webnovel memory / commit projection docs
- Posture: pattern-only
- Static evidence:
  - README describes `.story-system` as source of truth, accepted chapter commits, event/entity extraction, `.webnovel` read-model projections, RAG/query router, memory scratchpad, and read-only dashboard.
  - Public tree is docs-only except license and architecture asset.
- Absorbed pattern:
  - `longrun_commit_projection_health_gate`
- Local adaptation:
  - Accepted chapter commit is the boundary for prose, events, entities, summaries, and memory updates.
  - Source-of-truth files and read-model projections must be separated with freshness checks.
  - Dashboard/read-model surfaces are observational, not canon write surfaces.

## 2026-06-10 reader reward / tri-modal audit addendum

Static pass added two public GitHub sources for the next拆书续写 / 同类型仿写 quality loop.

### `haowjy/creative-writing-skills`

- URL: https://github.com/haowjy/creative-writing-skills
- Observed HEAD: `81fa0be02eeb985404bb3ffc361e62dcba0385e6`
- License: Apache-2.0
- Family: creative-writing skill pack / reader-response review / project knowledge maintenance
- Posture: pattern-only
- Static evidence:
  - README describes muse-led exploration, writer/critic/revision-writer loops, reader-sim feedback, continuity checking, style reference creation, and chronicler knowledge-base updates.
  - Public metadata confirms an external plugin / skill runtime surface, so no skill files, zip files, marketplace commands, or agents were installed or imported.
- Absorbed pattern:
  - `reader_reward_channel_gate`
- Local adaptation:
  - Review pivotal scenes on separate reader channels: immersion/transportation, prose aesthetics, social-simulation believability, and flow.
  - Treat reader-sim output as diagnostic evidence only; confusion or boredom becomes a bounded revision task, not an automatic rewrite.
  - For同类型仿写, require reader reward and independence evidence together.

### `jblemee/bmad-book-builder`

- URL: https://github.com/jblemee/bmad-book-builder
- Observed HEAD: `678c13f61a39f672308e920333709ade08829502`
- License: WTFPL
- Family: AI-assisted novel workflow module / chapter audit chain
- Posture: pattern-only
- Static evidence:
  - README describes 8 specialized agents, 17 workflows, Create/Edit/Validate modes, a pre-writing checklist, quantitative style metrics, automated post-chapter audits, living-bible update, character audits, theme tracking, rhythm analysis, and reality checks.
  - Public metadata confirms BMAD CLI / custom module install surface, so no CLI, npm installer, local module, workflow file, or agent runtime was installed or imported.
- Absorbed pattern:
  - `tri_modal_workflow_validation_gate`
- Local adaptation:
  - Declare workflow mode before any mutation: Create, Edit, or Validate.
  - Run pre-writing checklist before drafting.
  - After chapter acceptance, run review -> bible/state update -> character audit -> theme/rhythm audit -> next-chapter handoff.

## Deferred / duplicate sources

- `Saemer2023/webnovel-writer-opencode`: overlaps with existing `lujih/webnovel-writer-opencode`; useful as sibling evidence only. GPL/runtime installer surface keeps it pattern-only and not newly promoted.
- `SageAutoman/novel-control-station-openclaw-skill`: overlaps existing `jingtai123/Novel-Control-Station-Skill`; OpenClaw adaptation confirms one-chapter-at-a-time/writeback boundaries but does not require a new gate.
- `njacknot/novelist-skill`: useful skill-pack signal for chapter-control/professional mode, but install scripts and overlap with existing Chinese novelist skills keep it deferred for a later focused skill-pack pass.

## New workflow gates

### `book_mining_genesis_automation_gate`

Use when the system has source-book deconstruction or same-type writing inputs.

Rules:

- Mine source books into abstract pattern entries only.
- Run concept/genesis scoring before automation.
- Emit canon seed as the only handoff into chapter production.
- Keep source patterns, market notes, canon seed, and automation state in separate namespaces.

### `multi_book_autopilot_studio_gate`

Use when a writing session can run multiple books or unattended batches.

Rules:

- Bind every run to one book profile and context namespace.
- Require continue count, completion phrases, manual stop, and question-answer policy before autopilot.
- Insert periodic full-book logic checks before further unattended continuation.

### `longrun_commit_projection_health_gate`

Use when long-running continuation depends on derived state, summary, RAG, or dashboard projections.

Rules:

- Accepted chapter commit is the state mutation boundary.
- Derived projections must trace to the latest accepted commit.
- Stale projections or mixed source/new canon memory block next-chapter generation.

### `reader_reward_channel_gate`

Use when a continuation or same-type draft needs reader-facing quality feedback.

Rules:

- Score pivotal scenes on reader reward channels separately.
- Convert reader-sim issues into scoped revision tasks.
- Never let source resemblance count as reader pull in同类型仿写.

### `tri_modal_workflow_validation_gate`

Use when a workflow can create, edit, or validate bible / plan / chapter state.

Rules:

- Create, Edit, and Validate have different write permissions.
- Pre-writing checklist gates chapter drafting.
- Post-chapter audit chain gates canon/state write-back.

## Artifacts updated

- `backend/app/services/source_discovery_service.py`
- `backend/app/services/source_pattern_pack_prompt.py`
- `frontend/src/types/sourceDiscovery.ts`
- `frontend/src/components/book-remix/BookRemixSourceDiscoveryPanel.tsx`
- `backend/tests/services/test_source_discovery_service.py`
- `backend/tests/frontend/test_source_discovery_panel_copy.py`
- `backend/app/references/novel-source-pattern-pack-2026-06-10.json`

## Runtime exclusions

- No clone.
- No package manager.
- No scripts or installers.
- No Tauri, MCP, CLI, browser, provider, local model, or dashboard runtime.
- No source prose, pattern library body, or prompt file copied into runtime.

## Scene promise / serial simulation review addendum - 2026-06-10

This addendum records a public GitHub metadata + raw README/static file review pass for additional fiction-writing, webnovel, simulation, and manuscript-review sources. No external project was cloned, installed, built, launched, or executed. Scratch evidence was saved under `tmp/source-intake-*` only.

### Reviewed sources

- `Deland78/Claude-Writing-Skills`
  - URL: `https://github.com/Deland78/Claude-Writing-Skills`
  - observed HEAD: `e8f2a83ccf47e279e9c980b6765d92fda7c5d55e`
  - license: no license detected from public metadata
  - static evidence: README, `docs/mob_protocol.md`, `.claude/skills/scene-architect/SKILL.md`, tree metadata
  - absorbed pattern: `scene_promise_mob_review_gate`
  - reusable lesson: chapter promise -> scene cards -> draft -> cited mob review -> accepted canon commit. Specialist comments are queued one at a time and require citations/author resolution before they may mutate bible, relationships, timeline, or chapter plan.
  - runtime exclusion: Claude hooks, shell scripts, skill files, agents, and command protocols are not imported or executed.

- `netflypsb/webnovel-mcp`
  - URL: `https://github.com/netflypsb/webnovel-mcp`
  - observed HEAD: `7fd8ce5b9a061a8f49a435a5f36d10430af3b4be`
  - license: MIT
  - static evidence: README, `webnovel-author/SKILL.md`, `style-guide.md`, tree metadata
  - absorbed pattern: `webnovel_genre_tracker_gate`
  - reusable lesson: serial fiction needs explicit project structure plus genre-specific trackers for foreshadowing, timeline, LitRPG stats/inventory/quests, romance stages, cliffhanger rotation, stale characters, and chapter gaps.
  - runtime exclusion: uvx/pip install, MCP server launch, marketplace/license-key paths, and MCP tool calls are not executed.

- `hackertaco/novel-generator`
  - URL: `https://github.com/hackertaco/novel-generator`
  - observed HEAD: `eeac60fe9e41c144004a81f4764988f573188755`
  - license: no license detected from public metadata
  - static evidence: README, `docs/novel-engine-cli-library-parity.md`, tree metadata
  - absorbed pattern: `simulation_causal_ledger_verification_gate`
  - reusable lesson: long-form generation should advance world truth, character memory, belief state, utterance history, causal ledger, chapter summaries, and run metadata together, then verify long-horizon contradictions before accepting autopilot output.
  - runtime exclusion: npm/tsx scripts, provider calls, env files, Python legacy CLI, web routes, and API wrappers are not executed.

- `eristoddle/git-write`
  - URL: `https://github.com/eristoddle/git-write`
  - observed HEAD: `adf28c6f1bdd99fd1bdd95479b2f72413c9ebc4c`
  - license: MIT
  - static evidence: README, `docs/USER_GUIDE.md`, tree metadata
  - absorbed pattern: `writer_git_exploration_review_gate`
  - reusable lesson: risky rewrites should be treated as explorations/branches with word-level review, author-controlled accept/reject/modify decisions, beta-reader annotation provenance, and replayable merge history.
  - runtime exclusion: pip/poetry/npm install, Docker/compose, deploy scripts, API server, web app, and demo credentials are not used.

### Local projection

The pattern pack now exposes these additional prompt-safe hint fields:

- `scene_promise_mob_review_gate_hints`
- `webnovel_genre_tracker_gate_hints`
- `simulation_causal_ledger_verification_gate_hints`
- `writer_git_exploration_review_gate_hints`

These fields are static source-derived gates only. They do not authorize any upstream runtime, MCP server, package installation, provider call, browser/desktop control, or external account mutation.

## Narrative QA / summary / causality addendum - 2026-06-10

This addendum records a public GitHub HEAD + raw README/LICENSE static-review pass for narrative comprehension, long-form summary alignment, story QA, why-explanation, commonsense psychology, and query-focused long-summary sources. No external project was cloned, installed, built, launched, or executed. Scratch evidence was saved under `tmp/source-intake-narrative-qa-2026-06-10` only.

### Reviewed sources

- `google-deepmind/narrativeqa`
  - URL: `https://github.com/google-deepmind/narrativeqa`
  - observed HEAD: `904246f6d1fe99a99a08a03501fe3e619af2cee5`
  - license: Apache-2.0
  - static evidence: README, LICENSE
  - absorbed pattern: `narrative_qa_comprehension_gate`
  - reusable lesson:拆书 output should include evidence-backed questions and answers across plot, motive, relationships, setting rules, and unresolved hooks before it can feed续写.
  - runtime exclusion: story downloads, `download_stories.sh`, compare scripts, and corpus files are not executed or imported.

- `salesforce/booksum`
  - URL: `https://github.com/salesforce/booksum`
  - observed HEAD: `df178bf574cba106e6b5f71b5aafdcd488452798`
  - license: BSD-3-Clause
  - static evidence: README, LICENSE.txt
  - absorbed pattern: `chapter_summary_alignment_gate`
  - reusable lesson: paragraph-, chapter-, arc-, and book-level summaries need separate validation so long-form causal and temporal dependencies are not lost during context compression.
  - runtime exclusion: GCP downloads, summary collection scripts, datasets, and model baselines are not executed.

- `uci-soe/FairytaleQAData`
  - URL: `https://github.com/uci-soe/FairytaleQAData`
  - observed HEAD: `a24ddc17364666b7c13a425b9970c87368b03417`
  - license: Apache-2.0
  - static evidence: README, LICENSE
  - absorbed pattern: `story_question_answer_validation_gate`
  - reusable lesson: scene or section QA should ground answers to exact section/chapter evidence and narrative elements instead of accepting plausible genre guesses.
  - runtime exclusion: starter scripts, notebooks, HuggingFace loaders, and story/QA data are not executed or imported.

- `StonyBrookNLP/tellmewhy`
  - URL: `https://github.com/StonyBrookNLP/tellmewhy`
  - observed HEAD: `22ee9a0804f80b22d1afe45885243e059ca5206d`
  - license: no license detected from static README/LICENSE fetch
  - static evidence: README
  - absorbed pattern: `causal_why_explanation_gate`
  - reusable lesson: major character actions need why-answers grounded in prior events, belief state, pressure, and helpful sentence/chapter evidence; unsupported motives become reveal debt or revision tasks.
  - runtime exclusion: Google Drive downloads, HuggingFace dataset loading, evaluation scripts, and model tasks are not executed.

- `uwnlp/storycommonsense`
  - URL: `https://github.com/uwnlp/storycommonsense`
  - observed HEAD: `c8cb91b75b79925949fb2f0e564b58c198da11de`
  - license: no license detected from static README/LICENSE fetch
  - static evidence: README
  - absorbed pattern: `story_commonsense_consistency_gate`
  - reusable lesson:续写 should maintain a naive-psychology ledger for motivation, emotion, belief, desire, and likely reaction so character actions do not jump without on-page cause.
  - runtime exclusion: datasets, model code, project website workflows, and external loaders are not executed.

- `nyu-mll/SQuALITY`
  - URL: `https://github.com/nyu-mll/SQuALITY`
  - observed HEAD: `dc08d4f574639d773bc64ef3ab3527043108fb4e`
  - license: mixed data terms noted in README
  - static evidence: README
  - absorbed pattern: `query_focused_long_summary_gate`
  - reusable lesson: long-context summaries should be query-focused, with separate plot, character, relationship, and world-rule summaries plus disagreement notes before compression.
  - runtime exclusion: data files, training scripts, Project Gutenberg story consumption, and model baselines are not executed.

### Local projection

The pattern pack now exposes these additional prompt-safe hint fields:

- `narrative_qa_comprehension_gate_hints`
- `chapter_summary_alignment_gate_hints`
- `story_question_answer_validation_gate_hints`
- `causal_why_explanation_gate_hints`
- `story_commonsense_consistency_gate_hints`
- `query_focused_long_summary_gate_hints`

These fields are static source-derived gates only. They do not authorize any upstream dataset download, script execution, model training/evaluation, package installation, provider call, browser/desktop control, or external account mutation.
