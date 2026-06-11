# Novel Source Discovery - 2026-06-11 Guardrail Manual Review Gate

## Scope

Static source-intake pass for long-form AI novel systems related to???????????????????????

No repository was cloned, installed, or executed. Evidence was limited to public GitHub metadata/search and `git ls-remote HEAD`.

## Sources

- `ExplosiveCoderflome/AI-Novel-Writing-Assistant`
  - URL: https://github.com/ExplosiveCoderflome/AI-Novel-Writing-Assistant
  - Observed HEAD: `e88cdcd22ff02d056c9b7c7214d7e67b54a28d9e`
  - Public metadata: AI-native long-form novel system with agents, worldbuilding, RAG, structured planning, and full production workflow.
  - Posture: `pattern-only`; license is non-standard/NOASSERTION in GitHub metadata.
- `DuckTraDo/Novel`
  - URL: https://github.com/DuckTraDo/Novel
  - Observed HEAD: `cb80630cb340303d70bba42274dd7afbf892d4f8`
  - Public metadata: local-first AI novel pipeline with structured story memory, scene-level context, LoRA style adapters, and continuity checks.
  - Posture: `pattern-only`; MIT.
- `angel1411337-del/WriterOS`
  - URL: https://github.com/angel1411337-del/WriterOS
  - Observed HEAD: `22808f4b6e54d370ec8c90ffe3e50885d9f32ada`
  - Public metadata: complex-fiction writing assistant with specialized agents for worldbuilding, continuity, character arcs, plot holes, PostgreSQL/vector search, and Obsidian-compatible local-first storage.
  - Posture: `pattern-only`; license metadata `NOASSERTION`.
- `f5alcon/The-Novelists-Atelier`
  - URL: https://github.com/f5alcon/The-Novelists-Atelier
  - Observed HEAD: `e00560021c9773edad7cd745bbf5384bbdb45eab`
  - Public metadata: privacy-first browser-local writing assistant with multiple providers and series/book/chapter-level context management.
  - Posture: `pattern-only`; Apache-2.0.

## Reusable pattern

Chapter acceptance must be a separate gate from chapter text persistence.

A generated chapter may be saved for inspection, but if rewrite attempts still fail copy-risk, canon-repetition, or other high-severity guardrails, it should not be promoted as completed canon. It should be marked as review-required, and downstream analysis, memory extraction, foreshadow write-back, and continuation state write-back should wait for human review.

## Project adaptation

- `apply_chapter_guardrail_check` now emits `acceptance_status` and `manual_review_reasons`.
- Chapter generation saves unresolved guardrail failures with status `review_required` instead of `completed`.
- Batch generation raises after saving a review-required chapter so the ordered continuation batch stops before later chapters consume unsafe state.
- Generation history records a compact guardrail status note.
- The chapter list UI recognizes `review_required` and blocks later chapter generation until the user reviews the prior chapter.

## Runtime boundary

No external project code was imported. The local change only adds deterministic acceptance-state handling around existing guardrail results.

## 2026-06-11 follow-up: human review state resume

Additional static metadata pass, still no clone/install/runtime/provider calls:

- `iLearn-Lab/NovelClaw`: dynamic-memory-first long-form story generation, chapter planning, and coherent narrative writing; MIT; pattern-only.
- `zy-zmc/tianming-novel-ai-writer`: fact snapshots, change declarations, generation gates, and per-chapter state write-back; license not declared in GitHub metadata; pattern-only.

Absorbed pattern: a `review_required` chapter needs an explicit human approval event before it can become durable continuation state. The approval event must resume the same downstream chain that a safe generation would have used: foreshadow planting, remix continuation state write-back, and chapter analysis scheduling.

Project adaptation:

- Generation history now stores a structured guardrail review packet in addition to the compact text note.
- Backend exposes `/chapters/{chapter_id}/guardrail-review` to inspect latest structured reasons.
- Backend exposes `/chapters/{chapter_id}/guardrail-review/approve` to mark the chapter completed and resume downstream write-back/analysis.
- Frontend chapter actions show a `review_required` review action that displays guardrail reasons and approves the chapter after human inspection.

## 2026-06-11 follow-up: explicit review note and analysis task reuse

Additional static metadata pass, still no clone/install/runtime/provider calls:

