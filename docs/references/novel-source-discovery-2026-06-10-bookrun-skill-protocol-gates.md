# Novel Source Discovery - 2026-06-10 BookRun / Skill Protocol Gates

## Scope

This pass extends MuMuAINovel's public-source pattern pack for Chinese
long-form continuation and same-type original creation.

The sources were reviewed as public metadata and static README/root-file
signals only. No external project was cloned, installed, executed, imported,
served, or used as a provider/runtime dependency.

## Safety boundary

```text
source_intake_safety_review_packet_only_public_metadata_static_review_no_runtime
```

Runtime exclusions for every source in this pass:

- no package-manager install
- no shell script, PowerShell script, postinstall, Docker, sidecar, MCP, server,
  worker, browser extension, or native binary execution
- no model/provider call
- no credentials, cookies, tokens, private account, or repository secrets
- no runtime code import into MuMuAINovel
- no source prose copying into continuation or same-type creation prompts

## Source snapshots

### XZZKANY/StoryForge

- Source: `https://github.com/XZZKANY/StoryForge`
- Observed HEAD: `1a748b332d9b93497881c14c721746efc17852f7`
- License: no GitHub API license / no root license observed in the static pass
- Family: Chinese long-form novel production pipeline
- Posture: `pattern-only`
- Reusable value:
  - BookRun run identity
  - Blueprint and Story Memory separation
  - Judge/Repair acceptance loop
  - checkpoint resume
  - export audit artifacts
  - real LLM smoke gates before long generation

### spiritLHLS/novelbuilder

- Source: `https://github.com/spiritLHLS/novelbuilder`
- Observed HEAD: `5280b74c88226a5d7b4ab73a3f581e7a6b06048f`
- License: GPL-3.0
- Family: AI long-form fiction workbench
- Posture: `pattern-only`
- Reusable value:
  - Vue UI / Go API / Python sidecar boundary
  - task queue and provider-profile routing vocabulary
  - optional graph/vector memory profile separation
  - SQLite-only vs graph/vector/Docker deployment profiles

### qiuxinyuan321/novel-writer-master

- Source: `https://github.com/qiuxinyuan321/novel-writer-master`
- Observed HEAD: `ee3bcf373d7c233c719e4c217d32149b6ff64945`
- License: MIT in project metadata / README badge; GitHub API license not
  available during this pass
- Family: AI novel writing system
- Posture: `pattern-only`
- Reusable value:
  - anti-AI-rate review vocabulary
  - layered outline and checkpoint constraints
  - narrative milestone coverage
  - Story Bible as the truth source

### Byk3y/no-slop

- Source: `https://github.com/Byk3y/no-slop`
- Observed HEAD: `98cd8fb016bf5c3467e646e23d7ce09234ec0b2b`
- License: MIT
- Family: prose linter / writing rulepack
- Posture: `pattern-only`
- Reusable value:
  - banned vocabulary ledger
  - simple-copula and vague-attribution checks
  - marketing-language cadence detection
  - AI-prose structural-tell triage

### nntrivi2001/wordsmith

- Source: `https://github.com/nntrivi2001/wordsmith`
- Observed HEAD: `57ad23b258d9d7fe35f686411d1574506413530a`
- License: GPL-3.0
- Family: multi-skill writing assistant
- Posture: `pattern-only`
- Reusable value:
  - language-specific style profile
  - Vietnamese prose and glossary patterns
  - dashboard/resume/learn workflow vocabulary
  - local RAG boundary as evidence, not runtime import

### zy-zmc/tianming-skill

- Source: `https://github.com/zy-zmc/tianming-skill`
- Observed HEAD: `b5ef6e30817e086022ecbd09f9c2d2e781dd8b43`
- License: CC BY-NC-SA 4.0
- Family: Codex/skill protocol pack
- Posture: `pattern-only`
- Reusable value:
  - progressive disclosure protocol loading
  - intent-based command routing
  - protocol files separate from light entrypoints
  - codex/protocol/knowledge-base layer boundaries

## Patterns promoted

- `bookrun_audit_trail_gate`
- `provider_budget_smoke_gate`
- `sidecar_memory_profile_boundary`
- `outline_checkpoint_milestone_gate`
- `language_localization_style_profile_gate`
- `progressive_disclosure_skill_protocol_gate`
- `anti_slop_rulepack_triage_gate`

## MuMuAINovel fusion points

- `NovelSourceDiscoveryService`
  - default GitHub discovery queries
  - direct repository URL seed list
  - static repository pattern overrides
  - pattern priorities
  - bible enrichment targets
  - whole-book analysis targets
  - continuation and same-type inspired prompt/copy-risk guidance

- `source_pattern_pack_prompt`
  - digest output now exposes the seven new hint groups

- `book_remix_context_service`
  - continuation and same-type inspired context blocks render a compact
    `BookRun and skill protocol audit` section when the new patterns are present

- tests
  - source mapping and pattern-pack tests cover the six sources and seven gates
  - context-rendering tests cover the continuation and same-type inspired blocks

## Decision

Keep all six sources as `pattern-only`.

The durable value is workflow vocabulary and acceptance-gate design. Runtime
systems, licenses, providers, sidecars, graph/vector stores, scripts, Docker
profiles, and prose/code bodies stay outside MuMuAINovel.
