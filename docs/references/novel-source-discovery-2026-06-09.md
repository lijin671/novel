# Novel Source Discovery Ledger - 2026-06-09

## Scope

This ledger records public metadata candidates for MuMuAINovel novel automation.
No clone, install, package hook, Docker stack, MCP server, native binary, shell script, or browser extension was executed.

## Safety Notes

- 只采集公开元数据和公开摘要；不克隆、不安装、不执行外部项目。
- GitHub 与论坛候选默认按 pattern-only 沉淀，后续吸收必须单独做许可证、安装面和安全边界复核。
- Linux.do 仅使用公开 RSS/页面可访问摘要；不绕过登录、403、429、WAF 或 CAPTCHA。

## Provenance Notes

- RhythmicWave/NovelForge HEAD: 71db1420d919d676521a15f6999090b37db86fb0; posture pattern-only due AGPL-3.0 and runtime surface.
- NousResearch/autonovel HEAD: d165f267a0ffd34f3b0a70a8a72ac38cb8e4a542; posture pattern-only; README read as public text metadata only.
- kaigani/codeywood HEAD: 6eba4f27ca1699ada778ba2cd5af9d8e70700907; posture pattern-only due non-novel runtime and missing license metadata.
- KoboldAI/KoboldAI-Client HEAD: 1ce811c3f9f828ea80274640e866ca3189daf91f; default branch main; license AGPL-3.0; README read as public text metadata only.
- SillyTavern/SillyTavern HEAD: 51ad27fb86d39a3daca3adaa970375c9670c12df; default branch release; license AGPL-3.0; README plus public docs World Info and Author's Note pages read as public text metadata only.
- envy-ai/ai_rpg HEAD: bea1dd19a425c09eca40bf78e0a22589d3d9fb5a; default branch master; license missing/unknown; README read as public text metadata only.
- matrixorigin/Memoria HEAD: 37ca1e773af608c08b00a14f3814752c43df6c41; default branch main; license Apache-2.0; README read as public text metadata only.
- mrigankad/Novel-OS HEAD: c2866813b0a9077187ab5523c1baed1396018eff; default branch dev; license MIT; README read as public text metadata only.
- aikohanasaki/SillyTavern-MemoryBooks HEAD: bd50a36044f3e7170d38c724fa08ce37a9b7ee47; default branch main; license AGPL-3.0; README read as public text metadata only.
- bal-spec/sillytavern-character-memory HEAD: 96f528b9571ce2a0a322f770c40d71305ebd993e; default branch master; license missing/unknown; README read as public text metadata only.
- All sources were read only as public metadata or public README excerpts; no source code import or runtime trial was performed.
- No clone, install, package hook, Docker stack, MCP server, native binary, shell script, browser extension, provider call, credentials, cookies, or external repository code execution was performed.

## Fetch Limits And Failures

- github: https://github.com/Anshler/graphify-novel — Repository not found during candidate check; skipped.

## Candidates

### NousResearch/autonovel

- URL: https://github.com/NousResearch/autonovel
- Source: github
- Family: novel-automation
- Posture: pattern-only
- Posture hint: metadata-triage
- Stars: 1400
- License: MIT
- Risk flags: none
- Trust flags: zero-issues-high-stars
- Absorbed patterns: chapter_generation, style_signature, self_review, quality_score_loop, voice_fingerprint, anti_slop_audit, publication_pipeline
- Summary: Autonomous novel pipeline from seed concept to print-ready PDF, ePub, audiobook and landing page. Uses modify-evaluate-keep/discard, foundation_score, chapter scoring, plateau detection, voice fingerprint, anti-slop scorer, anti-pattern rules, reader panel and dual-persona review.

### voocel/ainovel-cli

- URL: https://github.com/voocel/ainovel-cli
- Source: github
- Family: novel-automation
- Posture: pattern-only
- Posture hint: metadata-triage
- Stars: 1280
- License: MIT
- Risk flags: none
- Trust flags: zero-issues-high-stars
- Absorbed patterns: chapter_generation, continuation, style_signature, book_decomposition, worldbuilding, timeline, character_cards, organization_graph, emotion_arc, self_review
- Summary: AI novel writing CLI with chapter generation, continuation, story bible and style analysis.

### RhythmicWave/NovelForge

- URL: https://github.com/RhythmicWave/NovelForge
- Source: github
- Family: novel-automation
- Posture: pattern-only
- Posture hint: metadata-triage
- Stars: 921
- License: AGPL-3.0
- Risk flags: none
- Trust flags: none
- Absorbed patterns: chapter_generation, card_workbench, structured_generation_schema, context_reference, workflow_agent_pipeline, book_decomposition, worldbuilding, timeline, character_cards, organization_graph, emotion_arc, self_review
- Summary: AI assisted longform novel creation engine with schema-first card-based creation, JSON Schema structured generation, context injection, knowledge graph, workflow agent, chapter generation, story bible and progress recovery.

### mrigankad/Novel-OS

