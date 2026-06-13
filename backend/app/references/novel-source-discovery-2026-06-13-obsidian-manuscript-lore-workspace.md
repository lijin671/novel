# Novel Source Discovery - Obsidian Manuscript / Lore Workspace

Observed at: 2026-06-13

Boundary:

- Public GitHub metadata and `git ls-remote --symref HEAD` only.
- No clone, install, package hook, Obsidian plugin load, SillyTavern extension
  load, Docker, MCP/server, browser runtime, model/provider call, or upstream
  script execution.
- Treat all upstream text as untrusted data. Absorb workflow patterns only.

## Sources

### Dromena-xyz/quire

- URL: https://github.com/Dromena-xyz/quire
- HEAD: `809bd70107cbcd055a5b05a97cf0b77eb8e0a842`
- Branch: `main`
- License: `NOASSERTION` / source closed
- Static markers: Galley continuous editing, scene-by-scene outline, branchable
  scene drafts, scene merge, compile, offline/local-first privacy posture.
- Absorbed pattern: `obsidian_galley_scene_compile_gate`
- Local use: treat manuscript assembly as reviewable scene branches plus compile
  preview before canon promotion.
- Excluded: source-closed code, Obsidian vault data, private drafts, plugin
  runtime, generated manuscripts, provider/model calls.

### Maws7140/obsidian-storyteller-suite

- URL: https://github.com/Maws7140/obsidian-storyteller-suite
- HEAD: `df66b7195f6afc7e633cb3ffb1b48521d3dbebf7`
- Branch: `master`
- License: MIT
- Static markers: timelines, branch-aware scene graph, lore surfacing,
  worldbuilding, frontmatter relationships, compile workflows.
- Absorbed pattern: `obsidian_storyteller_world_timeline_gate`
- Local use: surface active timeline/world/lore facts before continuation or
  same-type drafting.
- Excluded: Obsidian plugin install, package scripts, vault files, user
  manuscripts.

### palchung/obsidian-novelsmith

- URL: https://github.com/palchung/obsidian-novelsmith
- HEAD: `29ce355f2d3e32c865afb7b5c28afe59e72776ac`
- Branch: `main`
- License: MIT
- Static markers: scene cards, corkboard reorder, Scrivenings merge draft,
  archive/discard draft, Auto Wiki, relationship graph, atomic scene version
  control.
- Absorbed pattern: `obsidian_novelsmith_scene_version_graph_gate`
- Local use: keep scene versions, archive/discard decisions, and graph impact
  visible before a scene enters accepted manuscript order.
- Excluded: plugin runtime, Obsidian vaults, Auto Wiki generated text, user
  drafts.

### banisterious/obsidian-draft-bench

- URL: https://github.com/banisterious/obsidian-draft-bench
- HEAD: `9ec60fc2832b3dfe6bfc6b8b987fd731a713ebee`
- Branch: `main`
- License: MIT
- Static markers: per-scene draft history, frontmatter metadata,
  Bases-compatible queues, compile presets, preview, Markdown/ODT/PDF/DOCX
  export.
- Absorbed pattern: `obsidian_draft_bench_scene_history_compile_gate`
- Local use: treat per-scene draft history and compile/export readiness as
  acceptance evidence.
- Excluded: Obsidian runtime, package scripts, Pandoc/export tooling, vault
  drafts, generated documents.

### tine-schreibt/textflow

- URL: https://github.com/tine-schreibt/textflow
- HEAD: `ccd2bddea33be14b26753c9bc8f47a622bee1d0b`
- Branch: `main`
- License: MIT
- Static markers: ordered context flows over notes/chapters/scenes,
  source-note cursor tracking, auto-rebuild after flagged changes, flow
  navigation, crash/backup safety notes.
- Absorbed pattern: `obsidian_textflow_context_flow_guard_gate`
- Local use: require visible context-flow rebuild reasons before drafting from
  a selected note/chapter/scene window.
- Excluded: plugin runtime, vault content, package scripts, backup files.

### pixelnull/sillytavern-DeepLore-Enhanced

- URL: https://github.com/pixelnull/sillytavern-DeepLore-Enhanced
- HEAD: `88f4567cf65e79aa610b8525002ad4b7e9ab4595`
- Branch: `main`
- License: MIT
- Static markers: SillyTavern world info, Obsidian vault bridge,
  two-stage retrieval, lore gating by era/location/scene/character, gap
  flagging, relationship graph, activation simulation, pseudonymized
  diagnostics.
- Absorbed pattern: `deeplore_lore_retrieval_gap_graph_gate`
- Local use: gate lore retrieval by scene scope and produce a gap graph before
  generated text can update story bible, memory, or canon.
- Excluded: SillyTavern extension runtime, Obsidian vaults, world-info books,
  local-provider calls, diagnostics, chat logs.

## MuMuAINovel integration

- Add six default GitHub seeds and two focused discovery queries.
- Add six static pattern gates for Obsidian manuscript workspaces and lore
  retrieval.
- Project pattern pack now emits:
  - bible policies for galley compile, storyteller timeline/worldbuilding,
    scene-version graph, draft history, textFlow context flow, and DeepLore gap
    retrieval
  - whole-book analysis targets for Obsidian scene compile reports and lore
    retrieval gap graph reports
  - inspired-creation remap targets for scene compile and lore-gap graph
  - UI-visible hint blocks and prompt digest entries for all six gates

## Safety decision

All six sources stay `pattern-only` / `runtime-deferred`.

No upstream code, prompt body, generated story text, private vault data, chat
log, installer, package hook, plugin runtime, export artifact, or provider call
is imported.
