# Novel Source Discovery - 2026-06-11 Book Writing Graph / Rights / Editor Workspace Static Review

## Boundary

`public_github_book_writing_static_head_raw_readme_license_no_login_no_clone_no_runtime_20260611`

This pass used only public GitHub metadata, `git ls-remote --symref`, raw
README/LICENSE reads, and compact marker counts. It did not clone, install,
execute package managers, run extensions, launch apps, call providers, read
browser/editor storage, or inspect secrets.

Static cache:

- `tmp/source-intake-20260611-book-writing-graph-rights-vscode-static-review.json`

## Reviewed sources

### `lhfer/codex-novel-to-comic-studio`

- URL: <https://github.com/lhfer/codex-novel-to-comic-studio>
- HEAD: `7c64ef96b0ccb28a55ae514e185e92cb2364daac`
- Default branch: `main`
- License marker: `MIT License`
- Family: `novel-automation`
- Posture: `pattern-only`
- Reusable pattern:
  - rights gate before adaptation
  - source parsing separated from narrative bible and visual bible
  - QC and PDF/CBZ export as downstream hold states
- Absorbed as: `rights_first_adaptation_pipeline_gate`
- Runtime excluded:
  - no Codex skill install
  - no sample asset import
  - no image/page generation
  - no export runtime

### `yosrikhiari/Versatile`

- URL: <https://github.com/yosrikhiari/Versatile>
- HEAD: `a843c31064c9ab48cefc95b95d60a3f5d4248434`
- Default branch: `master`
- License marker: no raw LICENSE observed
- Family: `novel-automation`
- Posture: `pattern-only`
- Reusable pattern:
  - local IndexedDB writing workspace
  - flow sessions / focus mode / writing goals
  - story bible, timeline, scene cards, and story-network graph
  - local AI Spark / Polish as separate assistance phases
- Absorbed as: `local_flow_story_graph_workspace_gate`
- Runtime excluded:
  - no npm install
  - no browser app launch
  - no Ollama/provider call
  - no local browser storage read

### `okeylanders/prose-minion-vscode`

- URL: <https://github.com/okeylanders/prose-minion-vscode>
- HEAD: `828187df94a7476ed2ba93c63a5114aba8fa4382`
- Default branch: `main`
- License marker: Commons Clause condition
- Family: `novel-automation`
- Posture: `pattern-only`
- Reusable pattern:
  - editor-context prose analysis
  - professional prose metrics
  - manuscript/chapter/source-analysis scope labels
  - story bible analysis kept separate from runtime model/provider choice
- Absorbed as: `editor_context_prose_analysis_gate`
- Runtime excluded:
  - no VS Code extension install
  - no provider/model list adoption
  - no upstream rule body import
  - no editor workspace or file-state read

### `wwessex/Writer1`

- URL: <https://github.com/wwessex/Writer1>
- HEAD: `dbdd8e9af6edb7dabd7805225c5ff321abb1c3be`
- Default branch: `main`
- License marker: no raw LICENSE observed
- Family: `novel-automation`
- Posture: `pattern-only`
- Reusable pattern:
  - offline/online novel PWA workspace
  - chapter-isolated editing
  - IndexedDB autosave
  - version history, diff preview, restore
  - DOCX/PDF/RTF export as a final checkpoint
- Absorbed as: `offline_chapter_revision_export_gate`
- Runtime excluded:
  - no PWA/Tauri runtime
  - no optional sync endpoint
  - no export binary/tool execution
  - no collaboration/account surface

### Deferred candidate: `Anshler/graphify-novel`

- URL: <https://github.com/Anshler/graphify-novel>
- `git ls-remote` result: repository not found
- Decision: `defer`
- Reason: search-result title was not enough; no reachable HEAD or README.

## Project fusion

The static patterns were fused into the existing source-discovery pipeline:

- default GitHub seed URLs
- GitHub query vocabulary
- static repository pattern summaries
- `PATTERN_KEYWORDS`
- `build_pattern_pack_from_ledger`
- pattern-pack prompt rendering
- source-discovery regression test

## New gates

- `rights_first_adaptation_pipeline_gate`
  - forces rights/source-boundary review before拆书续写, adaptation, visual-bible,
    storyboard, export, or publication-package states.
- `local_flow_story_graph_workspace_gate`
  - binds writing sprints, story graph, timeline, scene cards, and story bible
    to stable local workspace IDs.
- `editor_context_prose_analysis_gate`
  - requires editor-context analysis to state chapter/selection/source-note
    scope and redact source chunks before same-type creation.
- `offline_chapter_revision_export_gate`
  - treats each chapter as an isolated autosaved document with revision/export
    checkpoints before it becomes whole-book state.

## Verification

RED:

```powershell
python -m pytest backend/tests/services/test_source_discovery_service.py::test_static_book_writing_graph_rights_vscode_sources_map_to_workspace_gates -q
```

Expected failure was the missing default repository seed.

GREEN:

```powershell
python -m pytest backend/tests/services/test_source_discovery_service.py::test_static_book_writing_graph_rights_vscode_sources_map_to_workspace_gates -q
```

Result: `1 passed`.
