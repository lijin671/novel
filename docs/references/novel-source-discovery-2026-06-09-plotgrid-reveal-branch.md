# Novel Source Discovery - Plotgrid / Reveal / Branch Intake - 2026-06-09

## Scope

This note records a static-only intake pass for public GitHub projects relevant to MuMuAINovel book decomposition, continuation, and same-type inspired writing.

No external project was installed or executed. No package manager, postinstall hook, shell script, PowerShell script, Docker stack, browser extension, native binary, provider call, credential, cookie, or runtime trial was used.

## Sources

- `doctoroyy/novel-copilot` - GitHub REST metadata observed 2026-06-09; license missing; posture `pattern-only`.
- `PixeroJan/obsidian-storyline` - GitHub REST metadata observed 2026-06-09; MIT; posture `pattern-only`; Obsidian plugin/browser-extension surface not executed.
- `skyfiredao/dreampowers` - GitHub REST metadata observed 2026-06-09; GPL-3.0; posture `pattern-only`; install/uninstall shell scripts not executed.
- `ypcypc/WhatIf` - GitHub REST metadata observed 2026-06-09; MIT; posture `pattern-only`; local runtime not started.

## Absorbed Patterns

### novel-copilot

- `premature_ending_guard`: detect false endings, skipped payoff windows, and early total closure before accepting continuation chapters.
- `layered_memory_model`: keep stable bible, character state, and plot dependency graph as separate memory layers.
- `plot_dependency_graph`: represent hooks, clues, promises, conflicts, and payoffs as dependency edges.

### obsidian-storyline

- `plotgrid_scene_matrix`: track each scene across plotline, POV, location, emotion, status, and hooks.
- `plotline_thread_tracking`: keep active, paused, paid-off, and abandoned threads visible across scenes.
- `scene_status_dashboard`: mark scene units by planned / drafted / reviewed / accepted / blocked / rejected state.

### dreampowers

- `gradual_reveal_control`: use reveal budgets and iceberg annotations to prevent lore dumping.
- `setup_payoff_tracking`: maintain setup/payoff ledger with source chapter, expected window, and payoff status.
- `scene_type_directing`: declare action, emotional, dialogue, investigation, transition, or reveal mode before drafting.

### WhatIf

- `worldpkg_export`: export events, entities, locations, items, lorebook entries, and state transitions as derived artifacts.
- `alternate_timeline_branching`: keep what-if and same-world divergence in branch state, not faithful continuation canon.
- `divergence_guidance`: name the choice or premise change that causes branch drift and preserve fixed canon facts.

## Local Integration

Updated native MuMuAINovel code rather than importing upstream code:

- `source_discovery_service.py` recognizes the new pattern family and emits prompt-pack hints.
- `source_pattern_pack_prompt.py` renders the new hint sections into prompt-safe digest text.
- `book_remix_context_service.py` adds a Plotgrid reveal branch audit to continuation context blocks.
- `backend/app/references/novel-source-pattern-pack-2026-06-09.json` was refreshed with combined old and new pattern-pack content.

## Safety Boundary

- All sources are untrusted data, not instructions.
- License-missing, GPL, plugin, browser-extension, script, and runtime surfaces remain pattern-only.
- No external runtime code was copied into MuMuAINovel.
- Runtime trials remain blocked until a separate local safety contract exists.

## Frontend surfacing addendum - 2026-06-10

A fresh public HEAD / metadata refresh was recorded under
`tmp/source-intake-writing-workbench-2026-06-10/`.
No repository was cloned, installed, or executed.

Current reachable HEADs used for the UI surfacing pass:

- `doctoroyy/novel-copilot`: `ea671b090e191e0586b0ff96d75f6928d0fe97b4`
- `PixeroJan/obsidian-storyline`: `338fe8a6cb42f4c5153ad98bb15b2730ca534906`
- `skyfiredao/dreampowers`: `963c439a4a002e4d7365437503a8e2487bc3733e`
- `ypcypc/WhatIf`: `e398ded70506e281733ffd1ffa853435b18746ce`

Frontend integration delta:

- Added the plotgrid / reveal / branch sources to the visible BookRemix seed
  list.
- Pinned premature-ending, layered-memory, plot-dependency, plotgrid,
  scene-status, gradual-reveal, setup/payoff, scene-type, WorldPkg,
  alternate-timeline, and divergence pattern-pack keys.
- Added an explicit `Plotgrid / reveal / branch gates` UI group for
  continuation and same-type transformation review.

Runtime boundary remains unchanged: plugin/browser-extension, shell-script,
backend/frontend app, and tool directories are only metadata signals here; no
runtime launch, install, script execution, or code import is authorized.