- `BlinkDL/AI-Writer`
  - URL: https://github.com/BlinkDL/AI-Writer
  - Observed HEAD: `d7e23c7ffb42fdde3fd14c88abb4d865544d88a4`
  - License: Apache-2.0
  - Public signal: Chinese AI novel generation with runnable scripts and local model/server surfaces.
  - Posture: `pattern-only`; runtime scripts and model/server paths were not executed.
- `Deng-m1/MaliangAINovalWriter`
  - URL: https://github.com/Deng-m1/MaliangAINovalWriter
  - Observed HEAD: `f500d0114393805c345d36c20e4331d0bb4290cc`
  - License: Apache-2.0
  - Public signal: online novel authoring platform with txt import, outline/chat UI, prompt management, data analysis, and editor tools.
  - Posture: `pattern-only`; platform runtime and deployment assets were not executed.
- `yangkevin2/emnlp22-re3-story-generation`
  - URL: https://github.com/yangkevin2/emnlp22-re3-story-generation
  - Observed HEAD: `3a97ebde04e3333962c2825146897efe1dc87dd8`
  - License: MIT
  - Public signal: Re3 long-story generation research code with plan/draft/rewrite/edit and recursive reprompting/revision ideas.
  - Posture: `pattern-only`; requirements, setup, notebooks, and scripts were not executed.
- `heider-x/vela`
  - URL: https://github.com/heider-x/vela
  - Observed HEAD: `854a0c0acc57b8f99904b96b4470df355e0918c9`
  - License: GPL-3.0
  - Public signal: privacy-first AI novel IDE with local LLM/RAG/BYOK and writing workspace surfaces.
  - Posture: `pattern-only`; GPL/runtime code was not imported.
- `MissingDanial/StyleMuse`
  - URL: https://github.com/MissingDanial/StyleMuse
  - Observed HEAD: `1eb1fbd8be3adda5143254e3438dc0755eac0ffa`
  - License: no GitHub license detected
  - Public signal: style-imitation RAG workspace with epub/txt upload, style analysis, vector index, and OpenAI-compatible providers.
  - Posture: `pattern-only`; corpus processing, Docker, scripts, and provider calls were not executed.

Absorbed pattern: review approval is not just a button state. A durable
chapter-promotion event should have an explicit reviewer note and should not
spawn duplicate downstream analysis tasks when an unfinished task already
exists. This matches the broader Plan/Draft/Rewrite/Edit lesson from Re3 and
the review-before-promotion pattern from style-RAG/authoring workspaces.

Project adaptation:

- `/chapters/{chapter_id}/guardrail-review/approve` now requires a non-empty
  `review_note`, so the promotion event records what the human checked.
- Approval now reuses the newest `pending` or `running` analysis task for the
  chapter instead of creating a second task.
- The approval response exposes whether the task was reused, plus current task
  status and progress for the UI.
- The frontend review modal now asks the reviewer to edit/confirm a复核说明
  before promoting the chapter.

## 2026-06-11 follow-up: reviewed text fingerprint

Additional static metadata pass, still no clone/install/runtime/provider calls:

- `zlx362211854/novelforge-agent`
  - URL: https://github.com/zlx362211854/novelforge-agent
  - Observed HEAD: `d80af87ac255948cda5b23091c796a392d683691`
  - License: MIT
  - Public signal: local-first long-form novel workflow engine for MCP/CLI
    hosts, with chapter review, revision counts, packed context, schema
    validation, and compact audit logs using length/sha256-style summaries.
  - Posture: `pattern-only`; MCP server, package scripts, host config edits,
    and provider/model calls were not executed.
- `Narcooo/inkos`
  - URL: https://github.com/Narcooo/inkos
  - Observed HEAD: `39021ba0e9b13d5bba571f24dff6ee542209a1a2`
  - License: AGPL-3.0
  - Public signal: story creation agent for novels/scripts/IP content with
    heavy-action confirmation, audits, revision, state snapshots, file locking,
    and schema deltas.
  - Posture: `pattern-only`; AGPL/runtime code was not imported or executed.
- `v-saprykin/storygraph`
  - URL: https://github.com/v-saprykin/storygraph
  - Observed HEAD: `1b8f5aaae5f1d047f25edd5a08d73adaddcee7e4`
  - License: MIT
  - Public signal: long-form fiction narrative graph with manuscript,
    chapters, scenes, narrative events, timeline versions, causal links, and
    human review.
  - Posture: `pattern-only`; service/runtime/database components were not
    executed.

