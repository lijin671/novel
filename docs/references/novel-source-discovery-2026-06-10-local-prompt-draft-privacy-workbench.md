# Novel Source Discovery - Local Prompt Draft Privacy Workbench

Observed at: 2026-06-10T23:58:00+08:00

Boundary:

```text
public_github_lsremote_raw_readme_license_marker_scan_no_login_no_clone_no_runtime
```

This pass statically reviewed public GitHub metadata, `git ls-remote` HEADs,
raw README/LICENSE markers, and root-file/package markers for novel-writing
workbenches around prompt preset governance, manuscript import migration,
style-DNA reference libraries, draft/review/confirmed promotion, and
privacy-preserving local indexing.

No repository was cloned, installed, built, executed, or launched. No package
manager, Docker stack, desktop app, updater, local model connector, provider
call, browser automation, MCP server, binary, shell script, PowerShell script,
`.bat`, or `.cmd` file was run.

## Source Snapshot

- `Deng-m1/MaliangAINovalWriter`
  - HEAD: `f500d0114393805c345d36c20e4331d0bb4290cc`
  - License marker: Apache-2.0
  - Static markers: hierarchical novel management, `txt` import, generated
    chapter outlines, prompt/template presets, private user API keys, public
    model pool, model validation, LLM observability, token/cost traces,
    knowledge-extraction review, Docker/deploy surface.
  - Posture: `pattern-only / runtime-deferred`

- `ponysb/91Writing`
  - HEAD: `df3de0362e8e4028b76dffa78c5bba7b8bbd20a1`
  - License marker: MIT
  - Static markers: user-configured APIs, local data posture, custom
    continuation direction, prompt template categories, variable system,
    template import, usage statistics, token-cost management, selective
    import/export, Docker/package scripts.
  - Posture: `pattern-only / runtime-deferred`

- `hezhengtao/MortalAINovel-AIWritingSystem-ai-`
  - HEAD: `51654488870e16ed67715e151763dc36c23e88f5`
  - License marker: no root license observed in this pass.
  - Static markers: local workspace, book/volume/chapter/section management,
    continuation, polishing, style imitation, character cards, relationship
    graph generation, inspiration brainstorming, book-decomposition knowledge
    base, writing-DNA analysis, desktop packaging/runtime markers.
  - Posture: `pattern-only / license-review-needed / runtime-deferred`

- `linnnn89/novel-agent-workbench`
  - HEAD: `9e2e113bd5d6d7b5a44242af52e13ec69291ed63`
  - License marker: AGPL-3.0
  - Static markers: local-first project storage, Memory Bank, world/character
    settings, draft generation, AI review, revision requests, rewrite
    candidates, candidate comparison, confirmed-chapter promotion, provider
    gates, mock provider, audit metadata, Windows `.bat`/`.cmd` scripts.
  - Posture: `pattern-only / no-code-import / runtime-deferred`

- `qnbs/StoryCraft-Studio`
  - HEAD: `1a0cfb21e09e7e0fcb7c844279d1f5920ce55c22`
  - License marker: MIT from raw `LICENSE`.
  - Static markers: IndexedDB local storage, PWA/desktop modes, story planning,
    character/world building, revision snapshots, template remixing,
    privacy-first local AI stack, encrypted API keys, metadata-only
    cross-project search, Tauri/PWA/Node runtime surfaces.
  - Posture: `pattern-only / runtime-deferred`

## Absorbed Patterns

- `prompt_preset_variable_library_gate`
  - Prompt presets need task, mode, required variables, context sources, model
    parameters, and visible defaults.
  - Variable substitution must resolve before prompt send/save.
  - Usage and outcome notes should attach to preset version.

- `imported_manuscript_migration_outline_gate`
  - Imported manuscripts are migration inputs, not unbounded context.
  - Record checksum, parser result, chapter map, generated outlines, and
    accepted-canon status before continuation.
  - Selective import/export must separate prompt libraries, API settings,
    manuscript text, and derived outlines.

- `style_dna_reference_library_gate`
  - Style-DNA libraries store abstract craft features, not source paragraphs.
  - Each reference item needs provenance, posture, allowed-use label,
    abstraction summary, and copy-risk review.
  - Same-type creation cites style-DNA ids and novelty requirements instead of
    requesting exact author imitation.

- `draft_candidate_promotion_gate`
  - AI output starts as a draft candidate.
  - AI review, rewrite candidates, manual edits, rejected drafts, and confirmed
    chapter text stay separate.
  - Only explicit acceptance can update confirmed chapter lineage and memory.

- `privacy_preserving_local_index_gate`
  - Local search indexes default to metadata-only fields.
  - Offline-first storage still needs encryption, export, deletion, backup, and
    provider-call boundaries.
  - Metadata hits cannot silently pull manuscript plaintext into prompts.

## Runtime Exclusions

- no clone, install, build, package manager, Docker, PWA, Tauri, desktop app,
  Streamlit, Flutter, Spring Boot, Vue/Vite, Python runtime, script, `.bat`,
  `.cmd`, or provider/model call
- no API key, token, cookie, local manuscript, private workspace, browser
  storage, or account state read
- no upstream code, prompt pack, templates, screenshots, or README prose copied
  into runtime context

## Local Fusion Targets

- discovery defaults: add the five repositories and four focused GitHub search
  queries
- pattern extraction: map static markers to the five new gates above
- pattern pack: expose prompt/import/style-DNA/draft-promotion/privacy hints
- same-type creation: keep style-DNA abstract and require copy-risk rejection
- continuation: draft from parsed chapter maps and promote only accepted
  candidates
