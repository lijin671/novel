# Static intake: external project boundaries, visible outlines, weighted RAG - 2026-06-13

## Boundary

This intake used public GitHub Search, public `git ls-remote`, and small public
README/LICENSE marker probes.

No upstream repository was cloned, installed, built, executed, imported, indexed,
or used as a runtime dependency. MCP servers, npm/npx/Smithery/Homebrew/Docker
install flows, Tauri/Rust/Svelte builds, Fastify/Vue services, ChromaDB,
Python bridges, LLM calls, local `.scriv` projects, SQLite project files,
uploaded settings, vector databases, exports, reports, and manuscript data
remain excluded.

## Sources

### writerslogic/scrivener-mcp

- URL: https://github.com/writerslogic/scrivener-mcp
- HEAD: `c2ae9ebe30ba9bdd11ebc0036186972d3d767b89`
- License: AGPL-3.0.
- Static markers reviewed: README, LICENSE.
- Posture: pattern-only / runtime-deferred.
- Absorbed gate: `scrivener_mcp_project_analysis_boundary_gate`.

Reusable pattern:

- Treat external manuscript containers such as `.scriv` projects as explicit
  project-boundary artifacts.
- Split permissions by read, analyze, search, and edit scope.
- Convert direct project analysis into review proposals with author acceptance.
- Keep bridge findings separate from accepted story canon until the author
  approves them.

Blocked surface:

- npm/npx/Smithery/Homebrew/Docker install flows, MCP server launch,
  auto-configuration, `.scriv` project access, editing tools, local manuscripts,
  and assistant runtime.

### smith-and-web/kindling

- URL: https://github.com/smith-and-web/kindling
- HEAD: `fb67c06ff6e26983e42977624b427dd889abc90d`
- License: MIT.
- Static markers reviewed: README, LICENSE.
- Posture: pattern-only.
- Absorbed gate: `kindling_local_outline_reference_import_gate`.

Reusable pattern:

- Keep scene beats visible beside the drafting surface.
- Separate outline prompts, reference links, and accepted prose.
- Track import/export custody across Scrivener, Plottr, yWriter, Obsidian
  Longform, Markdown, DOCX, EPUB, and Treatment outputs.
- Use smart reference detection as metadata, not as automatic canon mutation.

Blocked surface:

- Tauri/Rust/Svelte runtime, installers, release assets, local SQLite projects,
  parser execution, imports/exports, and manuscript data.

### jianghuaqi85-sys/Novel-Consistency-Checker

- URL: https://github.com/jianghuaqi85-sys/Novel-Consistency-Checker
- HEAD: `a505efac61be4b9d01959d2a17037cb17b7e8e3f`
- License: MIT.
- Static markers reviewed: README, LICENSE.
- Posture: pattern-only.
- Absorbed gate: `novelengine_weighted_rag_consistency_gate`.

Reusable pattern:

- Treat 吃书 prevention as a weighted memory-retrieval problem.
- Store raw setting chunks and structured memory cards separately.
- Search characters, events, factions, locations, raw chunks, foreshadowing,
  and timeline with explicit lane weights.
- Emit conflict warnings with source memory refs, severity, suggested fix, and
  incremental review status.

Blocked surface:

- Fastify/Vue runtime, Python bridge, ChromaDB execution, LLM calls, prompt
  bodies, uploaded settings, vector databases, and generated conflict reports.

## Project changes

- Added seed URLs and GitHub queries for external manuscript project boundaries,
  visible outline/reference import-export workflows, and weighted RAG consistency
  checking.
- Added pattern-pack hint fields so拆书、续写、同类型仿写 can use these structures
  without importing upstream runtimes or manuscript data.
- Added front-end labels so the source discovery panel exposes the new gates.

## Verification commands

```powershell
python -m py_compile backend/app/services/source_discovery_service.py backend/app/services/source_pattern_pack_prompt.py backend/tests/services/test_source_discovery_service.py backend/tests/frontend/test_source_discovery_panel_copy.py
python -m pytest backend/tests/services/test_source_discovery_service.py::test_static_external_project_outline_weighted_rag_sources_are_absorbed -q
python -m pytest backend/tests/frontend/test_source_discovery_panel_copy.py -q
npm --prefix frontend run build
git diff --check
```