Absorbed pattern: a human approval event should bind to the exact text that was
approved, not only to a chapter id and free-form note. Long-form state engines
use compact immutable facts such as length and content hash to make promotion,
revision, and graph-state write-back replayable.

Project adaptation:

- Manual guardrail approval now records `content_sha256`, `content_length`, and
  `word_count` inside `guardrail_check.manual_review`.
- The reviewed text fingerprint is carried into the BookRemix chapter change
  package, next to reviewer id, timestamp, and note.
- Tests verify that the fingerprint matches the exact chapter content promoted
  from `review_required` into durable continuation state.

## 2026-06-11 follow-up: stale approval guard

Additional static metadata pass, still no clone/install/runtime/provider calls:

- `RhythmicWave/NovelForge`
  - URL: https://github.com/RhythmicWave/NovelForge
  - Observed HEAD: `71db1420d919d676521a15f6999090b37db86fb0`
  - Default branch: `main`
  - Public README signal: chapter workflow has dense chapter/outline/review/context vocabulary, including review-heavy book-remix style operations.
  - Posture: `pattern-only`; no package manager, script, provider, or runtime was executed.
- `leenbj/novel-creator-skill`
  - URL: https://github.com/leenbj/novel-creator-skill
  - Observed HEAD: `a327428ea26962163f823ad74001243f91bc7738`
  - Default branch: `main`
  - Public README signal: Claude Code novel-creation skill vocabulary covers continuation, inspired writing, style, chapter, outline, review, memory, and character signals.
  - Posture: `pattern-only`; skill files were not installed or executed.
- `uu201/character-arc`
  - URL: https://github.com/uu201/character-arc
  - Observed HEAD: `ec3f5688e95182792bd4530181970a52f46b4bbb`
  - Default branch: `main`
  - Public README signal: character-arc and story-state vocabulary links style imitation, chapter state, and continuity review.
  - Posture: `pattern-only`; no scripts or generation runtime were executed.
- `worldwonderer/oh-story-claudecode`
  - URL: https://github.com/worldwonderer/oh-story-claudecode
  - Observed HEAD: `e89f68222cbb3211b62981dc7052f2221bd3ff18`
  - Default branch: `main`
  - Public README signal: role/context/story-planning vocabulary emphasizes structured context before continuation.
  - Posture: `pattern-only`; no Claude Code command pack was installed.
- `guchendesigndog/GC-Writer-Assistant`
  - URL: https://github.com/guchendesigndog/GC-Writer-Assistant
  - Observed HEAD: `b38f83c55dddbbd124a04bf7481d8fc97431c83c`
  - Default branch: `main`
  - Public README signal: lightweight writer-assistant vocabulary around continuation, chapter, outline, and review.
  - Posture: `pattern-only`; no code was downloaded or run.

Absorbed pattern: long-form continuation approval must be tied to the exact
chapter body visible to the reviewer. When chapter content can be edited while a
review dialog is open, a free-form note plus chapter id is not enough; the
approve request needs the dialog-time content fingerprint, and the backend must
reject stale approvals before writing canon state, foreshadow state, remix
continuation state, or analysis tasks.

Project adaptation:

- `GET /chapters/{chapter_id}/guardrail-review` now returns
  `current_content_sha256`, `current_content_length`, and `current_word_count`.
- The review modal displays the current text fingerprint and submits
  `review_content_sha256` with the approval request.
- `POST /chapters/{chapter_id}/guardrail-review/approve` rejects a mismatched
  submitted hash with HTTP 409 before changing chapter status, writing remix
  state, planting foreshadows, or scheduling analysis.
- Tests cover both matching-hash approval and stale-hash rejection.

## 2026-06-11 follow-up: source excerpt provenance

Additional static metadata pass, still no clone/install/runtime/provider calls:

- `guerra2fernando/libriscribe`
  - URL: https://github.com/guerra2fernando/libriscribe
  - Observed HEAD: `1d781d373432abe2df1e477eeab083edb86ebe84`
  - Default branch: `main`
  - Public README signal: book-generation workflow vocabulary around outline,
    chapter, style, review, character, and audit.
  - Posture: `pattern-only`; no package manager, script, or generation runtime
    was executed.
