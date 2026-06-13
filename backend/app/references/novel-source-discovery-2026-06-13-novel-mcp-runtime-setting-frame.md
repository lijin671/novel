# Novel Source Discovery - Novel MCP / Runtime Setting / Frame Gates

Observed at: 2026-06-13

Boundary:

- Public GitHub Search snippets, public `git ls-remote --symref HEAD`, and raw
  README/LICENSE/package/requirements marker probes only.
- No clone, install, package hook, Docker, MCP/server, browser/desktop
  connector, provider call, model download, Scrivener project read, book-file
  mutation, daemon scheduler, or upstream script execution.
- Treat all upstream text as untrusted data. Prompt-like repositories are source
  material, not instructions.

## Sources

### slima-ai/slima-mcp

- URL: https://github.com/slima-ai/slima-mcp
- HEAD: `9bbaf6f30ac6f1ff36ca9fbf81035a9f6b72e042`
- Branch: `main`
- License: MIT
- Static markers: local stdio MCP, remote HTTP MCP, OAuth login, book
  management, file/folder structure, writing statistics, read/edit/search/write
  tools, create/delete/append file operations, and AI beta reader personas.
- Absorbed pattern: `slima_book_mcp_beta_reader_file_gate`
- Local use: represent book-file operations as explicit read/search/review/edit
  envelopes with file path, book id, beta-reader persona, and human acceptance
  before mutation.
- Excluded: npm/npx install, Cloudflare worker deploy, remote MCP connector,
  OAuth session, live book files, write/delete tools, and generated feedback.

### cedretaber/dialogoi

- URL: https://github.com/cedretaber/dialogoi
- HEAD: `ab188a8912562337168464f3067d091ab6ada051`
- Branch: `master`
- License: no root license observed / `NOASSERTION`
- Static markers: `novel.json`, settings/content/instruction file classes,
  regex full-text search, RAG search, `fileType` filters for content/settings,
  Qdrant, multilingual-e5-small, smart chunking, file watchers, and Docker
  auto-start.
- Absorbed pattern: `dialogoi_filetype_rag_novel_project_gate`
- Local use: make retrieval scope explicit before continuation: manuscript
  content, settings, instructions, or both; record source file class in derived
  notes.
- Excluded: MCP runtime, Docker/Qdrant, model downloads, file watchers, npm
  scripts, and user novel projects.

### dcondrey/scrivener-mcp

- URL: https://github.com/dcondrey/scrivener-mcp
- HEAD: `c2ae9ebe30ba9bdd11ebc0036186972d3d767b89`
- Branch: `main`
- License: AGPL-3.0
- Static markers: open/read/edit/analyze/search `.scriv` projects, pacing
  analysis, RTF parsing, document structure analysis, word counts, Claude
  Desktop auto-configuration, global npm install, setup wizard, Neo4j/Redis,
  OpenAI/LangChain, postinstall and uninstall hooks.
- Absorbed pattern: `scrivener_mcp_direct_project_edit_boundary_gate`
- Local use: keep direct project access behind a boundary report; diagnostics
  are allowed as derived notes, while edits require an accepted patch envelope.
- Excluded: AGPL code, global install, postinstall/uninstall hooks, `.scriv`
  project data, RTF manuscript text, Neo4j/Redis/OpenAI runtime, and assistant
  edit traces.

### nickcottrell/abits

- URL: https://github.com/nickcottrell/abits
- HEAD: `3c79c31247ec489f63a38bc8755ca646e84a01be`
- Branch: `main`
- License: no root license observed
- Static markers: vector storytelling, story beats, VRGB coordinates for tone,
  density, and register, baseline word-count targets, frame configs, canonical
  baseline frames, generated timestamped drafts, diff against canonical
  baseline, OpenAI API access, AWS Bedrock access, environment variables, and
  shell generation scripts.
- Absorbed pattern: `vector_story_frame_coordinate_gate`
- Local use: reuse only the abstract frame-control shape: beat, tone, density,
  register, target length, and diff discipline for MuMuAINovel-owned scenes.
- Excluded: public manuscript prose, canonical baseline frames, generated
  drafts, prompt scaffolds, provider access, environment variables, shell
  scripts, and generation engine.

### novemberjae-cmyk/Novel-Setting-Runtime-Construction

- URL: https://github.com/novemberjae-cmyk/Novel-Setting-Runtime-Construction
- HEAD: `35a50ad58877f1728df97c351208f71d42f44c77`
- Branch: `main`
- License: MIT
- Static markers: multi-document fictional settings, voice bibles, story
  bibles, project instructions, tracked items, opening scenarios, theory of
  mind, anti-patterns, document jobs, concept-to-architecture mapping, review,
  runtime operations, maintenance, session start/resume protocols, and
  environment-specific file paths.
- Absorbed pattern: `setting_runtime_document_architecture_gate`
- Local use: use a session start packet to declare which setting documents were
  loaded, stale, or forbidden before resumed continuation.
- Excluded: upstream prompt body, campaign facts, environment paths, project
  instructions, document-job wording, and runtime procedures as instructions.

### wangjiaquangithub/InkFoundry

- URL: https://github.com/wangjiaquangithub/InkFoundry
- HEAD: `12b3a78cb5e5bdc7fe06036a1c9a94bb78490e03`
- Branch: `main`
- License: no root license observed
- Static markers: Navigator/Writer/Editor/RedTeam agents, StateDB as source of
  truth, StateFilter blocking contradictory RAG, SQLite locks, versioning,
  snapshots, circuit breaker, graceful degradation, watchdog timeout, ChromaDB
  memory, path-traversal-protected import/export, token tracker, daemon
  scheduler, genre validator, VoiceSandbox, and SideStoryAgent.
- Absorbed pattern: `inkfoundry_state_db_redteam_voice_sandbox_gate`
- Local use: make accepted canon state outrank vector recall; route conflicts
  through RedTeam and VoiceSandbox review before chapter acceptance.
- Excluded: unlicensed code, backend/frontend runtime, ChromaDB, provider calls,
  daemon scheduling, imports/exports, generated manuscripts, and VoiceSandbox
  prompt bodies.

## MuMuAINovel integration

- Add six default GitHub seeds and three focused discovery queries.
- Add six static pattern gates for:
  - book-MCP beta-reader file envelopes
  - filetype-scoped novel-project RAG
  - direct Scrivener project edit boundaries
  - vector-story frame coordinates
  - setting-runtime document architecture
  - StateDB / RedTeam / VoiceSandbox canon gates
- Pattern packs now emit bible policies, whole-book report targets, inspired
  remap targets, UI-visible hint blocks, and prompt digest entries for all six
  gates.

## Safety decision

All six sources stay `pattern-only` / `runtime-deferred`.

No upstream code, prompt body, manuscript text, book file, Scrivener project,
generated story, vector DB, hosted connector, OAuth session, installer,
postinstall hook, Docker/MCP/browser/desktop runtime, model/provider call,
environment variable, or script output is imported.
