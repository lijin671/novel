# Static intake: showrunner, local memory, MCP eval contracts - 2026-06-13

## Boundary

This intake used public GitHub metadata, `git ls-remote`, and small public marker
files captured under `tmp/source-intake-2026-06-13-*`.

No upstream repository was installed, built, executed, imported, or used as a
runtime dependency. Prompt bodies, generated fiction, sample project prose,
local workspace data, provider configs, MCP servers, desktop apps, and exports
remain excluded.

## Sources

### sumo91/Novel_Writer

- URL: https://github.com/sumo91/Novel_Writer
- HEAD: `882f455ff6d1a8c51739994565f66ab2809d68c3`
- License: no license observed in public metadata/static probe.
- Static markers reviewed: README, AGENTS, showrunner skill, file tree names.
- Posture: pattern-only.
- Absorbed gate: `file_based_showrunner_canon_approval_gate`.

Reusable pattern:

- Treat the showrunner as the routing and authority layer.
- Keep engine/knowledge files separate from book-local canon, outlines,
  chapters, reviews, state, and exports.
- Require approved concept, outline/brief, review packet, and canon promotion
  before generated prose becomes accepted state.
- Encode chapter briefs as obligation chains from parent book/volume/arc/unit
  context rather than free-form one-shot prompts.

Blocked surface:

- `pip install`, engine CLI runtime, validators, generated sample book content,
  skill prompt bodies, local book projects, and exports.

### TaylorMia0617/Nova

- URL: https://github.com/TaylorMia0617/Nova
- HEAD: `5c7ed6b32621a3af73fe51574712fe755b54e382`
- License: MulanPSL-2.0.
- Static markers reviewed: README, license, version-history and memory service
  file names/snippets.
- Posture: pattern-only.
- Absorbed gate: `nova_local_version_memory_role_gate`.

Reusable pattern:

- Treat a novel as a local workspace with reference database, blueprint plan,
  memory slots, and version history.
- Separate memory into author voice, obsessions, important facts, snapshots,
  and cache-like short-term notes.
- Separate architect/planner, writer, and editor responsibilities.
- Preserve accepted changes as versioned snapshots rather than overwrite-only
  edits.

Blocked surface:

- Electron app runtime, provider calls, BYOK endpoint settings, local user files,
  desktop storage, package install/build, and version snapshots from upstream.

### luo-cccc/ForClaw

- URL: https://github.com/luo-cccc/ForClaw
- HEAD: `aefaca68d6d57a4e1ffa0f9d208c87e9dc86a033`
- License: source-available/no redistribution license observed.
- Static markers reviewed: README, license, eval fixture README, tree names.
- Posture: reference-only / pattern-only.
- Absorbed gate: `forge_agent_mcp_eval_contract_gate`.

Reusable pattern:

- Model chapter work as typed proposals and operations over canon, promises,
  chapter missions, decisions, and reader-compensation ledgers.
- Gate writing through context assembly, provider-budget checks, drafting,
  quality evaluation, targeted revision, repair/compression, and regression-like
  writing eval categories.
- Preserve structured error classes and non-runtime eval contracts as design
  references, not as live MCP behavior.

Blocked surface:

- MCP server launch, stdio tools, provider calls, credential pools, Rust builds,
  eval execution, generated fixture text, traces, and plugin marketplace install.

### Deferred / insufficient evidence

- `polarstarg/webnovel-writer`
  - HEAD: `aae924dc96ee81ece64c0dc2ed5681a75151097b`
  - README contained only a title at probe time, despite useful repository
    description. Deferred until there is enough public source evidence.
- `T3-Venture-Labs-Limited/ghostwriter`
  - HEAD: `93d14b4721ea3dc7dc624ac3dfaae633372cced4`
  - Public marker fetch hit API rate-limit during probe. Deferred; no pattern
    promoted.

## Project changes

- Added seed URLs and GitHub queries for showrunner approval chains, Nova-style
  local memory/version roles, and Forge-style MCP eval contracts.
- Added pattern-pack hint fields so拆书、续写、同类型仿写 can use these patterns
  without importing upstream runtime or text.
- Added front-end labels so the source discovery panel exposes the new gates.

## Verification commands

```powershell
python -m py_compile backend/app/services/source_discovery_service.py backend/app/services/source_pattern_pack_prompt.py backend/tests/services/test_source_discovery_service.py backend/tests/frontend/test_source_discovery_panel_copy.py
python -m pytest backend/tests/services/test_source_discovery_service.py::test_static_showrunner_local_memory_mcp_eval_sources_are_absorbed -q
python -m pytest backend/tests/frontend/test_source_discovery_panel_copy.py -q
npm --prefix frontend run build
git diff --check
```