- `DoktorDaveJoos/manuscript`
  - URL: https://github.com/DoktorDaveJoos/manuscript
  - Observed HEAD: `c88bd26053454478cf099497936045596854783c`
  - Default branch: `main`
  - Public README signal: manuscript workflow vocabulary around chapters,
    revision, accept/dismiss, review, context, and consistency.
  - Posture: `pattern-only`; no runtime or provider was executed.
- `kshanxs/book-writer-skill`
  - URL: https://github.com/kshanxs/book-writer-skill
  - Observed HEAD: `2a247a6666e77c439c9351a842123c07b5982205`
  - Default branch: `main`
  - Public README signal: skill workflow vocabulary around chapter, outline,
    style, review, memory, character, revision, and consistency.
  - Posture: `pattern-only`; skill files were not installed.
- `pulpgen-dev/pulpgen`
  - URL: https://github.com/pulpgen-dev/pulpgen
  - Observed HEAD: `91c77b4877cb90a0fffba1b4593bb176909c88ff`
  - Default branch: `main`
  - Public README signal: long-form generation vocabulary around outline,
    chapter, context, revision, review, and audit.
  - Posture: `pattern-only`; no runtime was executed.
- `shenminglinyi/PlotPilot`
  - URL: https://github.com/shenminglinyi/PlotPilot
  - Observed HEAD: `0011e503ce577489eac6e4ee8f4eeedc7f3bc2b5`
  - Default branch: `master`
  - Public README signal: Chinese writing workflow vocabulary around chapter,
    context, plot, causality, and foreshadowing.
  - Posture: `pattern-only`; no scripts or providers were executed.

Absorbed pattern: review packets should not only say that a generated chapter
looked too similar to some source. They should preserve compact provenance for
the source excerpts used by the copy-similarity guardrail. Hash, length, and a
bounded preview are enough for a reviewer to replay which reference window
triggered review without storing or reusing the full upstream prose.

Project adaptation:

- `apply_chapter_guardrail_check` now records bounded
  `source_excerpt_fingerprints` for inspired-source excerpts.
- The structured `GUARDRAIL_REVIEW_JSON` history packet carries those
  fingerprints into the review API.
- Manual approval keeps the fingerprints beside the reviewed content hash in
  the BookRemix chapter change package.
- Tests cover fingerprint creation, history serialization, and continuation
  state write-back.


## 2026-06-11 follow-up: reviewer-visible source fingerprints

Additional static metadata pass, still no clone/install/runtime/provider calls:

- `rhavekost/author-toolkit`
  - URL: https://github.com/rhavekost/author-toolkit
  - Observed HEAD: `5faebfac5fddb59149798b8108a2c379d9b2465c`
  - Default branch: `main`
  - Public README signal: Claude writing skill vocabulary around chapter,
    continuity, voice, and character state.
  - Posture: `pattern-only`; no license detected in GitHub metadata, and no
    skill/plugin files were installed.
- `mike-cramblett/novel-novel-generator`
  - URL: https://github.com/mike-cramblett/novel-novel-generator
  - Observed HEAD: `a658c9bbd24f2ab00799c295768608f91388b198`
  - Default branch: `main`
  - License: MIT
  - Public README signal: one-shot AI novel workflow with continuity,
    structural integrity, outline, chapter, audit, voice, and fingerprint
    vocabulary.
  - Posture: `pattern-only`; React/Gemini runtime and provider surfaces were
    not executed.
- `geobond13/fiction-forge`
  - URL: https://github.com/geobond13/fiction-forge
  - Observed HEAD: `181a28cfe41c018eef278a00d28be1887ce7ba01`
  - Default branch: `main`
  - License: MIT
  - Public README signal: prose-pattern scanner and MCP context vocabulary for
    AI-assisted novel editing, including fingerprint, chapter, outline,
    continuity, style, voice, cluster, pattern, and character markers.
  - Posture: `pattern-only`; MCP/server surfaces and scanners were not
    installed or executed.

Absorbed pattern: compact source-excerpt provenance only helps the reviewer if
it is visible at approval time. The review dialog should show the same bounded
hash/length/preview packet that the backend will later persist beside the
approved chapter-change package.

Project adaptation:

- The chapter guardrail review type now exposes `source_excerpt_fingerprints`.
- The review modal renders each source excerpt fingerprint with a short hash,
  character length, and bounded preview before the reviewer approves.
- The approval request still binds to the current chapter content hash, so the
  visible source provenance and approved chapter text remain in one review
  event.


