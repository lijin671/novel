# Novel Source Discovery Ledger - 2026-05-31

## Scope

This ledger records public metadata candidates for MuMuAINovel novel automation.
No clone, install, package hook, Docker stack, MCP server, native binary, shell script, or browser extension was executed.

## Safety Notes

- 只采集公开元数据和公开摘要；不克隆、不安装、不执行外部项目。
- GitHub 与论坛候选默认按 pattern-only 沉淀，后续吸收必须单独做许可证、安装面和安全边界复核。
- Linux.do 仅使用公开 RSS/页面可访问摘要；不绕过登录、403、429、WAF 或 CAPTCHA。

## Candidates

### Deng-m1/MaliangAINovalWriter

- URL: https://github.com/Deng-m1/MaliangAINovalWriter
- Source: github
- Family: novel-automation
- Posture: pattern-only
- Stars: 780
- License: Apache-2.0
- Risk flags: none
- Absorbed patterns: chapter_generation
- Summary: 马良AI写作是一个专为小说作者与平台运营者设计的智能化创作平台。它结合了强大的AI模型（支持OpenAI, Gemini, Anthropic等）与专业的在线富文本编辑器，旨在帮助作者激发灵感、提高写作效率、管理创作内容，同时为平台管理员提供了强大的后台管理与监控功能。

### voocel/ainovel-cli

- URL: https://github.com/voocel/ainovel-cli
- Source: github
- Family: novel-automation
- Posture: pattern-only
- Stars: 313
- License: Apache-2.0
- Risk flags: none
- Absorbed patterns: chapter_generation
- Summary: ✨多agent实现全自动AI小说生成

### leew666/aiNovel

- URL: https://github.com/leew666/aiNovel
- Source: github
- Family: novel-automation
- Posture: pattern-only
- Stars: 3
- License: BSD-3-Clause
- Risk flags: none
- Absorbed patterns: source_discovery
- Summary: 使用ai创作小说

### yulan233/CLINovel

- URL: https://github.com/yulan233/CLINovel
- Source: github
- Family: novel-automation
- Posture: pattern-only
- Stars: 2
- License: unknown
- Risk flags: none
- Absorbed patterns: source_discovery
- Summary:

## Next Absorption Targets

- Use candidates as pattern references for source-book analysis, continuation state, style signature, and self-review loops.
- Do not import upstream runtime code without a separate local safety contract.