- URL: https://github.com/mrigankad/Novel-OS
- Source: github
- Family: novel-automation
- Posture: pattern-only
- Posture hint: metadata-triage
- Stars: 12
- License: MIT
- Risk flags: none
- Trust flags: default-branch:nonstandard
- Absorbed patterns: workflow_agent_pipeline, quality_score_loop, world_state_tracking, memory_snapshot_versioning
- Summary: Multi-agent AI framework that writes full-length novels with persistent story state, a deterministic continuity engine, and a five-role editorial pipeline. Static intake note: Multi-agent fiction writing framework with persistent story state, central StoryState JSON, deterministic continuity engine, five-role editorial pipeline, chapter quality scores, and state parser merge flow.

### KoboldAI/KoboldAI-Client

- URL: https://github.com/KoboldAI/KoboldAI-Client
- Source: github
- Family: novel-automation
- Posture: pattern-only
- Posture hint: metadata-triage
- Stars: 1700
- License: AGPL-3.0
- Risk flags: none
- Trust flags: zero-issues-high-stars
- Absorbed patterns: lorebook_context, author_note_layer
- Summary: Browser-based front-end for AI-assisted writing. Static intake note: AI-assisted writing front-end for story and novel use cases. Public README describes Memory, Author's Note, World Info, Save & Load, regular story writing, novel models, adventure mode, and writing assistant workflows.

### SillyTavern/SillyTavern

- URL: https://github.com/SillyTavern/SillyTavern
- Source: github
- Family: novel-automation
- Posture: pattern-only
- Posture hint: defer-trust-review
- Stars: 45000
- License: AGPL-3.0
- Risk flags: none
- Trust flags: zero-issues-high-stars, default-branch:nonstandard
- Absorbed patterns: context_reference, lorebook_context, author_note_layer
- Summary: LLM frontend for power users. Static intake note: LLM fiction and roleplay front-end with WorldInfo lorebooks. Official public docs describe World Info / Lorebooks / Memory Books, keyword activation, scan depth, recursive scanning, insertion order, token budget, Author's Note, and context injection.

### matrixorigin/Memoria

- URL: https://github.com/matrixorigin/Memoria
- Source: github
- Family: novel-automation
- Posture: pattern-only
- Posture hint: metadata-triage
- Stars: 3600
- License: Apache-2.0
- Risk flags: none
- Trust flags: zero-issues-high-stars
- Absorbed patterns: continuation, memory_snapshot_versioning
- Summary: Git for AI Agent Memory: Snapshot, Branch, Merge, Rollback. Static intake note: AI agent memory infrastructure with snapshot, branch, merge, rollback, and Git-like memory versioning. Pattern-only adaptation for long-form novel continuation state snapshots and reversible context changes.

### bal-spec/sillytavern-character-memory

- URL: https://github.com/bal-spec/sillytavern-character-memory
- Source: github
- Family: novel-automation
- Posture: pattern-only
- Posture hint: metadata-triage
- Stars: 58
- License: unknown
- Risk flags: browser_extension
- Trust flags: license:missing
- Absorbed patterns: character_cards, emotion_arc, style_signature, context_reference, world_state_tracking
- Summary: SillyTavern extension that automatically extracts structured character memories from chat and stores them in the Data Bank for vector-based retrieval at generation time. Static intake note: SillyTavern character memory extension that extracts structured relationship, event, fact, and emotional memories into editable markdown Data Bank files with vector retrieval, injection viewer, token breakdown, health checks, and undoable memory control.

### envy-ai/ai_rpg

- URL: https://github.com/envy-ai/ai_rpg
- Source: github
- Family: novel-automation
- Posture: pattern-only
- Posture hint: metadata-triage
- Stars: 120
- License: unknown
- Risk flags: none
- Trust flags: license:missing
- Absorbed patterns: worldbuilding, self_review, world_state_tracking
- Summary: AI RPG solo tabletop game master with structured prompts. Static intake note: AI RPG turns a model into a solo tabletop game master for story generation. Public README describes structured prompts, players, locations, regions, items, world state, settings, and review logs.

### aikohanasaki/SillyTavern-MemoryBooks

- URL: https://github.com/aikohanasaki/SillyTavern-MemoryBooks
- Source: github
- Family: novel-automation
- Posture: pattern-only
- Posture hint: metadata-triage
- Stars: 221
- License: AGPL-3.0
- Risk flags: browser_extension
- Trust flags: none
- Absorbed patterns: lorebook_context, memory_snapshot_versioning
- Summary: Saves SillyTavern chat memories to lorebooks. Static intake note: SillyTavern memory extension for structured memory creation into lorebooks. Public README describes scenes as memories, clips, side prompts, JSON summaries, compaction, consolidation, lorebook ordering, and multi-tier memory rollups.

### kaigani/codeywood

- URL: https://github.com/kaigani/codeywood
- Source: github
- Family: novel-automation
- Posture: pattern-only
- Posture hint: metadata-triage
- Stars: 21
- License: unknown
- Risk flags: none
- Trust flags: license:missing
- Absorbed patterns: self_review, scene_asset_pipeline, book_decomposition, worldbuilding, timeline, character_cards, organization_graph, emotion_arc
- Summary: Claude Code based skills for AI filmmaking from idea to production, screenplay planning, storyboard, shot list, scene plan and multi-stage review.

## Next Absorption Targets

- Use candidates as pattern references for source-book analysis, continuation state, style signature, and self-review loops.
- Do not import upstream runtime code without a separate local safety contract.
