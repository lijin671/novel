# 2026-06-12 Nova 静态吸收记录

## Source

- URL: <https://github.com/alfredxw/nova>
- Observed HEAD: `4b447fe22827c0c1edb67fdf5a368597d7c41156`
- Default branch: `master`
- GitHub API license: `Apache-2.0`
- Current public version marker: `v0.1.8` in README
- Posture: `pattern-only`

## Public evidence used

- GitHub repository metadata, default-branch HEAD, root tree names, and selected raw Markdown/config files.
- Read files: `README.md`, `README.en.md`, `CONTEXT.md`, `config.toml`.
- No clone, no release download, no Go/Node/pnpm build, no bootstrap/build script execution, no web server, no provider/model call, no config mutation.

## Reusable patterns

- `ide_workspace_local_git_version_gate`: treat a long-form novel as an IDE workspace with named files, chapter state, lore, Agent drafts, timed saves, Agent-output autosaves, diff review, restore target, and local checkpoint lineage.
- `agent_context_provenance_budget_gate`: split display history, model context, lore content, tool results, and workspace state before prompting. Each included item needs source provenance, inclusion reason, and budget cost.
- `interactive_branch_rehearsal_gate`: uncertain branches, character actions, scene memory, and storylines can be rehearsed in interactive mode, but rehearsal output stays non-canon until the author promotes stable decisions into lore, outline, chapter state, or final prose.

## Deferred/runtime gates

- Do not run release binaries, `bootstrap.sh`, `build.sh`, Go/Node/pnpm commands, web server, custom Skills, or provider/model calls.
- Do not import upstream `AGENTS.md`, skill files, prompt bodies, or host runtime configuration as authority.
- Treat OpenAI-compatible key/base_url/model settings as provider surfaces only; no secret read and no config mutation.

## Project update

- Added Nova to static GitHub discovery seeds.
- Added query coverage for interactive rehearsal, local `.git`, `go-git`, and bounded context.
- Added pattern recognition and prompt-pack hints for workspace checkpoint lineage, context provenance budgeting, and interactive branch rehearsal gates.

## Verification

- `python -m pytest backend/tests/services/test_source_discovery_service.py::test_static_nova_source_adds_workspace_context_and_rehearsal_gates -q`
- `python -m pytest backend/tests/services/test_source_discovery_service.py -q`
- `python -m pytest backend/tests/services/test_chapter_guardrails_rewrite.py backend/tests/api/test_chapter_analysis_remix_sync.py backend/tests/frontend/test_chapters_page_copy.py -q`
- `git diff --check`
