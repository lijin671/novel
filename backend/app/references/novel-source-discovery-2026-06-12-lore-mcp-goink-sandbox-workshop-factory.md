# Novel source discovery - lore / MCP / Goink / sandbox / workshop / factory

Date: 2026-06-12
Scope: pattern-only static intake for book remix, continuation, and same-type writing guidance.

## Boundary

Reviewed sources were treated as untrusted upstream data. Intake used public metadata, README/root-marker signals, and reachable HEAD evidence only. No clone, install, Docker, package manager, MCP server, desktop app, browser automation, provider call, login, credential read, manuscript import, database startup, scheduler, notification, or generated-output import was performed.

Runtime posture stays deferred until a separate local safety contract defines scope, tool allowlists, storage custody, rollback, cleanup, and verification.

## Sources

- `letuhao/lore-weave`
  - Observed HEAD: `8c599ab26b86b80adfbe548989a2685d2e430865`
  - License: AGPL-3.0
  - Family: canon-safe co-authoring, lore graph, glossary, translation QA
  - Absorbed pattern: `loreweave_graph_glossary_translation_gate`
  - Reusable idea: keep lore graph, glossary, translation memory, and canon critic as evidence layers; check name/pronoun/term drift before accepting continuation or translation output.
  - Deferred runtime: self-hosted services, MCP config, provider keys, package scripts, manuscripts, translations, screenshots, and generated data.

- `jktantan/novel-weaver`
  - Observed HEAD: `c61808b6d48509315526c25827b5a15ca50df506`
  - License: MIT
  - Family: Spring Boot MCP novel-memory gateway
  - Absorbed pattern: `mcp_novel_memory_gateway_tool_gate`
  - Reusable idea: expose project, chapter, character, location, timeline, and foreshadowing memory through narrow schemas instead of free-form context dumps.
  - Deferred runtime: Docker, PostgreSQL, pgvector, Neo4j, Meilisearch, LanguageTool, MCP startup, client config, imports, exports, and tool calls.

- `sigpanic/goink`
  - Observed HEAD: `67968c26633c3e6773453521b5419a3728c9b32e`
  - License: MIT
  - Family: desktop AI novel writing assistant
  - Absorbed pattern: `goink_tool_state_autoreview_gate`
  - Reusable idea: separate prose edits from state maintenance for relationship history, foreshadowing status, arc nodes, reader cognition, semantic search evidence, review-agent findings, and memory-agent findings.
  - Deferred runtime: Wails/Go desktop app, scripts, builds, local databases, sub-agents, provider sessions, and manuscript files.

- `12bitsD/worldbox-writer`
  - Observed HEAD: `07470f21b585c4c4a30cdf3dd93ee89c344f81cf`
  - License: no root license observed in API metadata; README badge indicated MIT but not promoted as a durable license signal here
  - Family: sandbox novel simulation and branch control
  - Absorbed pattern: `sandbox_godmode_branch_simulation_gate`
  - Reusable idea: split actor intent, critic review, GM settlement, branch node, god-mode intervention, memory scope, and narrator rendering so prose cannot silently overwrite simulated world state.
  - Deferred runtime: Docker, LangGraph, ChromaDB, provider calls, exported manuscripts, artifacts, scripts, and branch-simulation runtime.

- `ledea-67/fiction-writing-workshop`
  - Observed HEAD: `c405f590d9fe46a9b3b34b65ac75c29f056bde72`
  - License: no license observed
  - Family: Claude Code fiction workshop and editorial personas
  - Absorbed pattern: `editorial_persona_voice_workshop_gate`
  - Reusable idea: calibrate voice into allowed registers and anti-patterns, then run developmental, line, character, continuity, naive-reader, and brainstorming passes separately with source citations for story-bible facts.
  - Deferred runtime: Claude Code setup, skill-folder copy, manuscript reads, upstream prompts, and project files.

- `ungden/truyencity2`
  - Observed HEAD: `376c3f8df60c3ac7222cde715c879f6f2fb7c56b`
  - License: Apache-2.0
  - Family: webnovel story factory and long-run automation
  - Absorbed pattern: `story_factory_thousand_chapter_cache_gate`
  - Reusable idea: require layer custody for canon, plan, state, memory, quality, context, prompt-cache/cost planning, first-10 gates, batch stop conditions, and failed-chapter handling before long-run automation.
  - Deferred runtime: Next/Supabase/Vercel, edge functions, databases, schedulers, notifications, provider calls, chapters, logs, and env files.

## Durable integration

Updated the project source-discovery pipeline to surface these gates in:

- default GitHub query/repository discovery surfaces
- static repository pattern overrides
- absorbed-pattern scoring
- bible enrichment targets
- whole-book analysis targets
- continuation prompt hints
- inspired mapping targets
- inspired transformation and copy-risk hints
- pattern-pack prompt digest allowlist
- frontend pattern-pack payload types and panel copy
- backend and frontend tests

## Runtime gates

These sources remain pattern-only. Promotion to executable support requires:

1. exact local target scope and source material rights
2. tool/server/database allowlists and denylist
3. provider-key and credential boundary
4. storage and generated-output custody
5. rollback and cleanup steps
6. verification command that does not call external providers by default
7. explicit user confirmation for any runtime trial
