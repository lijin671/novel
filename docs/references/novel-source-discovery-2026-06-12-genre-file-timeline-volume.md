# Novel Source Discovery - Genre/file/timeline/volume gates

Date: 2026-06-12
Boundary: `public_github_search_lsremote_raw_readme_license_marker_no_login_no_clone_no_runtime`

## Scope

This pass statically reviewed four GitHub repositories found through public
GitHub search results and direct repository metadata checks. The goal was to
extract pattern-only lessons for MuMuAINovel's 拆书续写、同类型仿写、长篇一致性、以及
安全边界能力.

No repository was cloned, installed, executed, or imported. No package manager,
provider call, browser, Obsidian plugin, Flask app, Electron app, Vite server,
CLI, generated novel archive, or ZIP artifact was launched or downloaded.

## Source snapshots

### `SteakWrangler/novelcraft-genre-weaver`

- URL: <https://github.com/SteakWrangler/novelcraft-genre-weaver>
- HEAD: `640176b017bcea17650bdf53fcaedd8dd6c383d4`
- Default branch: `main`
- License: no root license observed through GitHub metadata/raw license check
- Static markers: README, `package.json`, `server/package.json`, sample world
  bible/plot skeleton files
- Posture: `pattern-only`
- Absorbed gate: `genre_inspiration_budget_library_gate`

Reusable pattern:

- Keep genre mix, trope inspiration, format, quality level, target length,
  chapter/illustration count, and cost estimate as separate fields.
- For 同类型仿写, inspiration libraries should become abstract option matrices,
  not copied premise bundles or chapter orders.
- A generated-book library needs lineage and budget metadata so retries and
  polish scope stay visible.

Runtime gates:

- No Vite/Node runtime.
- No package scripts.
- No OpenAI/API paths.
- No sample manuscript import.

### `perivar/OpenTale`

- URL: <https://github.com/perivar/OpenTale>
- HEAD: `83a110c98c2fd78a3feae411042d61751a32e385`
- Default branch: `main`
- License: no root license observed
- Static markers: README, `requirements.txt`, `config.py`, `prompts.py`,
  `web_app.py`, `.env.example`
- Posture: `pattern-only`
- Absorbed gate: `stepwise_local_book_generation_file_gate`

Reusable pattern:

- Model a book-generation run as local artifacts:
  `world.txt`, `characters.txt`, `synopsis.txt`, `outline.txt`,
  `outline.json`, `chapters.json`, chapter folders, and settings.
- Treat world -> characters -> outline -> scenes -> chapters as a guided chain.
- Continuation should cite the previous-chapter context window and accepted
  local files before producing new text.

Runtime gates:

- No Flask app launch.
- No virtualenv or pip install.
- No provider/API call.
- No browser UI.
- No upstream prompt execution.

### `EricRhysTaylor/Radial-Timeline`

- URL: <https://github.com/EricRhysTaylor/Radial-Timeline>
- HEAD: `02b25cf3673ce44a2153a8c49b03c4804770e60a`
- Default branch: `master`
- License: source-available non-commercial license / GitHub SPDX `NOASSERTION`
- Static markers: README, custom license, `package.json`, `manifest.json`,
  `AGENT_RULES.md`, script gates
- Posture: `pattern-only`
- Absorbed gate: `radial_subplot_timeline_xray_gate`

Reusable pattern:

- Visualize scenes by act, subplot, narrative order, and chronological order.
- Use synopsis/story-pulse metadata to inspect rhythm, B-plot dropouts, and
  chronology inversions before continuation.
- Keep visual X-ray ideas separate from code reuse because the license is
  non-commercial/source-available.

Runtime gates:

- No Obsidian plugin install.
- No vault access.
- No Node/Husky/build/release scripts.
- No code or asset reuse.

### `3stythe/ai-novel-generator`

- URL: <https://github.com/3stythe/ai-novel-generator>
- HEAD: `cf66f2bff42d6f33629a8ad0a53b92439df2f3f3`
- Default branch: `master`
- License: MIT
- Static markers: README, `requirements.txt`, `config.py`, `novel_generator.py`,
  generated `novels/` archive references
- Posture: `pattern-only`
- Absorbed gate: `volume_antipattern_dependency_graph_gate`

Reusable pattern:

- Separate volume planning, chapter rhythm, outline validation,
  anti-pattern detection, character-arc enforcement, and event dependency graph.
- Let the editor/reviewer side catch repeated beats, weak escalation, broken
  dependencies, and character-integrity drift before writer execution.
- For Chinese webnovel continuation, volume and dependency gates are more useful
  than one-shot chapter prompts.

Runtime gates:

- No raw ZIP artifacts.
- No CLI execution.
- No pip install.
- No provider/API call.
- No generated novel folder import.
- Security-topic labels keep this source under static review only.

## Deferred / rejected signal

`Riccjamez214/wordplay` was reachable and current, but this pass did not absorb
it into code because the public README promotes raw ZIP download links, the root
contains crawler scripts and platform-specific crawler commands, and
`package.json` has Electron `postinstall` / packaging surfaces. It remains a
manual-review or reject/defer signal unless a future pass finds a bounded,
non-runtime pattern with stronger provenance.

## MuMuAINovel integration

Added durable pattern-pack fields:

- `genre_inspiration_budget_library_gate_hints`
- `stepwise_local_book_generation_file_gate_hints`
- `radial_subplot_timeline_xray_gate_hints`
- `volume_antipattern_dependency_graph_gate_hints`

Added transformation/copy-risk rules for 同类型仿写:

- remap genre/trope/cost matrices instead of copying source bundles
- rebuild local file manifests with new ids and filenames
- inspect both narrative order and chronological order for subplot continuity
- rebuild volume dependency edges and character-arc checkpoints

## Verification targets

- `backend/tests/services/test_source_discovery_service.py`
- `backend/tests/frontend/test_source_discovery_panel_copy.py`
- `frontend` TypeScript build
- `git diff --check`