## 2026-06-11 follow-up: violation-level source trace

Additional static metadata pass, still no clone/install/runtime/provider calls:

- `IsaiahN/Serendipity-Engine`
  - URL: https://github.com/IsaiahN/Serendipity-Engine
  - Observed HEAD: `0ee0b5ba9df2de82f554e32f926be654c4582aad`
  - Default branch: `pwa-app`
  - License: GitHub metadata `NOASSERTION`
  - Public README signal: structured story-architecture workshop for novels,
    screenplays, film, and narrative forms; marker scan found audit, phase,
    continuity, chapter, fingerprint, decision, and override vocabulary.
  - Posture: `pattern-only`; no app/runtime, scripts, provider, or workshop
    pipeline was executed.

Absorbed pattern: a review queue is easier to audit when each failed check
points to the exact source item it depends on. Whole-packet source fingerprints
are useful, but violation rows should also carry source index, source hash,
source length, and the detected copy signal so a reviewer can inspect one
failure without manually matching it back to the full provenance list.

Project adaptation:

- `inspired_source_copy` violations now carry `source_excerpt_index`,
  `source_excerpt_sha256`, `source_excerpt_length`, and `copy_signal`.
- Structured guardrail history serializes those violation-level provenance
  fields into `final_violations` / `initial_violations`.
- The review modal shows the short source hash and copy signal inside each
  violation detail, beside the bounded source preview list.

## 2026-06-11 follow-up: source-entity leakage guard

Additional static metadata pass, still no clone/install/runtime/provider calls:

- `YfengJ/novel-studio-ai`
  - URL: https://github.com/YfengJ/novel-studio-ai
  - Observed HEAD: `90fbf0681e76afe791d11f21edd1fb1516ee5e1d`
  - Default branch: `main`
  - License: GitHub metadata `NOASSERTION`
  - Public metadata signal: local-first long-form fiction workbench with story
    bibles, outlines, character state, graph facts, retrieval memory, and
    continuity checks. README marker scan found story-bible, continuity,
    character-state, memory, review, and export vocabulary.
  - Posture: `pattern-only`; no app/runtime, provider, package manager, or
    repository clone was executed.
- `hayrgpt-rgb/NovelForge-AI`
  - URL: https://github.com/hayrgpt-rgb/NovelForge-AI
  - Observed HEAD: `48c9bca5e62eefa2dd8365f4a2bf4564b94b546a`
  - Default branch: `main`
  - License: GitHub metadata `NOASSERTION`
  - Public metadata signal: long-form platform language around story bible,
    scene cards, drafts, review, revision, memory, continuity tracking,
    version-safe generation, and traceability.
  - Posture: `pattern-only`; no app/runtime, provider, package manager, or
    repository clone was executed.
- `Riccjamez214/wordplay`
  - URL: https://github.com/Riccjamez214/wordplay
  - Observed HEAD: `d82ac671efca4a6b2df4f2279b2d66337fe2bc28`
  - Default branch: `main`
  - License: Apache-2.0
  - Public metadata signal: AI writing assistant with project management,
    chapter editing, and story consistency vocabulary.
  - Posture: `pattern-only`; no app/runtime, provider, package manager, or
    repository clone was executed.
- `author-repo-testing/novel-writing-workflow`
  - URL: https://github.com/author-repo-testing/novel-writing-workflow
  - Observed HEAD: `16e0d98d1b19442c6b15880ea31a5464a924996e`
  - Default branch: `main`
  - License: MIT
  - Public metadata signal: GitHub-managed novel workflow vocabulary around
    story bible, revision, review, characters, memory, and continuity.
  - Posture: `pattern-only`; no app/runtime, provider, package manager, or
    repository clone was executed.

Absorbed pattern:同类仿写的相似度检查不能只看长句复刻。长篇写作工作台通常把 story bible、character state、graph facts、memory、scene cards、review 和 traceability 拆成可检查状态；迁移到仿写安全上，源书专有实体也应是可检查状态。即使草稿没有连续照搬源文，只要复用了源书独有组织、物件、能力、地名等实体，也应进入人工复核/改写链路。

Project adaptation:

- `ChapterGuardrails` now derives source-specific Chinese entity candidates
  from inspired-source excerpts when no phrase-copy signal fires.
