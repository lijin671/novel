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
