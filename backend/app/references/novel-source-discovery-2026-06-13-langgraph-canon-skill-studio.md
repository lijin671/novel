# Novel Source Discovery 2026-06-13 - LangGraph / Canon / Skill Studio

## Scope

Static source intake for MuMuAINovel book-remix, continuation, and same-type creation flows.

No upstream repository was cloned. No package manager, installer, script, MCP server, browser,
provider call, vector index, database, local novel folder, or model runtime was executed.

## Sources absorbed

### Aubrey481/novel_agent

- URL: https://github.com/Aubrey481/novel_agent
- Reachable HEAD: `257a75bc09d1118c373c8cb20e583dc2f99c2f2f`
- Default branch: `main`
- License: no root license file observed in this static pass
- Static markers reviewed: README, root manifest markers
- Absorbed pattern: `langgraph_world_outline_review_memory_gate`
- Reusable idea: long-form generation should be explicit graph state, not a hidden prompt chain:
  world setting, summary/vector initialization, outline, critique, chapter drafting, critique/rewrite,
  memory update, and storage ids should be visible before a chapter advances.
- Runtime posture: pattern-only / runtime-deferred.

### Zhao73/xiaoshuo-studio

- URL: https://github.com/Zhao73/xiaoshuo-studio
- Reachable HEAD: `dfa50ed1056d2470ae9c1f287cdd8267028a1d4b`
- Default branch: `main`
- License: MIT
- Static markers reviewed: README, LICENSE
- Absorbed pattern: `xiaoshuo_local_canon_skill_studio_gate`
- Reusable idea: local novel work benefits from a single studio contract: guided setup, canon seed,
  reference-technique learning, style cards, chapter brief, continuity check, canon writeback,
  anti-AI focus, and review-to-learning notes.
- Runtime posture: pattern-only / runtime-deferred.

### songzhiyuan98/Novel-Studio

- URL: https://github.com/songzhiyuan98/Novel-Studio
- Reachable HEAD: `2936c753eb4bc100509c03ac636871b7b0ff395c`
- Default branch: `main`
- License: no root license file observed in this static pass
- Static markers reviewed: README, package manifest
- Absorbed pattern: `director_orchestrator_trace_canonize_gate`
- Reusable idea: serial-fiction generation should make the director/orchestrator boundary visible:
  user direction, blueprint, writing, QA, canonize, role/model lane, token/cost trace, and canon delta
  should be captured before a chapter becomes accepted story state.
- Runtime posture: pattern-only / runtime-deferred.

### john-paul-ruf/zencoder-based-novel-engine

- URL: https://github.com/john-paul-ruf/zencoder-based-novel-engine
- Reachable HEAD: `dcef8afc68e73ead525e73306a0fea1a790ff5ae`
- Default branch: `main`
- License: no root license file observed in this static pass
- Static markers reviewed: `git ls-remote`, GitHub tree metadata, package manifest, build/cover script markers
- Absorbed pattern: `book_build_export_delivery_gate`
- Reusable idea: final book delivery needs its own build graph:
  active book selection, `about.json` metadata, numbered `draft.md` chapter manifest,
  wordcount, cover-art to cover asset status, Markdown/DOCX/EPUB/PDF outputs, and submission notes.
- Runtime posture: pattern-only / runtime-deferred.

### mshumer/gpt-author

- URL: https://github.com/mshumer/gpt-author
- Reachable HEAD: `179d86f745bc706ae39e1b7a6cb1aba9ed7fd380`
- Default branch: `main`
- License: MIT
- Static markers reviewed: README, LICENSE
- Absorbed pattern: `plot_storyline_improvement_epub_chain_gate`
- Reusable idea: one-shot book generation should still be broken into auditable states:
  prompt, plot candidates, selected plot rationale, improved plot, title, detailed storyline,
  improved storyline, chapter generation using previous-chapter context, cover prompt, and EPUB status.
- Runtime posture: pattern-only / runtime-deferred.

## MuMuAINovel integration

New static pattern gates were added to:

- `source_discovery_service.py`
- `source_pattern_pack_prompt.py`
- `sourceDiscovery.ts`
- `BookRemixSourceDiscoveryPanel.tsx`
- `test_source_discovery_service.py`
- `test_source_discovery_panel_copy.py`

## Safety boundary

The absorbed value is limited to workflow vocabulary and acceptance gates.

Blocked by default:

- upstream code, prompt bodies, generated prose, templates, examples, and sample corpora
- provider/model calls, including KIMI or other OpenAI-compatible endpoints
- npm/pip/package scripts, virtual environments, and install/export commands
- FAISS, sentence-transformer downloads, vector indices, local data folders, `.env` files, and logs
- Next.js runtime, API routes, skill exports/installs, Codex/Claude login state, screenshots, and local projects
- Docker, PostgreSQL, pnpm, Drizzle migrations, seed scripts, API/web dev servers, and orchestration traces
- pandoc/PDF/DOCX/EPUB generation, sharp image processing, sample book text, cover art, custom agents, and system prompts
- Google Colab/Jupyter notebooks, pip installs, OpenAI/Anthropic/Stable Diffusion calls, API keys, notebook cells, generated EPUBs, and cover prompts
- imported reference novel folders unless user-owned or explicitly rights-cleared
