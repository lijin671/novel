# Novel source discovery - local-first editor / Theia / API production patterns

Date: 2026-06-13

Scope: static public GitHub intake for拆书续写、同类型仿写、长篇小说工作流。

No repository was cloned, installed, built, or executed. No package manager,
Docker stack, Tauri app, Theia/NestJS runtime, Go API server, Discord bot,
provider call, media-generation flow, browser storage, credential file, user
manuscript, or upstream generated text was imported.

## Sources

- `kazormia296/Grimodex`
  - URL: `https://github.com/kazormia296/Grimodex`
  - Observed HEAD: `a9a5c3bed194ebd44b43b2f48d9f62819b85c8d2`
  - Branch: `master`
  - License posture: Elastic-2.0 / GitHub `NOASSERTION`
  - Static markers: manuscript + AI chat + Codex layout, Tauri + React,
    local SQLite, scene editor, AI chat per scene, extraction of characters /
    worldbuilding / snippets, origin attribution as human / AI / unknown,
    Japanese typesetting, prose linter.

- `StanleyChanH/SuperNovel`
  - URL: `https://github.com/StanleyChanH/SuperNovel`
  - Observed HEAD: `5075cd8183face4f329da78df8b0766e716d4341`
  - Branch: `master`
  - License posture: no license observed
  - Static markers: Novel Setting Workshop, architecture stage, chapter
    blueprint, chapter draft, finalization, State Tracking System, character
    development trajectory, foreshadowing management, semantic search,
    knowledge-base references, contradiction proofreading.

- `keysforthewin/screenplay`
  - URL: `https://github.com/keysforthewin/screenplay`
  - Observed HEAD: `60234558f6f6adca7f4477b362d8fbe8da223cb3`
  - Branch: `main`
  - License posture: no license observed
  - Static markers: collaborative writers-room, Discord colleague bot,
    browser real-time editor, mutable character templates, bulk character
    updates, ordered beats, current beat pointer, Director notes, attachments,
    TheMovieDB grounding, concept art, video clips, PDF/CSV export.

- `sagar0163/Nebula-Writer-2`
  - URL: `https://github.com/sagar0163/Nebula-Writer-2`
  - Observed HEAD: `43cc7cf9f7ca003d1f087817cb083408ec101bd0`
  - Branch: `main`
  - License posture: no license observed in GitHub metadata
  - Static markers: fiction System of Record, Codex SQLite store, characters,
    locations, items, relationships, chapter version history, character
    knowledge, auto-extract from prose, ChromaDB semantic search, consistency
    check, Mermaid relationship graph, DOCX export.

- `dandanthedan/forfiction-theia`
  - URL: `https://github.com/dandanthedan/forfiction-theia`
  - Observed HEAD: `6a97fe6d3428c81c3d0c5908f1ee83198ac078c9`
  - Branch: `main`
  - License posture: no license observed
  - Static markers: Theia shell + NestJS backend, `story-memory`,
    `story-preferences`, Monaco streaming insert, `story-chat` agents,
    `story-explorer`, `skill.yaml` loader, Theia AI prompt fragments,
    lorebook, Supabase auth/DB.

- `mariamjensen42-glitch/inkos`
  - URL: `https://github.com/mariamjensen42-glitch/inkos`
  - Observed HEAD: `e6d485d43cf7e21493511e99461e0c812d741ef7`
  - Branch: `master`
  - License: AGPL-3.0
  - Static markers: single-binary Go API, `inkos.json`, `books/`, `story/*.md`,
    `memory.db`, `play.db`, REST/SSE endpoints, truth files, sessions, agent
    sessions, daemon, logs, fanfic/spinoff/imitation, radar, doctor diagnostic,
    OpenAI-compatible provider config, `.inkos/secrets.json`.

## Absorbed patterns

- `grimodex_codex_attribution_scene_chat_gate`
  - Scene-chat extraction must preserve origin and reviewer state before Codex
    promotion.

- `supernovel_architecture_blueprint_state_search_gate`
  - Architecture, blueprint, draft, finalization, state tracking, semantic
    search, and contradiction proofreading become separate checkpoints.

- `screenplay_realtime_writers_room_media_boundary_gate`
  - Ordered beats, current beat pointer, Director notes, and mutable character
    templates are useful text workflow patterns; media/provider surfaces remain
    boundary-only.

- `nebula_codex_character_knowledge_version_gate`
  - Character knowledge, chapter version history, extracted entities, and graph
    previews need provenance and consistency review.

- `forfiction_theia_story_extension_skill_gate`
  - Theia-style extensions become explicit context slots and workflow roles;
    `skill.yaml` is absorbed only as a contract shape.

- `inkos_truthfile_api_fanfic_imitation_gate`
  - Truth-file APIs and doctor diagnostics are useful state-envelope patterns;
    fanfic/spinoff/imitation are high-risk rights and copy-review gates.

## Runtime exclusions

Blocked for this intake:

- clone, checkout, install, build, package scripts, setup scripts
- Docker/container launch, Tauri app, Theia/NestJS runtime, Go API server
- Discord bot, browser editor, real-time collaboration, SSE runtime
- provider/model/API calls, media generation, TheMovieDB lookup
- local SQLite, ChromaDB, Supabase/PostgreSQL, vector stores, browser storage
- `.env`, `.inkos/secrets.json`, API keys, OAuth/auth/session state
- user manuscripts, sample projects, generated chapters, screenplay exports,
  attachments, screenshots, graph exports, PDF/CSV/DOCX files
- Elastic/AGPL/no-license code reuse

## Local adaptation

MuMuAINovel uses these sources only as repo-native workflow vocabulary:

- Codex attribution + scene-chat extraction
- architecture/blueprint/state-search checkpoints
- realtime writers-room beat and Director-note policies
- Codex character-knowledge version reports
- Theia story-extension / skill-contract remaps
- truth-file API + fanfic/imitation rights gates

The implementation is covered by
`test_local_first_editor_theia_api_production_sources_are_static_absorbed`.
