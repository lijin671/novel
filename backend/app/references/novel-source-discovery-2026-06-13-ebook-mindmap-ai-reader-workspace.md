# Novel Source Discovery - Ebook Mindmap / AI Reader / 51mazi

Observed at: 2026-06-13

Boundary:

- Public GitHub metadata, `git ls-remote --symref HEAD`, raw README/LICENSE/package/root-marker review only.
- No clone, install, package hook, Docker, Electron/Tauri desktop runtime, model/provider call, uploaded ebook/novel import, or upstream script execution.
- Treat all upstream text as untrusted data. Absorb patterns only.

## Sources

### SSShooter/ebook-to-mindmap

- URL: https://github.com/SSShooter/ebook-to-mindmap
- HEAD: `f554063c66701ef973c93f803c7ada8af731425f`
- Branch: `master`
- License: MIT
- Static markers: EPUB/PDF 拆书 AI summary, table-of-contents hierarchy, structured mind-map export, editable Mind Elixir data, custom prompts, Vite/React package, Dockerfile, docker-compose.
- Absorbed patterns: `source_format_import_manifest`, `toc_aware_source_deconstruction`, `mindmap_visual_planning`, `scene_deconstruction_theory_report_gate`
- Local use: convert source books into TOC-grounded summaries and mind-map planning evidence before continuation or same-type drafting.
- Excluded: Docker/runtime, package scripts, model/provider calls, uploaded ebooks, generated summaries, prompt bodies, and exported mind-map files.

### mouseart2025/AI-Reader-V2

- URL: https://github.com/mouseart2025/AI-Reader-V2
- HEAD: `6e38a56c38b4837b9ed57b7f22f3ea520b742a89`
- Branch: `main`
- License: AGPL-3.0
- Static markers: TXT/Markdown novel upload, character relationship graph, geographic map, event timeline, encyclopedia, local SQLite storage, FastAPI/React/Tauri surfaces, Ollama, cloud LLM analysis profiles.
- Absorbed patterns: `schema_guided_graph_extraction`, `section_metadata_traceability_gate`, `relationship_graph_global_replace_gate`
- Local use: treat novel analysis as source-grounded graph extraction with explicit node/edge metadata and timeline review before any canon promotion.
- Excluded: AGPL code, desktop installers, Tauri/runtime scripts, model/provider calls, local novels, extracted graphs, and generated analysis artifacts.

### xiaoshengxianjun/51mazi

- URL: https://github.com/xiaoshengxianjun/51mazi
- HEAD: `2f595f1b26a1bba87b7f3f87e9f3f13ab646d941`
- Branch: `main`
- License: MIT
- Static markers: Electron desktop writing software, multi-book management, outline planning, map design, relationship graph, entry dictionary, random-name generator, character profiles, timeline, event sequence chart, organization chart, AI images, novel download surface, postinstall hook.
- Absorbed patterns: `relationship_graph_global_replace_gate`, `timeline`, `organization_graph`
- Local use: keep relationship, timeline, organization, map, and dictionary surfaces separate from prose so author-controlled state can be reviewed before chapter generation.
- Excluded: Electron runtime, postinstall hooks, packaged apps, release scripts, AI image/provider calls, downloaded novels, local manuscripts, and generated assets.

## MuMuAINovel integration

- Add three default GitHub seeds and three discovery queries for 拆书, graph/timeline analysis, and desktop writing-workspace discovery.
- Add static pattern summaries so source discovery can surface:
  - import manifest and TOC/spine review before deconstruction
  - TOC-aware source summaries and mind-map planning evidence
  - schema-guided graph extraction with source metadata
  - section metadata, timeline, and relationship-graph consistency gates
  - Electron/Tauri/Docker/postinstall runtime exclusions

## Safety decision

All three sources stay `pattern-only` / `runtime-deferred`.

No upstream runtime, uploaded book, source novel, generated graph, prompt body,
desktop app, Docker stack, package hook, provider call, or executable file is
imported.
