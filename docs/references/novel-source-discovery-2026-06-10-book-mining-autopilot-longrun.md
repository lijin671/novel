# Novel Source Discovery - 2026-06-10 Book Mining / Autopilot / Longrun

## Scope

Static source-intake pass for MuMuAINovel book-deconstruction, continuation, and same-type writing workflows.

No external repository was cloned, installed, executed, or imported. Review used public GitHub metadata, `git ls-remote` HEAD checks, raw README/LICENSE snippets, and GitHub tree metadata only.

## Promoted sources

### `cchheerrss/ai-novel-trilogy`

- URL: https://github.com/cchheerrss/ai-novel-trilogy
- Observed HEAD: `c5e533b36a0bf913e03a51e536322a51d0d52a02`
- License: MIT
- Family: novel automation / book-mining / genesis / continuation pipeline
- Posture: pattern-only
- Static evidence:
  - README describes a three-system lifecycle: book mining, novel genesis, then novel automation.
  - Public tree exposes `book-mining/`, `novel-genesis/`, `novel-automation/`, pattern libraries, canon-seed handoff, and automation gate files.
- Absorbed pattern:
  - `book_mining_genesis_automation_gate`
- Local adaptation:
  - Split source-book deconstruction from new-book canon.
  - Keep pattern library, concept scoring, canon seed, and automation gate decisions as separate artifacts.
  - Source mining notes stay reference-only; only accepted canon seed fields can drive chapter automation.

### `zhitongblog/novel-studio`

- URL: https://github.com/zhitongblog/novel-studio
- Observed HEAD: `df15dde3d618c2704de530e0d2654046c3ce716f`
- License: MIT
- Family: multi-book webnovel studio / autopilot orchestration
- Posture: pattern-only / runtime-deferred
- Static evidence:
  - README describes multi-book longform writing, per-book Unterm profile isolation, Codex/Claude/Gemini CLI orchestration, autopilot continuation, stop limits, and periodic full-book logic checks.
  - Public tree contains desktop/Tauri, CLI, MCP, model, and autopilot surfaces.
- Absorbed pattern:
  - `multi_book_autopilot_studio_gate`
- Local adaptation:
  - Add per-book profile boundary and context namespace checks.
  - Autopilot must have visible continue limits, stop phrases, manual stop, and periodic full-book logic review.
  - MCP, Tauri, npm, local auth-token, and CLI runtime surfaces remain excluded from intake.

### `DinhLucent/webnovel-longrun-aigen-docs`

- URL: https://github.com/DinhLucent/webnovel-longrun-aigen-docs
- Observed HEAD: `e98081c825ecd8762a0254f4d5bf4692e53fefcf`
- License: GPL-3.0
- Family: long-running webnovel memory / commit projection docs
- Posture: pattern-only
- Static evidence:
  - README describes `.story-system` as source of truth, accepted chapter commits, event/entity extraction, `.webnovel` read-model projections, RAG/query router, memory scratchpad, and read-only dashboard.
  - Public tree is docs-only except license and architecture asset.
- Absorbed pattern:
  - `longrun_commit_projection_health_gate`
- Local adaptation:
  - Accepted chapter commit is the boundary for prose, events, entities, summaries, and memory updates.
  - Source-of-truth files and read-model projections must be separated with freshness checks.
  - Dashboard/read-model surfaces are observational, not canon write surfaces.

## Deferred / duplicate sources

- `Saemer2023/webnovel-writer-opencode`: overlaps with existing `lujih/webnovel-writer-opencode`; useful as sibling evidence only. GPL/runtime installer surface keeps it pattern-only and not newly promoted.
- `SageAutoman/novel-control-station-openclaw-skill`: overlaps existing `jingtai123/Novel-Control-Station-Skill`; OpenClaw adaptation confirms one-chapter-at-a-time/writeback boundaries but does not require a new gate.
- `njacknot/novelist-skill`: useful skill-pack signal for chapter-control/professional mode, but install scripts and overlap with existing Chinese novelist skills keep it deferred for a later focused skill-pack pass.

## New workflow gates

### `book_mining_genesis_automation_gate`

Use when the system has source-book deconstruction or same-type writing inputs.

Rules:

- Mine source books into abstract pattern entries only.
- Run concept/genesis scoring before automation.
- Emit canon seed as the only handoff into chapter production.
- Keep source patterns, market notes, canon seed, and automation state in separate namespaces.

### `multi_book_autopilot_studio_gate`

Use when a writing session can run multiple books or unattended batches.

Rules:

- Bind every run to one book profile and context namespace.
- Require continue count, completion phrases, manual stop, and question-answer policy before autopilot.
- Insert periodic full-book logic checks before further unattended continuation.

### `longrun_commit_projection_health_gate`

Use when long-running continuation depends on derived state, summary, RAG, or dashboard projections.

Rules:

- Accepted chapter commit is the state mutation boundary.
- Derived projections must trace to the latest accepted commit.
- Stale projections or mixed source/new canon memory block next-chapter generation.

## Artifacts updated

- `backend/app/services/source_discovery_service.py`
- `backend/app/services/source_pattern_pack_prompt.py`
- `frontend/src/types/sourceDiscovery.ts`
- `frontend/src/components/book-remix/BookRemixSourceDiscoveryPanel.tsx`
- `backend/tests/services/test_source_discovery_service.py`
- `backend/tests/frontend/test_source_discovery_panel_copy.py`
- `backend/app/references/novel-source-pattern-pack-2026-06-10.json`

## Runtime exclusions

- No clone.
- No package manager.
- No scripts or installers.
- No Tauri, MCP, CLI, browser, provider, local model, or dashboard runtime.
- No source prose, pattern library body, or prompt file copied into runtime.
