# Novel Source Discovery - 2026-06-11 Style RAG Copy-Safety Pass

## Scope

Static source-intake pass for projects related to book deconstruction,
continuation, and same-type/style imitation workflows.

No upstream project was cloned as a checkout, installed, executed, started, or
connected to model providers. Review used public GitHub metadata, `git
ls-remote`, root tree metadata, README/LICENSE markers, and isolated scratch
files under `tmp/source-intake-20260611-storyforge-stylemuse-moyun/`.

## Sources

### `MissingDanial/StyleMuse`

- URL: <https://github.com/MissingDanial/StyleMuse>
- Observed HEAD: `adfcf96da89917b5dbb5132eba1c811ca1fb2fdf`
- Default branch: `main`
- Stars/forks at review: 2 / 0
- License marker: no GitHub license detected
- Root markers: `README.md`, `Dockerfile`, `docker-compose.yml`, `.env.example`,
  `requirements.txt`, `app.py`, `main.py`, `prompts`, `skills`, `tests`
- Posture: `pattern-only`

Reusable pattern:

- Style imitation should not be treated as direct style prompt copying.
- Source works should first become protected reference chunks with provenance,
  style traits, and retrieval reasons.
- Generation needs an explicit anti-copy loop: chunking, retrieval filtering,
  post-generation repetition/copy detection, and prompt constraints.
- Same-type output can be promoted only after lexical/proper-noun/retrieved-span
  checks prove it did not copy source passages.

Runtime exclusions:

- No package install, Docker run, provider/API call, uploaded corpus processing,
  or `.env` usage.

### `91zgaoge/StoryForge`

- URL: <https://github.com/91zgaoge/StoryForge>
- Observed HEAD: `94f90eb058e8e2281d76eb3d23c06e3a7dbecd8a`
- Default branch: `master`
- Stars/forks at review: 31 / 8
- License marker: GitHub API license empty; README badge says ISC
- Root markers: `Cargo.toml`, `package.json`, `docker-compose.yml`, `deploy.sh`,
  `run-dev.ps1`, `src-tauri`, `src-frontend`, `.env.example`, `AGENTS.md`,
  `CLAUDE.md`
- Posture: `pattern-only`

Reusable pattern:

- Split authoring workspace into backstage planning/state management and
  frontstage immersive drafting.
- Keep director-style workflow state visible: story, character, scene,
  worldbuilding, foreshadowing, StyleDNA, and stage progress.
- Treat host-agent files and desktop/runtime scaffolding as high-trust runtime
  surfaces, not importable project instructions.

Runtime exclusions:

- No Tauri/Rust/npm/Docker/PowerShell/shell execution, no host-agent import, no
  provider call.

### `wuyinglai/moyun-studio`

- URL: <https://github.com/wuyinglai/moyun-studio>
- Observed HEAD: `0d8d55670712575d370bbb6c2b50a8216dbb90eb`
- Default branch: `main`
- Stars/forks at review: 1 / 1
- License: MIT
- Root markers: `README.md`, `LICENSE`, `.env.example`, `backend`, `frontend`,
  `prompts`, `scripts`, `kill_port_8000.ps1`, `tests`
- Posture: `pattern-only`

Reusable pattern:

- Scene-level files can be the smallest generation/edit unit.
- Rewrite/polish should produce candidate drafts first; confirmed text changes
  require author review.
- Story memory files such as recent context and story state should be updated
  from accepted text only.
- YAML prompt pipelines are useful as visible contracts, but remain project
  data rather than hidden global prompts.

Runtime exclusions:

- No script/PowerShell execution, package-manager install, tests, provider call,
  or local workspace import.

## Fusion into MuMuAINovel

Added source-discovery support for:

- `anti_copy_style_rag_gate`
- default GitHub query for style-imitation RAG anti-copy evidence
- default seeds for StyleMuse, StoryForge, and Moyun Studio
- pattern-pack hints, bible targets, inspired remap targets, prompt hints, and
  copy-risk hints
- UI display for anti-copy style RAG gates

Design rule:

> Same-type imitation may use source chunks as protected evidence, not as
> generation material. Prompts should cite chunk ids, style traits, and retrieval
> reasons. Accepted output must pass copied-span and source-neighbor checks.
