# Novel Source Discovery - 2026-06-11 Deconstruction / Platform / Memory / Codex Scaffold

## Scope

Static L0/L1 source-intake pass for拆书续写 and同类型仿写 support. No repositories were cloned, installed, or executed. Review used public GitHub search metadata, `git ls-remote --symref HEAD`, and raw README/LICENSE marker scans only.

Boundary marker:

```text
public_github_search_lsremote_raw_readme_license_marker_scan_no_login_no_clone_no_runtime_20260611_deconstruction_platform_memory_codex
```

## Reviewed Sources

- [`QQ-L-XX/novel-deconstruct`](https://github.com/QQ-L-XX/novel-deconstruct)
  - HEAD: `c75702bece3d110674452226528c0cb92c1b194a` on `master`
  - License: MIT
  - Family: novel deconstruction / Claude Code skill / webnovel source-study
  - Posture: `pattern-only`
  - Absorbed pattern: `scene_deconstruction_theory_report_gate`
  - Static markers: Novel Deconstruction, scene-level deep analysis, chapter quantitative scan, 18-chapter structured report, McKee / Xu Rongzhe theory framing, Fanqie URL input, font decoding, API capture, OCR/dependency install surface.

- [`d3nnywong/qidian-mcp-server`](https://github.com/d3nnywong/qidian-mcp-server)
  - HEAD: `9a4f033eeac1ce8e3a386f88e0b55ef666fbbca6` on `main`
  - License: no license observed in static pass
  - Family: platform research / MCP / webnovel market signal
  - Posture: `pattern-only`, `runtime-deferred`
  - Absorbed pattern: `platform_ranking_research_boundary_gate`
  - Static markers: Qidian ranking scan, book details, chapter structure, free chapter scope, AI-assisted deconstruction, MCP configuration, Playwright, optional Anthropic key.

- [`KanishkaV25/StorySync`](https://github.com/KanishkaV25/StorySync)
  - HEAD: `f4dbb29dfbff444e006e74283e855cd1de27588b` on `main`
  - License: no license observed in static pass
  - Family: RAG continuity assistant / story bible memory
  - Posture: `pattern-only`, `runtime-deferred`
  - Absorbed pattern: continuity QA vocabulary; no vector store or model runtime.
  - Static markers: story bible generation, structured memory facts, semantic retrieval, ChromaDB, continuity analysis, rewrite assistance, Gemini key setup.

- [`senjinthedragon/Smart-Memory`](https://github.com/senjinthedragon/Smart-Memory)
  - HEAD: `52f058cce1450a9417e28ad6319bd3204a12771f` on `main`
  - License: AGPL-3.0
  - Family: tiered memory / roleplay story continuity / SillyTavern extension
  - Posture: `pattern-only`
  - Absorbed pattern: `tiered_memory_fact_retirement_gate`
  - Static markers: long-term, session, and short-term memory; token usage display; memory context budget; activation triggers; fact retirement/replacement; entity state; relationship history; scene history; story arcs; rolling summaries.

- [`astrapi69/bibliogon`](https://github.com/astrapi69/bibliogon)
  - HEAD: `6aa53a98a07e20ae292bae589584b867cf5dede6` on `main`
  - License: MIT
  - Family: book authoring / story bible / self-publishing workbench
  - Posture: `pattern-only`
  - Absorbed pattern: `entity_mention_arc_timeline_gate`
  - Static markers: Story Bible entities, @-mentions, auto-detect linking, appearance tracker, Arc View swim-lane timeline, disappearance / absence-gap warnings, Markdown export, plugin ZIP install, encrypted credential storage, Git sync.

- [`rxb123ahuan/codexwriteskill`](https://github.com/rxb123ahuan/codexwriteskill)
  - HEAD: `6ab89a484da2d8d0e10149223b4f28288a533233` on `main`
  - License: MIT
  - Family: Codex story skill pack / oh-story port
  - Posture: `pattern-only`, selective route vocabulary only
  - Absorbed pattern: `codex_story_skill_project_scaffold_gate`
  - Static markers: Codex-readable `STORY.md`, `.codex-story/rules/`, tracking files, long/short deconstruction, market/ranking scan skills, Codex skill-installer commands.

## Durable Fusion

Added source discovery gates:

- `scene_deconstruction_theory_report_gate`
  - 拆书 reports must split source access from analysis.
  - Keep scene function, conflict turn, desire/obstacle, value shift, hook, payoff, and craft note as abstract fields.
  - Font decoding, OCR, API calls, or full-chapter scraping are runtime-deferred.

- `platform_ranking_research_boundary_gate`
  - Platform signals need platform,榜单,品类, observed date, and free/paid scope.
  - Ranking data may inform reader promise, pacing pressure, and trope saturation.
  - It must not become copied titles, book details, source chapter text, or proprietary tags.

- `tiered_memory_fact_retirement_gate`
  - Separate long-term facts, session details, short-term recap, entity state, relationship history, and arc memory.
  - Changed facts need retire/supersede evidence instead of accumulating contradictions.
  - Continuation audits should expose trimmed, omitted, and superseded memory.

- `entity_mention_arc_timeline_gate`
  - Link entities to chapter appearances before continuity and absence-gap checks.
  - Flag disappearances, long returns, unexpected role/mood changes, and unsupported chapter appearances.
  - Same-type creation must rebuild appearance rhythm on new entities.

- `codex_story_skill_project_scaffold_gate`
  - Codex story projects should expose `STORY.md`, rule files, tracking ledgers, analysis reports, and chapter tasks as separate artifacts.
  - Deconstruction and market-scan skills are route vocabulary until rights, command, and output boundaries are declared.

## Runtime Exclusions

No clone, install, package manager, skill install, MCP server, Playwright/browser, extension runtime, provider/model call, OCR/font decoding, platform scrape, credential read, chapter download, Git sync, plugin ZIP install, or local manuscript import was performed.

## Project Changes

Updated:

- `backend/app/services/source_discovery_service.py`
- `backend/app/services/source_pattern_pack_prompt.py`
- `backend/tests/services/test_source_discovery_service.py`

Verification target:

```powershell
python -m py_compile backend/app/services/source_discovery_service.py backend/app/services/source_pattern_pack_prompt.py backend/tests/services/test_source_discovery_service.py
python -m pytest backend/tests/services/test_source_discovery_service.py -q
python -m pytest backend/tests/api/test_source_discovery_api.py backend/tests/frontend/test_source_discovery_panel_copy.py backend/tests/services/test_source_discovery_service.py -q
```