- Same-type drafts that reuse those source entities emit
  `inspired_source_entity_leak` with the same source index/hash/length and
  `copy_signal` provenance used by `inspired_source_copy`.
- The new gate catches source-specific artifact/faction leakage such as a
  reused token or organization name without needing the full source sentence to
  survive.
- Tests cover the red/green path where a draft reuses source entities but does
  not copy enough prose to trigger the existing phrase-copy detector.

### 2026-06-11 patch: entity leak repair prompt carry-through

Follow-up implementation note:

- `inspired_source_entity_leak` now feeds detected source entities back into the
  guardrail rewrite prompt's source-element denylist.
- The denylist is built from explicit forbidden names plus entity candidates
  recovered from the triggering violation context and `source_entity_leak:*`
  signal.
- This closes the loop between detection and repair: the rewrite model receives
  concrete leaked entities such as source-specific artifacts and factions, not
  only a generic violation label.

### 2026-06-11 patch: multi-entity leak signal

Follow-up implementation note:

- `inspired_source_entity_leak` now keeps every matched source-specific entity
  in the violation `copy_signal` instead of only the first match.
- Multi-entity signals use `source_entity_leak:<entity>|<entity>` and are split
  back into separate denylist rows when building the guardrail rewrite prompt.
- This makes review and repair more faithful to the actual leak surface when a
  draft reuses both a source artifact and a source faction in the same passage.

### 2026-06-11 patch: modal-phrase false-positive guard

Follow-up implementation note:

- Source-entity detection now filters common modal phrases ending in `会`, such
  as `一定会` and `不会`, so ordinary prose modality is not treated as a source
  faction or organization leak.
- The guard still catches organization-style names such as `青岚会` because they
  are not modal phrases and remain source-specific entity candidates.
- This reduces false positives while keeping same-type creation checks focused
  on copied source artifacts, factions, powers, locations, and named settings.

### 2026-06-11 patch: rewrite denylist atomization

Follow-up implementation note:

- The guardrail rewrite prompt now prefers atomic entities from
  `source_entity_leak:*` when building the source-element denylist.
- Context-derived candidates are used only as a fallback when no structured
  leak signal exists.
- This prevents long source-context fragments such as `林寒把玄霜令` from
  polluting the repair prompt while still listing the actual leaked entities
  like `玄霜令` and `青岚会`.

### 2026-06-11 patch: rewrite denylist dedupe regression

Follow-up test note:

- Added regression coverage that explicit forbidden source names and detected
  `source_entity_leak:*` entities are merged without duplicate prompt rows.
- This keeps repair prompts compact when a source faction or artifact is both
  user-specified and detected from the generated draft.

### 2026-06-12 intake: review-readable copy signal display

Static intake boundary:

- No external repository was cloned, installed, executed, or used as runtime
  code.
- Public GitHub metadata, `git ls-remote`, and raw README marker scans were used
  only as pattern evidence.
- Posture for all sources below remains `pattern-only`.

Observed sources:

- `iLearn-Lab/NovelClaw`
  - URL: https://github.com/iLearn-Lab/NovelClaw
  - Observed HEAD: `226d50d3ec284c9cc037c47eb14af39505f9ed74`
  - Default branch: `main`
  - License: MIT
  - Public signal: dynamic-memory-first long-form story generation, chapter
    planning, review, and inspectable narrative state.
- `mrigankad/Novel-OS`
  - URL: https://github.com/mrigankad/Novel-OS
  - Observed HEAD: `5f950095aaf397e82297e62423635b2f41edcc57`
  - Default branch: `dev`
  - License: MIT
  - Public signal: persistent story state, deterministic continuity engine, and
    editorial pipeline.
- `ARMANDSnow/make-ur-Agent-writer`
  - URL: https://github.com/ARMANDSnow/make-ur-Agent-writer
  - Observed HEAD: `e3c18f83f17f204f382781c746e57cf0a05a41be`
  - Default branch: `main`
  - License: NOASSERTION
  - Public signal: Chinese long-form continuation pipeline with mock-first
    multi-agent review/rewrite vocabulary.
- `forsonny/book-os`
  - URL: https://github.com/forsonny/book-os
  - Observed HEAD: `bf155998505bd5951e73564c3ff1b5fbe7190e83`
  - Default branch: `main`
  - License: MIT
  - Public signal: tool-agnostic fiction context layers, genre guides, story
    outlines, scene tasks, and inspectable style context.
