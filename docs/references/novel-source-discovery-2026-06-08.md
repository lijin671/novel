# Novel Source Discovery Ledger - 2026-06-08

## Scope

This ledger records public metadata candidates for MuMuAINovel novel automation.
No clone, install, package hook, Docker stack, MCP server, native binary, shell script, or browser extension was executed.

## Safety Notes

- 只采集公开元数据和公开摘要；不克隆、不安装、不执行外部项目。
- GitHub 与论坛候选默认按 pattern-only 沉淀，后续吸收必须单独做许可证、安装面和安全边界复核。
- Linux.do 仅使用公开 RSS/页面可访问摘要；不绕过登录、403、429、WAF 或 CAPTCHA。

## Candidates

### KazKozDev/NovelGenerator

- URL: https://github.com/KazKozDev/NovelGenerator
- Source: github
- Family: novel-automation
- Posture: pattern-only
- Posture hint: metadata-triage
- Stars: 134
- License: NOASSERTION
- Risk flags: none
- Trust flags: license:noassertion
- Absorbed patterns: chapter_generation, worldbuilding, character_cards, emotion_arc, style_signature, book_decomposition, timeline, organization_graph, self_review
- Summary: Fiction generator using LLM agents to create complete novels with coherent plots, developed characters, worldbuilding, chapter generation, emotional arcs, and diverse writing styles.

### voocel/ainovel-cli

- URL: https://github.com/voocel/ainovel-cli
- Source: github
- Family: novel-automation
- Posture: pattern-only
- Posture hint: metadata-triage
- Stars: 454
- License: Apache-2.0
- Risk flags: none
- Trust flags: none
- Absorbed patterns: chapter_generation, continuation, style_signature, book_decomposition, worldbuilding, timeline, character_cards, organization_graph, emotion_arc, self_review
- Summary: Multi-agent automatic AI novel generation CLI with chapter generation, continuation, story bible and style analysis.

### NousResearch/autonovel

- URL: https://github.com/NousResearch/autonovel
- Source: github
- Family: novel-automation
- Posture: pattern-only
- Posture hint: defer-trust-review
- Stars: 1099
- License: unknown
- Risk flags: none
- Trust flags: license:missing, downloads:enabled-high-stars
- Absorbed patterns: character_cards, style_signature, self_review
- Summary: An autonomous novel writing pipeline by Hermes Agent with characters, style evaluation, review, and manuscript pipeline.

### YuanShiJiLoong/author

- URL: https://github.com/YuanShiJiLoong/author
- Source: github
- Family: novel-automation
- Posture: pattern-only
- Posture hint: metadata-triage
- Stars: 157
- License: AGPL-3.0
- Risk flags: docker
- Trust flags: none
- Absorbed patterns: worldbuilding, self_review
- Summary: Author is an AI-powered writing platform for novelists and screenwriters with local-first worldbuilding manager, AI memory, preview, and accept/reject workflow.

### raestrada/storycraftr

- URL: https://github.com/raestrada/storycraftr
- Source: github
- Family: novel-automation
- Posture: pattern-only
- Posture hint: metadata-triage
- Stars: 142
- License: MIT
- Risk flags: none
- Trust flags: none
- Absorbed patterns: worldbuilding
- Summary: Open-source AI-powered tool that helps writers craft stories, generate worldbuilding details, create book outlines and chapters through a CLI.

### brandburner/fabula

- URL: https://github.com/brandburner/fabula
- Source: github
- Family: novel-automation
- Posture: pattern-only
- Posture hint: metadata-triage
- Stars: 32
- License: unknown
- Risk flags: none
- Trust flags: license:missing
- Absorbed patterns: character_cards, organization_graph, emotion_arc
- Summary: Turn television drama into storyworld knowledge graphs with two-pass extraction, entity resolution, character, location, object, organization, event and relationship checks.

### leenbj/novel-creator-skill

- URL: https://github.com/leenbj/novel-creator-skill
- Source: github
- Family: novel-automation
- Posture: pattern-only
- Posture hint: metadata-triage
- Stars: 406
- License: unknown
- Risk flags: none
- Trust flags: license:missing
- Absorbed patterns: source_discovery
- Summary: AI ?????????????????? Smart State???????????????????????RAG/?????????????

## Next Absorption Targets

- Use candidates as pattern references for source-book analysis, continuation state, style signature, and self-review loops.
- Do not import upstream runtime code without a separate local safety contract.
