# Novel Source Discovery - 2026-06-10 Project Workbench / Memory Diversity Gates

## Scope

This pass extends MuMuAINovel's source-discovered pattern pack for long-form
continuation and same-type original creation.

The sources were reviewed as public GitHub metadata, reachable HEADs, README
signals, and root-license signals only. No repository was cloned, installed,
executed, imported, served, or connected to a provider.

## Safety boundary

```text
source_intake_safety_review_packet_only_public_metadata_static_review_no_runtime
```

Runtime exclusions:

- no package-manager install
- no plugin, skill, MCP, Tauri, Rust, Node, Python package, Docker, app server,
  browser, desktop, provider, or sidecar launch
- no credential, cookie, token, Windows Credential Manager, sync directory,
  Scrivener project, private manuscript, or local account read
- no prompt-file wholesale copy
- no source prose or example output imported into MuMuAINovel generation context

## Source snapshots

### para-droid-ai/NovelizeAI

- Source: `https://github.com/para-droid-ai/NovelizeAI`
- Observed HEAD: `57485bc4ae927e13df027b346adab959e4b0920a`
- License: no root license observed in the static pass
- Family: AI novel web app / dashboard workflow
- Posture: `pattern-only`
- Reusable value:
  - project modifiers before planning
  - AI-driven initial plan
  - chapter plan -> prose -> review -> revision flow
  - live timings and system log
  - project-state JSON export

### Moosphan/novel-orchestrator

- Source: `https://github.com/Moosphan/novel-orchestrator`
- Observed HEAD: `6b5e2d55bd98d1f8cd82a312ee4e9d20d5cc5ac8`
- License: PolyForm Noncommercial 1.0.0
- Family: structured long-form fiction engine
- Posture: `pattern-only`
- Reusable value:
  - story assets as Markdown/frontmatter
  - canon layer separated from skill/rule layer
  - SQLite state, artifacts, checkpoints
  - plan/draft/audit/revise/canon-sync workflow

### kirinonakar/Novelgen

- Source: `https://github.com/kirinonakar/Novelgen`
- Observed HEAD: `706c6ad6f9f8b68e5436c88b10473f9fd899e93c`
- License: MIT
- Family: desktop AI story generator
- Posture: `pattern-only`
- Reusable value:
  - staged plot generation for long outlines
  - current/adjacent sliding-window context
  - CJK-aware token/plot usage checks
  - interrupted resume
  - exact chapter-range refinement

### abrahamp47/storyforge-wiki

- Source: `https://github.com/abrahamp47/storyforge-wiki`
- Observed HEAD: `e05622343ee2999cef2d547465a28a92f9c673f6`
- License: MIT
- Family: story bible / worldbuilding wiki
- Posture: `pattern-only`
- Reusable value:
  - raw manuscript ingestion cadence
  - wiki health/lint/query/graph workflow
  - timeline contradiction and character-state mismatch checks
  - relationship graph quality review
  - unresolved setup/payoff review

### third-order-labs/longform-plugin

- Source: `https://github.com/third-order-labs/longform-plugin`
- Observed HEAD: `1623bed717e07b2625d430feaf8c70dd21a05a2b`
- License: MIT
- Family: Claude/Cowork longform writing workflow plugin
- Posture: `pattern-only`
- Reusable value:
  - Plan -> Draft -> Log -> Verify -> Repeat
  - living documents that update after every chapter
  - scene log, continuity record, glossary, thread tracking
  - foreshadowing checklist
  - wrap/resume discipline

### hannasdev/mcp-writing

- Source: `https://github.com/hannasdev/mcp-writing`
- Observed HEAD: `8055d635819ae2ab76ab733166719763e1b756b2`
- License: AGPL-3.0
- Family: MCP service for long-form fiction editing
- Posture: `pattern-only / runtime-deferred`
- Reusable value:
  - metadata-first scene index
  - SQLite-canonical structural and relationship metadata
  - targeted scene reading
  - safe scene revision with confirmation
  - git/history-backed reversible edit evidence
  - review bundles

### xbraindance/Creative-writing-skill

- Source: `https://github.com/xbraindance/Creative-writing-skill`
- Observed HEAD: `093b9b75357fe48ad254e80ea8b4ccad9ecaa779`
- License: MIT
- Family: creative writing skill / writer wiki
- Posture: `pattern-only`
- Reusable value:
  - verbalized sampling for diverse alternatives
  - probability-scored premise/outline/draft variants
  - mode-collapse avoidance
  - persistent writer wiki
  - automatic character/setting filing

## Patterns promoted

- `user_modifier_project_blueprint_gate`
- `portable_canon_skill_runtime_gate`
- `staged_outline_chunk_window_gate`
- `wiki_canon_graph_lint_gate`
- `plan_draft_log_verify_loop_gate`
- `mcp_scene_index_revision_boundary`
- `verbalized_sampling_diversity_wiki_gate`

## MuMuAINovel fusion points

- `NovelSourceDiscoveryService`
  - discovery queries and direct repository seeds
  - static pattern overrides
  - pattern detection, priority, bible targets, whole-book audit targets
  - continuation and same-type inspired guidance

- `source_pattern_pack_prompt`
  - digest exposes the seven new hint groups

- `book_remix_context_service`
  - continuation and same-type inspired context blocks now render
    `Project workbench and memory diversity audit` when these gates are present

- tests
  - source mapping
  - pattern-pack target/hint/digest exposure
  - continuation and same-type inspired context rendering

## Decision

Keep all sources as `pattern-only`.

The value retained by MuMuAINovel is durable workflow structure: blueprint
evidence, canon-state layering, staged context windows, wiki/graph linting,
living-document updates, reversible scene revision boundaries, and diversity
sampling. Runtime code, examples, providers, plugins, MCP surfaces, and external
prompt files stay outside the project.