- `adaumann/speckit-preset-fiction-book-writing`
  - URL: https://github.com/adaumann/speckit-preset-fiction-book-writing
  - Observed HEAD: `c31b629ef8c733eb4e3af8643a5761ee9328fec0`
  - Default branch: `main`
  - License: unknown
  - Public signal: spec-driven fiction book task templates and scene-writing
    workflow vocabulary.

Absorbed pattern:

- Long-form writing systems make review state inspectable. Copy-risk guardrails
  should expose not only source hash and length but also a reviewer-readable
  reason.
- Same-type imitation review should translate internal detector signals into
  plain labels, especially source-entity leakage. A reviewer should see
  `source entity leak: 玄霜令, 青岚会`, not raw internal text like
  `source_entity_leak:玄霜令|青岚会`.

Project adaptation:

- The chapter guardrail review panel now formats `copy_signal` values before
  display.
- `source_entity_leak:*` is split into individual entity names for human
  review.
- Copy detectors such as `distinctive_substring`,
  `fingerprint_overlap:<ratio>`, and `simhash_near_duplicate:<ratio>` are shown
  as readable labels while keeping the source excerpt hash and length visible.
- A frontend regression test prevents returning to raw `copy_signal` display.

### 2026-06-12 patch: Latin-script source entity leakage

Static intake boundary:

- No external repository was cloned, installed, executed, or used as runtime
  code.
- Public GitHub metadata, `git ls-remote`, and raw README marker scans were used
  only as pattern evidence.
- Posture for all sources below remains `pattern-only`.

Observed sources:

- `loreum-app/loreum`
  - URL: https://github.com/loreum-app/loreum
  - Observed HEAD: `c38ade12a664790d10ff3ae847ce2529845f299c`
  - Default branch: `main`
  - License: AGPL-3.0
  - Public signal: worldbuilding platform with characters, knowledge graph,
    timeline, lore wiki, storyboard, style guide, and review vocabulary.
- `Lanerra/saga`
  - URL: https://github.com/Lanerra/saga
  - Observed HEAD: `865a3912f17b09af9927c0358f9f026020f51673`
  - Default branch: `master`
  - License: Apache-2.0
  - Public signal: agentic story writing with embeddings, knowledge graphs,
    canon, relationships, and fact extraction vocabulary.
- `doctoroyy/novel-copilot`
  - URL: https://github.com/doctoroyy/novel-copilot
  - Observed HEAD: `ea671b090e191e0586b0ff96d75f6928d0fe97b4`
  - Default branch: `main`
  - License: unknown
  - Public signal: novel assistant with three-layer memory, plot consistency,
    relationship graph, timeline, and state vocabulary.
- `XuanRanL/webnovel-writer`
  - URL: https://github.com/XuanRanL/webnovel-writer
  - Observed HEAD: `269583f662bcfe44958924496653e5f6e0e2d50c`
  - Default branch: `master`
  - License: GPL-3.0
  - Public signal: Claude Code long web-novel workflow focused on forgotten
    state and hallucination control.
- `hayrgpt-rgb/NovelForge-AI`
  - URL: https://github.com/hayrgpt-rgb/NovelForge-AI
  - Observed HEAD: `48c9bca5e62eefa2dd8365f4a2bf4564b94b546a`
  - Default branch: `main`
  - License: unknown
  - Public signal: long-form novel platform with story bible, scene cards,
    drafts, review, revision, memory, continuity, traceable generation, and
    source/fact vocabulary.

Absorbed pattern:

- Entity/canon systems must treat source-specific names as state, not just as
  prose. For same-type imitation, this applies to Latin-script artifacts,
  stations, project codenames, organizations, and mixed alphanumeric names as
  much as to Chinese sect/place/item names.
- Copy-risk review should catch `AetherLedgerKey`, `BetaClerk77`, and
  `Moonfall Station` style source entities even when no long source sentence is
  copied.

Project adaptation:

- Source entity extraction now keeps raw source text for entity detection, while
  still using normalized text for phrase-copy checks.
- Same-type guardrails now detect reused camel-case, mixed alphanumeric, and
  multi-word title-case Latin source entities.
- Reused Latin-script source entities emit the same
  `inspired_source_entity_leak` violation and `source_entity_leak:*` signal as
  Chinese source entities, so the existing manual-review and rewrite-denylist
  chain can handle them without a separate path.
