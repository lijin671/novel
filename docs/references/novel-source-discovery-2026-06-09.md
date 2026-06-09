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
- kaigani/codeywood HEAD: 6eba4f27ca1699ada778ba2cd5af9d8e70700907; posture pattern-only due non-novel runtime and missing license metadata.
- NovelForge README was read only as public text metadata; no source code import or runtime trial was performed.
- No clone, install, package hook, Docker stack, MCP server, native binary, shell script, browser extension, or external repository code execution was performed.

## Fetch Limits And Failures

- github: https://api.github.com/repos/RhythmicWave/NovelForge — GitHub REST API unauthenticated rate limit exceeded during metadata refresh; HEAD verified by git ls-remote.
- github: https://api.github.com/repos/kaigani/codeywood — GitHub REST API unauthenticated rate limit exceeded during metadata refresh; HEAD verified by git ls-remote.

## Candidates

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
