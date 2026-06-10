# Novel Source Discovery Intake - Living Codex Editorial Workbench

Date: 2026-06-11

## Source

- Repository: `Meryouc/inkwell`
- URL: https://github.com/Meryouc/inkwell
- Reachable HEAD: `fc0829dfcfccbc8a2738ade899027a4af2033bea`
- License signal: MIT via `LICENSE-INKWELL.md`; VS Code-derived notices remain upstream-owned.
- Intake posture: `pattern-only`

## Static evidence

Inkwell frames itself as a VS Code-derived local fiction workbench. Public README markers reviewed from the scratch copy and `git ls-remote` evidence show:

- local-first Markdown project files
- manuscript tree organized as acts, chapters, and scenes
- living codex entries for characters, places, items, lore, and factions
- continuity checks over attributes, timeline math, geography, promise/payoff, and relationship evolution
- Plan / Write / Edit modes
- editorial passes for developmental, line, and copy review
- diagnostics for pacing, emotional tempo, POV balance, beat alignment, sentence length, and dialogue ratio
- invocation-only AI suggestions and BYOK provider surface

## Reusable pattern

`living_codex_editorial_workbench_gate`

The useful pattern is not the VS Code/Electron application. The useful pattern is the contract between manuscript structure, codex state, continuity diagnostics, and editorial pass evidence.

For this project, the pattern becomes:

1. Before drafting, select the target manuscript node.
2. Link that node to current codex entries.
3. Read continuity findings before prose generation.
4. Pick an editorial pass type explicitly.
5. Persist diagnostics and author acceptance separately from source-analysis notes.
6. Reject same-type drafts that preserve a source manuscript tree, codex backlink shape, or diagnostic rhythm.

## Productization in MuMuAINovel

Updated source discovery so the backend can surface:

- `living_codex_scene_link_policy`
- `editorial_pass_diagnostic_policy`
- `manuscript_tree_scene_map`
- `codex_scene_reference_report`
- `editorial_pass_diagnostics`
- `continuity_engine_findings`
- `living_codex_scene_remap`
- `living_codex_editorial_workbench_gate_hints`

The frontend now pins this gate under local RAG / canon QA / patch replay gates so it is visible instead of falling into the dynamic overflow group.

## Runtime boundary

No upstream code was installed, built, or executed.

Blocked without a separate runtime safety contract:

- npm install / build / watch
- Electron or VS Code shell launch
- batch files and inherited VS Code toolchain
- provider/model calls
- OS keystore or API-key access
- copying upstream prompt or application code

## Deferred candidates

- `ayermac/novelos`: overlaps with existing LangGraph / multi-agent chapter workflow gates. Keep as a later agent-profile-routing refinement.
- `v-saprykin/storygraph`: overlaps with counterfactual/story graph RAG gates. Keep as reinforcement evidence.
- `10Legs/novel-template`: overlaps with existing writers-room and editorial-agent gates. Keep as reference only unless a sharper stop-authority gap appears.
