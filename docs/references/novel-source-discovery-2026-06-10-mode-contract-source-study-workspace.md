# Novel Source Discovery - Mode Contracts / Source Study / Workspace Gates - 2026-06-10

## Scope

Static source-intake pass for public GitHub repositories that can improve
MuMuAINovel's deconstruction-to-continuation workflow and same-type creation
controls.

Boundary: public GitHub search results, `git ls-remote` HEAD, raw README and
raw license probes only. No clone, no install, no package manager, no APK/EXE/ZIP
or Docker download, no provider call, no API key, no browser/app/runtime launch,
no MCP/plugin/device control, and no private data.

## Reviewed sources

- `FURUYAN1234/story-maker`
  - HEAD: `c6a2a8e843cb81e9c0069df4601d837634b5bd92`
  - License: no raw `LICENSE`, `LICENSE.md`, or `LICENSE.txt` observed
  - Posture: pattern-only / runtime-deferred
  - Reusable value: visible creative axes, selected-mode-first contracts,
    output-mode shapes, under-length rewrite handling, style analysis, and
    explicit provider-key/legal-safety caveats.

- `yuanbw2025/storyforge`
  - HEAD: `c3a5e69b9d02d5b90e12eac0ddd5f9e4fa1e7d9d`
  - License: README badge says MIT; raw license file was not observed
  - Posture: pattern-only / runtime-deferred
  - Reusable value: visible/editable/savable prompt templates, prompt workflows,
    privacy-first IndexedDB workspace, chunked import, three-layer memory,
    consistency review, and master-study tables isolated from creative data.

- `dedyrio/novelwriter`
  - HEAD: `7c5be5041c1531dd7511b1e9d2ab2d5f9371dd2d`
  - License: AGPL-3.0
  - Posture: pattern-only / runtime-deferred
  - Reusable value: import existing stories, extract characters and
    relationships, maintain a world model, apply story rules, and preserve
    style-consistent continuation.

- `qq1375828505/AI-Fic-IDE`
  - HEAD: `86db145dc6c2a4038a54e45c02d483ee5c7abd0d`
  - License: raw license is an Operit AI project license based on LGPL-3.0
  - Posture: pattern-only / runtime-deferred
  - Reusable value: Android-native web-novel IDE vocabulary for character cards,
    setting cards, foreshadowing states, AI memory, cross-chapter search/replace,
    autosave, history snapshots, local models, and mobile/offline workspaces.

## Absorbed patterns

- `mode_contract_generation_gate`
  - Treat output mode as a first-class contract, not a decorative label.
  - Record mode, genre, audience, POV/narrator, ending style, source-material
    role, axis tags, and under-length rewrite reason with each draft.
  - Rewrite weak drafts from the same accepted inputs instead of injecting
    source-specific people, places, or plot facts.

- `source_study_method_bank_isolation_gate`
  - Keep source-study outputs separate from creative canon.
  - Promote only abstract methods: beat function, pacing device, reveal
    technique, reader promise, style metric range, or craft rule.
  - Same-type creation prompts may cite method-bank ids, but should not load raw
    source chunks, original beats, or source-specific style notes as context.

- Existing gates extended
  - `prompt_library` now recognizes transparent prompt templates and workflow
    JSON surfaces.
  - `world_state_tracking` now recognizes story world models and story rules.
  - `memory_snapshot_versioning` and `relationship_graph_global_replace_gate`
    absorb mobile/offline IDE snapshot and cross-chapter edit lessons.

## Runtime exclusions

- `Story Maker`: Vite app, GitHub Pages deployment, provider calls, API keys,
  screenshots, and browser runtime are excluded.
- `StoryForge`: npm app, provider calls, private prompts, IndexedDB/user data,
  and repository startup instructions are excluded.
- `novelwriter`: Windows installer links, Docker instructions, ZIP/EXE artifacts,
  provider keys, app runtime, and downloaded binaries are excluded.
- `AI-Fic-IDE`: APK releases, Android runtime, ADB/root/accessibility control,
  MCP plugin market, local model runtime, provider keys, and native binaries are
  excluded.

## Local implementation

- Added the four reviewed repositories to backend default GitHub seeds.
- Added targeted GitHub queries for mode contracts, master-study method banks,
  world-model story rules, and AI-Fic-IDE/mobile snapshot signals.
- Added static summaries and pattern keywords for mode-contract generation and
  source-study method-bank isolation.
- Added pattern-pack hints, bible targets, whole-book analysis targets, inspired
  remap targets, transformation guidance, and copy-risk checks.
- Added regression coverage proving that these sources map into the new gates and
  expose digest guidance.
